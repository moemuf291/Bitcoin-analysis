#!/usr/bin/env python3
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

console = Console()

class BitcoinAddressAnalyzer:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.console = Console()
        self.analysis_data = {}
        
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
    
    def calculate_address_stats(self, address_info):
        """Calculate and return address statistics"""
        total_received = self.satoshi_to_btc(address_info.get('chain_stats', {}).get('funded_txo_sum', 0))
        total_sent = self.satoshi_to_btc(address_info.get('chain_stats', {}).get('spent_txo_sum', 0))
        current_balance = total_received - total_sent
        tx_count = address_info.get('chain_stats', {}).get('tx_count', 0)
        
        stats = {
            'total_received_btc': total_received,
            'total_sent_btc': total_sent,
            'current_balance_btc': current_balance,
            'transaction_count': tx_count,
            'average_transaction_size_btc': (total_received + total_sent) / (tx_count * 2) if tx_count > 0 else 0
        }
        
        return stats
    
    def display_address_stats(self, address_info):
        """Display address statistics"""
        stats_table = Table(title="Address Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats = self.calculate_address_stats(address_info)
        
        stats_table.add_row("Total Received", f"{stats['total_received_btc']:.8f} BTC")
        stats_table.add_row("Total Sent", f"{stats['total_sent_btc']:.8f} BTC")
        stats_table.add_row("Current Balance", f"{stats['current_balance_btc']:.8f} BTC")
        stats_table.add_row("Transaction Count", str(stats['transaction_count']))
        
        if stats['transaction_count'] > 0:
            stats_table.add_row("Average Transaction Size", f"{stats['average_transaction_size_btc']:.8f} BTC")
        
        self.console.print(stats_table)
        return stats
    
    def process_transactions(self, transactions, address, limit=10):
        """Process and return transaction data"""
        processed_transactions = []
        
        for i, tx in enumerate(transactions[:limit]):
            processed_tx = {
                'txid': tx['txid'],
                'confirmed': tx.get('status', {}).get('confirmed', False),
                'block_time': None,
                'formatted_time': None,
                'amount_in_satoshis': 0,
                'amount_out_satoshis': 0,
                'net_amount_satoshis': 0,
                'net_amount_btc': 0,
                'transaction_type': None,
                'fee_satoshis': tx.get('fee', 0),
                'fee_btc': self.satoshi_to_btc(tx.get('fee', 0))
            }
            
            if processed_tx['confirmed']:
                processed_tx['block_time'] = tx['status']['block_time']
                processed_tx['formatted_time'] = self.format_datetime(tx['status']['block_time'])
            
            # Calculate amounts
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
            processed_tx['amount_in_satoshis'] = amount_in
            processed_tx['amount_out_satoshis'] = amount_out
            processed_tx['net_amount_satoshis'] = net_amount
            processed_tx['net_amount_btc'] = self.satoshi_to_btc(net_amount)
            processed_tx['transaction_type'] = "Received" if net_amount > 0 else "Sent"
            
            processed_transactions.append(processed_tx)
        
        return processed_transactions
    
    def display_recent_transactions(self, transactions, address, limit=10):
        """Display recent transactions"""
        tx_table = Table(title=f"Recent Transactions (Last {min(limit, len(transactions))})")
        tx_table.add_column("Time", style="cyan")
        tx_table.add_column("TXID", style="yellow", max_width=20)
        tx_table.add_column("Type", style="magenta")
        tx_table.add_column("Amount (BTC)", style="green")
        tx_table.add_column("Fee (BTC)", style="red")
        
        processed_txs = self.process_transactions(transactions, address, limit)
        
        for tx in processed_txs:
            time_str = tx['formatted_time'] if tx['formatted_time'] else "Unconfirmed"
            txid = tx['txid'][:16] + "..."
            
            tx_table.add_row(
                time_str,
                txid,
                tx['transaction_type'],
                f"{abs(tx['net_amount_btc']):.8f}",
                f"{tx['fee_btc']:.8f}"
            )
        
        self.console.print(tx_table)
        return processed_txs
    
    def analyze_address_clustering(self, address, transactions):
        """Analyze address clustering and related addresses"""
        related_addresses = set()
        address_connections = {}
        clustering_data = {
            'related_addresses': [],
            'connection_details': {},
            'cluster_analysis': []
        }
        
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
        
        # Prepare clustering data for JSON export
        clustering_data['related_addresses'] = list(related_addresses)
        clustering_data['connection_details'] = address_connections
        
        sorted_connections = sorted(address_connections.items(), key=lambda x: x[1], reverse=True)
        
        for addr, count in sorted_connections:
            likelihood = "High" if count > 5 else "Medium" if count > 2 else "Low"
            clustering_data['cluster_analysis'].append({
                'address': addr,
                'connection_count': count,
                'likelihood': likelihood
            })
        
        # Display clustering results
        cluster_table = Table(title="Address Clustering Analysis")
        cluster_table.add_column("Related Address", style="cyan", max_width=35)
        cluster_table.add_column("Connection Count", style="green")
        cluster_table.add_column("Likelihood", style="yellow")
        
        for item in clustering_data['cluster_analysis'][:10]:  # Show top 10
            cluster_table.add_row(
                item['address'][:35] + "...", 
                str(item['connection_count']), 
                item['likelihood']
            )
        
        self.console.print(cluster_table)
        return clustering_data
    
    def create_network_data(self, address, clustering_data, transactions):
        """Create network graph data structure"""
        try:
            self.console.print("[yellow]Creating network data structure...[/yellow]")
            
            network_data = {
                'main_address': address,
                'nodes': [],
                'edges': [],
                'graph_metrics': {}
            }
            
            # Add main address node
            network_data['nodes'].append({
                'id': address,
                'type': 'main',
                'transaction_count': len(transactions),
                'label': f"Main: {address[:16]}..."
            })
            
            # Add related address nodes (limit to top 20)
            related_addresses = clustering_data['related_addresses'][:20]
            for related_addr in related_addresses:
                connection_count = clustering_data['connection_details'].get(related_addr, 1)
                network_data['nodes'].append({
                    'id': related_addr,
                    'type': 'related',
                    'connection_count': connection_count,
                    'label': f"Related: {related_addr[:16]}..."
                })
                
                # Add edge
                network_data['edges'].append({
                    'source': address,
                    'target': related_addr,
                    'weight': connection_count
                })
            
            network_data['graph_metrics'] = {
                'total_nodes': len(network_data['nodes']),
                'total_edges': len(network_data['edges']),
                'related_addresses_count': len(related_addresses)
            }
            
            self.console.print(f"[green]Network data created: {len(network_data['nodes'])} nodes, {len(network_data['edges'])} edges[/green]")
            return network_data
            
        except Exception as e:
            self.console.print(f"[red]Error creating network data: {type(e).__name__}: {str(e)}[/red]")
            return None
    
    def create_timeline_data(self, transactions, address):
        """Create timeline data structure"""
        try:
            self.console.print("[yellow]Creating timeline data...[/yellow]")
            
            timeline_data = {
                'address': address,
                'transactions': [],
                'summary_stats': {}
            }
            
            if not transactions:
                self.console.print("[yellow]No transactions to create timeline[/yellow]")
                return timeline_data
            
            confirmed_txs = []
            total_received = 0
            total_sent = 0
            
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
                    
                    net_amount_satoshis = amount_in - amount_out
                    net_amount_btc = self.satoshi_to_btc(net_amount_satoshis)
                    
                    tx_data = {
                        'txid': tx['txid'],
                        'timestamp': timestamp,
                        'formatted_date': date.isoformat(),
                        'readable_date': date.strftime("%Y-%m-%d %H:%M:%S"),
                        'amount_btc': abs(net_amount_btc),
                        'amount_satoshis': abs(net_amount_satoshis),
                        'net_amount_btc': net_amount_btc,
                        'net_amount_satoshis': net_amount_satoshis,
                        'type': 'Received' if net_amount_btc > 0 else 'Sent',
                        'fee_btc': self.satoshi_to_btc(tx.get('fee', 0)),
                        'fee_satoshis': tx.get('fee', 0)
                    }
                    
                    timeline_data['transactions'].append(tx_data)
                    confirmed_txs.append(tx_data)
                    
                    if net_amount_btc > 0:
                        total_received += net_amount_btc
                    else:
                        total_sent += abs(net_amount_btc)
            
            # Sort by timestamp
            timeline_data['transactions'].sort(key=lambda x: x['timestamp'])
            
            # Add summary statistics
            timeline_data['summary_stats'] = {
                'total_confirmed_transactions': len(confirmed_txs),
                'total_received_btc': total_received,
                'total_sent_btc': total_sent,
                'date_range': {
                    'earliest': timeline_data['transactions'][0]['readable_date'] if timeline_data['transactions'] else None,
                    'latest': timeline_data['transactions'][-1]['readable_date'] if timeline_data['transactions'] else None
                },
                'monthly_activity': self._calculate_monthly_activity(timeline_data['transactions'])
            }
            
            self.console.print(f"[green]Timeline data created with {len(confirmed_txs)} confirmed transactions[/green]")
            return timeline_data
            
        except Exception as e:
            self.console.print(f"[red]Error creating timeline data: {type(e).__name__}: {str(e)}[/red]")
            return None
    
    def _calculate_monthly_activity(self, transactions):
        """Calculate monthly transaction activity"""
        monthly_stats = {}
        
        for tx in transactions:
            date = datetime.fromisoformat(tx['formatted_date'].replace('Z', '+00:00'))
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'transaction_count': 0,
                    'total_received': 0,
                    'total_sent': 0,
                    'net_flow': 0
                }
            
            monthly_stats[month_key]['transaction_count'] += 1
            
            if tx['type'] == 'Received':
                monthly_stats[month_key]['total_received'] += tx['amount_btc']
                monthly_stats[month_key]['net_flow'] += tx['amount_btc']
            else:
                monthly_stats[month_key]['total_sent'] += tx['amount_btc']
                monthly_stats[month_key]['net_flow'] -= tx['amount_btc']
        
        return monthly_stats
    
    def export_analysis_to_json(self, address):
        """Export all analysis data to JSON file"""
        try:
            import os
            current_dir = os.getcwd()
            filename = f"bitcoin_analysis_{address[:8]}.json"
            file_path = os.path.join(current_dir, filename)
            
            self.console.print(f"[cyan]Exporting analysis data to: {file_path}[/cyan]")
            
            # Add metadata
            self.analysis_data['metadata'] = {
                'address': address,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'api_source': self.base_url
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_data, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.console.print(f"[green]Analysis data exported successfully![/green]")
                self.console.print(f"[green]File: {filename}[/green]")
                self.console.print(f"[green]Size: {file_size:,} bytes[/green]")
                self.console.print(f"[green]Location: {file_path}[/green]")
                return file_path
            else:
                self.console.print("[red]JSON file was not created[/red]")
                return None
                
        except Exception as e:
            self.console.print(f"[red]Error exporting to JSON: {type(e).__name__}: {str(e)}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback: {traceback.format_exc()}[/red]")
            return None
    
    def analyze_address(self, address):
        """Main function to analyze a Bitcoin address"""
        self.analysis_data = {}  # Reset analysis data
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing address...", total=6)
            
            # Step 1: Get basic address info
            progress.update(task, advance=1, description="[cyan]Fetching address info...")
            address_info = self.get_address_info(address)
            if not address_info:
                return None
            
            # Step 2: Get transactions
            progress.update(task, advance=1, description="[cyan]Fetching transactions...")
            transactions = self.get_address_transactions(address)
            
            # Step 3: Calculate and display statistics
            progress.update(task, advance=1, description="[cyan]Calculating statistics...")
            self.console.print(Panel.fit(f"[bold]Bitcoin Address Analysis: {address}[/bold]"))
            stats = self.display_address_stats(address_info)
            self.analysis_data['address_stats'] = stats
            self.analysis_data['address_info'] = address_info
            
            # Step 4: Process transactions
            progress.update(task, advance=1, description="[cyan]Processing transactions...")
            if transactions:
                processed_transactions = self.display_recent_transactions(transactions, address)
                self.analysis_data['recent_transactions'] = processed_transactions
                self.analysis_data['all_transactions'] = transactions
                
                # Address clustering analysis
                self.console.print("\n")
                clustering_data = self.analyze_address_clustering(address, transactions)
                self.analysis_data['clustering_analysis'] = clustering_data
                
                # Create network and timeline data
                progress.update(task, advance=1, description="[cyan]Creating data structures...")
                self.console.print("\n[yellow]Processing network and timeline data...[/yellow]")
                network_data = self.create_network_data(address, clustering_data, transactions)
                timeline_data = self.create_timeline_data(transactions, address)
                
                if network_data:
                    self.analysis_data['network_graph'] = network_data
                if timeline_data:
                    self.analysis_data['transaction_timeline'] = timeline_data
            
            # Step 6: Export to JSON
            progress.update(task, advance=1, description="[cyan]Exporting to JSON...")
            json_file = self.export_analysis_to_json(address)
            
            progress.update(task, description="[green]Analysis complete!")
            return json_file

def main():
    analyzer = BitcoinAddressAnalyzer()
    
    console.print(Panel.fit(
        "[bold blue]Bitcoin Address Analyzer - JSON Export Version[/bold blue]\n"
        "[cyan]Analyze Bitcoin addresses and export all data to JSON[/cyan]"
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
        
        json_file = analyzer.analyze_address(address)
        
        if json_file:
            console.print(f"\n[green]Analysis complete! All data exported to JSON file: {json_file}[/green]")
        else:
            console.print("\n[red]Analysis completed but JSON export failed[/red]")

if __name__ == "__main__":
    main()
