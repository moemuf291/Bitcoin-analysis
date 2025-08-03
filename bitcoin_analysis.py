import requests
import json
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt
from rich.text import Text
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

console = Console()

class BitcoinAddressAnalyzer:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.console = Console()
        
    def get_address_info(self, address):
        """Get basic address information"""
        try:
            response = requests.get(f"{self.base_url}/address/{address}")
            if response.status_code == 200:
                return response.json()
            else:
                self.console.print(f"[red]Error: {response.status_code}[/red]")
                return None
        except Exception as e:
            self.console.print(f"[red]Error fetching address info: {e}[/red]")
            return None
    
    def get_address_transactions(self, address, last_seen_txid=None):
        """Get transactions for an address"""
        try:
            url = f"{self.base_url}/address/{address}/txs"
            if last_seen_txid:
                url += f"/{last_seen_txid}"
            
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                self.console.print(f"[red]Error: {response.status_code}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]Error fetching transactions: {e}[/red]")
            return []
    
    def get_transaction_details(self, txid):
        """Get detailed transaction information"""
        try:
            response = requests.get(f"{self.base_url}/tx/{txid}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            self.console.print(f"[red]Error fetching transaction details: {e}[/red]")
            return None
    
    def satoshi_to_btc(self, satoshis):
        """Convert satoshis to BTC"""
        return satoshis / 100000000
    
    def format_datetime(self, timestamp):
        """Format timestamp to readable datetime"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def display_address_stats(self, address_info):
        """Display address statistics"""
        stats_table = Table(title="Address Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        total_received = self.satoshi_to_btc(address_info.get('chain_stats', {}).get('funded_txo_sum', 0))
        total_sent = self.satoshi_to_btc(address_info.get('chain_stats', {}).get('spent_txo_sum', 0))
        current_balance = total_received - total_sent
        
        tx_count = address_info.get('chain_stats', {}).get('tx_count', 0)
        
        stats_table.add_row("Total Received", f"{total_received:.8f} BTC")
        stats_table.add_row("Total Sent", f"{total_sent:.8f} BTC")
        stats_table.add_row("Current Balance", f"{current_balance:.8f} BTC")
        stats_table.add_row("Transaction Count", str(tx_count))
        
        if tx_count > 0:
            avg_tx_size = (total_received + total_sent) / (tx_count * 2)
            stats_table.add_row("Average Transaction Size", f"{avg_tx_size:.8f} BTC")
        
        self.console.print(stats_table)
        return current_balance, total_received, total_sent, tx_count
    
    def display_recent_transactions(self, transactions, address, limit=10):
        """Display recent transactions"""
        tx_table = Table(title=f"Recent Transactions (Last {min(limit, len(transactions))})")
        tx_table.add_column("Time", style="cyan")
        tx_table.add_column("TXID", style="yellow", max_width=20)
        tx_table.add_column("Type", style="magenta")
        tx_table.add_column("Amount (BTC)", style="green")
        tx_table.add_column("Fee (BTC)", style="red")
        
        for i, tx in enumerate(transactions[:limit]):
            if 'status' in tx and tx['status'].get('confirmed'):
                timestamp = tx['status']['block_time']
                time_str = self.format_datetime(timestamp)
            else:
                time_str = "Unconfirmed"
            
            txid = tx['txid'][:16] + "..."
            
            # Calculate amount for this address
            amount_in = 0
            amount_out = 0
            
            # Check inputs
            for vin in tx.get('vin', []):
                if vin.get('prevout', {}).get('scriptpubkey_address') == address:
                    amount_out += vin['prevout']['value']
            
            # Check outputs
            for vout in tx.get('vout', []):
                if vout.get('scriptpubkey_address') == address:
                    amount_in += vout['value']
            
            net_amount = amount_in - amount_out
            tx_type = "Received" if net_amount > 0 else "Sent"
            
            fee = self.satoshi_to_btc(tx.get('fee', 0))
            
            tx_table.add_row(
                time_str,
                txid,
                tx_type,
                f"{self.satoshi_to_btc(abs(net_amount)):.8f}",
                f"{fee:.8f}"
            )
        
        self.console.print(tx_table)
    
    def analyze_address_clustering(self, address, transactions):
        """Analyze address clustering and related addresses"""
        related_addresses = set()
        address_connections = {}
        
        for tx in transactions:
            tx_addresses = set()
            
            # Collect all addresses in inputs
            for vin in tx.get('vin', []):
                if 'prevout' in vin and 'scriptpubkey_address' in vin['prevout']:
                    addr = vin['prevout']['scriptpubkey_address']
                    tx_addresses.add(addr)
            
            # Collect all addresses in outputs
            for vout in tx.get('vout', []):
                if 'scriptpubkey_address' in vout:
                    addr = vout['scriptpubkey_address']
                    tx_addresses.add(addr)
            
            # If our target address is in this transaction, record connections
            if address in tx_addresses:
                for addr in tx_addresses:
                    if addr != address:
                        related_addresses.add(addr)
                        if addr not in address_connections:
                            address_connections[addr] = 0
                        address_connections[addr] += 1
        
        # Display clustering results
        cluster_table = Table(title="Address Clustering Analysis")
        cluster_table.add_column("Related Address", style="cyan", max_width=35)
        cluster_table.add_column("Connection Count", style="green")
        cluster_table.add_column("Likelihood", style="yellow")
        
        sorted_connections = sorted(address_connections.items(), key=lambda x: x[1], reverse=True)
        
        for addr, count in sorted_connections[:10]:  # Show top 10
            likelihood = "High" if count > 5 else "Medium" if count > 2 else "Low"
            cluster_table.add_row(addr[:35] + "...", str(count), likelihood)
        
        self.console.print(cluster_table)
        return related_addresses, address_connections
    
    def create_network_graph(self, address, related_addresses, address_connections, transactions):
        """Create an interactive network graph"""
        try:
            self.console.print("[yellow]Creating network graph...[/yellow]")
            G = nx.Graph()
            
            # Add main address as central node
            G.add_node(address, node_type='main', balance=0, tx_count=len(transactions))
            self.console.print(f"[cyan]Added main node: {address[:16]}...[/cyan]")
            
            # Add related addresses
            related_list = list(related_addresses)[:20]  # Limit to top 20 for readability
            self.console.print(f"[cyan]Adding {len(related_list)} related addresses...[/cyan]")
            
            for related_addr in related_list:
                connection_count = address_connections.get(related_addr, 1)
                G.add_node(related_addr, node_type='related', connection_count=connection_count)
                G.add_edge(address, related_addr, weight=connection_count)
            
            self.console.print("[cyan]Creating network layout...[/cyan]")
            # Create plotly visualization
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Prepare edge traces
            edge_x = []
            edge_y = []
            edge_weights = []
            
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_weights.append(G[edge[0]][edge[1]]['weight'])
            
            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Prepare node traces
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            node_size = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                if G.nodes[node]['node_type'] == 'main':
                    node_text.append(f"Main Address<br>{node[:16]}...")
                    node_color.append('red')
                    node_size.append(30)
                else:
                    connections = G.nodes[node].get('connection_count', 1)
                    node_text.append(f"Related Address<br>{node[:16]}...<br>Connections: {connections}")
                    node_color.append('lightblue')
                    node_size.append(10 + connections * 2)
            
            # Create node trace
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                hovertext=node_text,
                marker=dict(
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color='white')
                )
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title=f'Bitcoin Address Network Graph for {address[:16]}...',
                              titlefont_size=16,
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              annotations=[ dict(
                                  text="Network visualization of related Bitcoin addresses",
                                  showarrow=False,
                                  xref="paper", yref="paper",
                                  x=0.005, y=-0.002,
                                  xanchor="left", yanchor="bottom",
                                  font=dict(color="#888", size=12)
                              )],
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                          )
            
            # Save as HTML file
            try:
                import os
                current_dir = os.getcwd()
                file_path = os.path.join(current_dir, "bitcoin_network_graph.html")
                self.console.print(f"[cyan]Attempting to save file to: {file_path}[/cyan]")
                
                fig.write_html(file_path)
                
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    self.console.print(f"[green]Network graph saved successfully! File size: {file_size} bytes[/green]")
                    self.console.print(f"[green]Location: {file_path}[/green]")
                else:
                    self.console.print("[red]File was not created despite no error[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]Error saving network graph: {type(e).__name__}: {str(e)}[/red]")
                import traceback
                self.console.print(f"[red]Full traceback: {traceback.format_exc()}[/red]")
            
        except Exception as e:
            self.console.print(f"[red]Error creating network graph: {type(e).__name__}: {str(e)}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback: {traceback.format_exc()}[/red]")
    
    def create_transaction_timeline(self, transactions, address):
        """Create a timeline visualization of transactions"""
        try:
            self.console.print("[yellow]Creating transaction timeline...[/yellow]")
            if not transactions:
                self.console.print("[yellow]No transactions to create timeline[/yellow]")
                return
            
            self.console.print(f"[cyan]Processing {len(transactions)} transactions...[/cyan]")
            dates = []
            amounts = []
            tx_types = []
            
            for tx in transactions:
                if 'status' in tx and tx['status'].get('confirmed'):
                    timestamp = tx['status']['block_time']
                    date = datetime.fromtimestamp(timestamp)
                    
                    # Calculate amount for this address
                    amount_in = 0
                    amount_out = 0
                    
                    for vin in tx.get('vin', []):
                        if vin.get('prevout', {}).get('scriptpubkey_address') == address:
                            amount_out += vin['prevout']['value']
                    
                    for vout in tx.get('vout', []):
                        if vout.get('scriptpubkey_address') == address:
                            amount_in += vout['value']
                    
                    net_amount = self.satoshi_to_btc(amount_in - amount_out)
                    
                    dates.append(date)
                    amounts.append(abs(net_amount))
                    tx_types.append('Received' if net_amount > 0 else 'Sent')
            
            if dates:
                df = pd.DataFrame({
                    'Date': dates,
                    'Amount': amounts,
                    'Type': tx_types
                })
                
                fig = px.scatter(df, x='Date', y='Amount', color='Type',
                               title=f'Transaction Timeline for {address[:16]}...',
                               labels={'Amount': 'Amount (BTC)', 'Date': 'Date'})
                
                try:
                    import os
                    current_dir = os.getcwd()
                    file_path = os.path.join(current_dir, "bitcoin_timeline.html")
                    self.console.print(f"[cyan]Attempting to save timeline to: {file_path}[/cyan]")
                    
                    fig.write_html(file_path)
                    
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        self.console.print(f"[green]Timeline saved successfully! File size: {file_size} bytes[/green]")
                        self.console.print(f"[green]Location: {file_path}[/green]")
                    else:
                        self.console.print("[red]Timeline file was not created despite no error[/red]")
                        
                except Exception as e:
                    self.console.print(f"[red]Error saving timeline: {type(e).__name__}: {str(e)}[/red]")
                    import traceback
                    self.console.print(f"[red]Full traceback: {traceback.format_exc()}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error creating timeline: {type(e).__name__}: {str(e)}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback: {traceback.format_exc()}[/red]")
    
    def analyze_address(self, address):
        """Main function to analyze a Bitcoin address"""
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing address...", total=5)
            
            # Step 1: Get basic address info
            progress.update(task, advance=1, description="[cyan]Fetching address info...")
            address_info = self.get_address_info(address)
            if not address_info:
                return
            
            # Step 2: Get transactions
            progress.update(task, advance=1, description="[cyan]Fetching transactions...")
            transactions = self.get_address_transactions(address)
            
            # Step 3: Display statistics
            progress.update(task, advance=1, description="[cyan]Calculating statistics...")
            self.console.print(Panel.fit(f"[bold]Bitcoin Address Analysis: {address}[/bold]"))
            balance, total_received, total_sent, tx_count = self.display_address_stats(address_info)
            
            # Step 4: Display recent transactions
            progress.update(task, advance=1, description="[cyan]Processing transactions...")
            if transactions:
                self.display_recent_transactions(transactions, address)
                
                # Address clustering analysis
                self.console.print("\n")
                related_addresses, address_connections = self.analyze_address_clustering(address, transactions)
                
                # Create visualizations
                self.console.print("\n[yellow]Creating visualizations...[/yellow]")
                self.create_network_graph(address, related_addresses, address_connections, transactions)
                self.create_transaction_timeline(transactions, address)
            
            progress.update(task, advance=1, description="[green]Analysis complete!")

def test_libraries():
    """Test that all required libraries are working"""
    console.print("[yellow]Testing libraries...[/yellow]")
    try:
        import plotly.graph_objects as go
        import pandas as pd
        import networkx as nx
        
        # Test plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
        test_html = fig.to_html()
        console.print("[green]✓ Plotly working[/green]")
        
        # Test pandas
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        console.print("[green]✓ Pandas working[/green]")
        
        # Test networkx
        G = nx.Graph()
        G.add_edge(1, 2)
        console.print("[green]✓ NetworkX working[/green]")
        
        console.print("[green]All libraries are working correctly![/green]")
        return True
    except Exception as e:
        console.print(f"[red]Library test failed: {e}[/red]")
        return False

def main():
    # Test libraries first
    if not test_libraries():
        console.print("[red]Please check your library installations[/red]")
        return
    
    analyzer = BitcoinAddressAnalyzer()
    
    console.print(Panel.fit(
        "[bold blue]Bitcoin Address Analyzer[/bold blue]\n"
        "[cyan]Analyze Bitcoin addresses for transaction history, stats, and network relationships[/cyan]"
    ))
    
    while True:
        console.print("\n" + "="*50)
        address = Prompt.ask("[yellow]Enter Bitcoin address to analyze (or 'quit' to exit)[/yellow]")
        
        if address.lower() == 'quit':
            console.print("[green]Goodbye![/green]")
            break
        
        if len(address) < 25 or len(address) > 62:
            console.print("[red]Invalid Bitcoin address format[/red]")
            continue
        
        analyzer.analyze_address(address)
        
        console.print("\n[green]Analysis complete! Check the generated HTML files for visualizations.[/green]")

if __name__ == "__main__":
    main()
