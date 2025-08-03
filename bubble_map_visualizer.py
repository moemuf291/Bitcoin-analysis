#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import plotly.graph_objs as go
import plotly.utils
from flask import Flask, render_template, jsonify
import networkx as nx
import math
from rich.console import Console

class BitcoinBubbleMapVisualizer:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.console = Console()
        
    def satoshi_to_btc(self, satoshis):
        """Convert satoshis to BTC"""
        return satoshis / 100000000
    
    def get_address_info(self, address):
        """Get basic address information"""
        try:
            response = requests.get(f"{self.base_url}/address/{address}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching address info: {e}")
            return None
    
    def get_address_transactions(self, address, limit=50):
        """Get transactions for an address"""
        try:
            url = f"{self.base_url}/address/{address}/txs"
            response = requests.get(url)
            if response.status_code == 200:
                transactions = response.json()
                return transactions[:limit]
            else:
                return []
        except Exception as e:
            print(f"Error fetching transactions: {e}")
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
            print(f"Error fetching transaction details: {e}")
            return None
    
    def analyze_transaction_flow(self, address, max_transactions=30):
        """Analyze transaction flow and create bubble map data"""
        print(f"Analyzing transaction flow for address: {address}")
        
        # Get address info
        address_info = self.get_address_info(address)
        if not address_info:
            return None
        
        # Get recent transactions
        transactions = self.get_address_transactions(address, max_transactions)
        if not transactions:
            return None
        
        # Collect all unique addresses involved in transactions
        address_flows = defaultdict(lambda: {
            'total_received': 0,
            'total_sent': 0,
            'transaction_count': 0,
            'first_seen': None,
            'last_seen': None
        })
        
        # Initialize with the main address
        address_flows[address] = {
            'total_received': 0,
            'total_sent': 0,
            'transaction_count': 0,
            'first_seen': None,
            'last_seen': None
        }
        
        # Analyze each transaction
        for tx in transactions:
            tx_details = self.get_transaction_details(tx['txid'])
            if not tx_details:
                continue
            
            tx_time = tx_details.get('status', {}).get('block_time', 0)
            tx_date = datetime.fromtimestamp(tx_time) if tx_time else datetime.now()
            
            # Analyze inputs and outputs
            for vin in tx_details.get('vin', []):
                if 'prevout' in vin and 'scriptpubkey_address' in vin['prevout']:
                    input_address = vin['prevout']['scriptpubkey_address']
                    input_amount = self.satoshi_to_btc(vin['prevout'].get('value', 0))
                    
                    address_flows[input_address]['total_sent'] += input_amount
                    address_flows[input_address]['transaction_count'] += 1
                    
                    if not address_flows[input_address]['first_seen'] or tx_date < address_flows[input_address]['first_seen']:
                        address_flows[input_address]['first_seen'] = tx_date
                    if not address_flows[input_address]['last_seen'] or tx_date > address_flows[input_address]['last_seen']:
                        address_flows[input_address]['last_seen'] = tx_date
            
            for vout in tx_details.get('vout', []):
                if 'scriptpubkey_address' in vout:
                    output_address = vout['scriptpubkey_address']
                    output_amount = self.satoshi_to_btc(vout.get('value', 0))
                    
                    address_flows[output_address]['total_received'] += output_amount
                    address_flows[output_address]['transaction_count'] += 1
                    
                    if not address_flows[output_address]['first_seen'] or tx_date < address_flows[output_address]['first_seen']:
                        address_flows[output_address]['first_seen'] = tx_date
                    if not address_flows[output_address]['last_seen'] or tx_date > address_flows[output_address]['last_seen']:
                        address_flows[output_address]['last_seen'] = tx_date
            
            time.sleep(0.1)  # Rate limiting
        
        return address_flows
    
    def create_bubble_map_data(self, address_flows, main_address):
        """Create bubble map visualization data"""
        if not address_flows:
            return None
        
        # Prepare data for bubble chart
        addresses = list(address_flows.keys())
        total_flows = []
        net_flows = []
        transaction_counts = []
        colors = []
        labels = []
        
        for addr in addresses:
            flow_data = address_flows[addr]
            total_flow = flow_data['total_received'] + flow_data['total_sent']
            net_flow = flow_data['total_received'] - flow_data['total_sent']
            
            total_flows.append(total_flow)
            net_flows.append(net_flow)
            transaction_counts.append(flow_data['transaction_count'])
            
            # Color coding: green for positive net flow, red for negative, blue for main address
            if addr == main_address:
                colors.append('blue')
            elif net_flow > 0:
                colors.append('green')
            else:
                colors.append('red')
            
            # Create labels
            short_addr = addr[:8] + '...' + addr[-8:] if len(addr) > 16 else addr
            labels.append(f"{short_addr}<br>Net: {net_flow:.6f} BTC<br>Total: {total_flow:.6f} BTC")
        
        return {
            'addresses': addresses,
            'total_flows': total_flows,
            'net_flows': net_flows,
            'transaction_counts': transaction_counts,
            'colors': colors,
            'labels': labels,
            'main_address': main_address
        }
    
    def create_bubble_map_plot(self, bubble_data):
        """Create interactive bubble map plot"""
        if not bubble_data:
            return None
        
        # Create bubble chart
        fig = go.Figure()
        
        # Add bubble trace
        fig.add_trace(go.Scatter(
            x=bubble_data['net_flows'],
            y=bubble_data['total_flows'],
            mode='markers+text',
            marker=dict(
                size=[max(10, count * 2) for count in bubble_data['transaction_counts']],
                color=bubble_data['colors'],
                opacity=0.7,
                line=dict(width=2, color='black')
            ),
            text=[addr[:8] + '...' for addr in bubble_data['addresses']],
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            hovertemplate="<b>%{text}</b><br>" +
                         "Net Flow: %{x:.6f} BTC<br>" +
                         "Total Flow: %{y:.6f} BTC<br>" +
                         "Transactions: %{marker.size}<extra></extra>",
            name="Addresses"
        ))
        
        # Add connection lines (simplified network representation)
        main_idx = bubble_data['addresses'].index(bubble_data['main_address'])
        main_x = bubble_data['net_flows'][main_idx]
        main_y = bubble_data['total_flows'][main_idx]
        
        # Add lines from main address to others
        for i, addr in enumerate(bubble_data['addresses']):
            if i != main_idx:
                fig.add_trace(go.Scatter(
                    x=[main_x, bubble_data['net_flows'][i]],
                    y=[main_y, bubble_data['total_flows'][i]],
                    mode='lines',
                    line=dict(width=1, color='gray', dash='dot'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        fig.update_layout(
            title="Bitcoin Transaction Flow Bubble Map",
            xaxis_title="Net Flow (BTC) - Positive = Received, Negative = Sent",
            yaxis_title="Total Transaction Volume (BTC)",
            hovermode='closest',
            template='plotly_white',
            showlegend=False
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_flow_network_plot(self, address_flows, main_address):
        """Create a network graph showing transaction flows"""
        if not address_flows:
            return None
        
        # Create network graph
        G = nx.DiGraph()
        
        # Add nodes
        for addr, data in address_flows.items():
            G.add_node(addr, 
                      total_received=data['total_received'],
                      total_sent=data['total_sent'],
                      transaction_count=data['transaction_count'])
        
        # Add edges based on transaction relationships
        # This is a simplified approach - in reality, you'd need to analyze actual transaction flows
        for addr in address_flows.keys():
            if addr != main_address:
                # Create a directed edge from main address to this address
                G.add_edge(main_address, addr, weight=address_flows[addr]['total_received'])
        
        # Calculate node positions using spring layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Prepare data for plotly
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = G.nodes[node]
            total_flow = data['total_received'] + data['total_sent']
            net_flow = data['total_received'] - data['total_sent']
            
            short_addr = node[:8] + '...' + node[-8:] if len(node) > 16 else node
            node_text.append(f"{short_addr}<br>Net: {net_flow:.6f} BTC<br>Total: {total_flow:.6f} BTC")
            
            node_size.append(max(10, data['transaction_count'] * 3))
            
            if node == main_address:
                node_color.append('blue')
            elif net_flow > 0:
                node_color.append('green')
            else:
                node_color.append('red')
        
        # Create network plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='gray'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color=node_color,
                opacity=0.8,
                line=dict(width=2, color='black')
            ),
            text=[addr[:8] + '...' for addr in G.nodes()],
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            hovertemplate="<b>%{text}</b><br>" +
                         "Net Flow: %{marker.size}<extra></extra>",
            name="Addresses"
        ))
        
        fig.update_layout(
            title="Bitcoin Transaction Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def main():
    """Main function to test the bubble map visualizer"""
    visualizer = BitcoinBubbleMapVisualizer()
    
    # Example Bitcoin address (you can replace this with any address)
    test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Genesis block address
    
    print(f"Analyzing transaction flow for: {test_address}")
    
    # Analyze transaction flow
    address_flows = visualizer.analyze_transaction_flow(test_address, max_transactions=20)
    
    if address_flows:
        # Create bubble map data
        bubble_data = visualizer.create_bubble_map_data(address_flows, test_address)
        
        if bubble_data:
            # Create plots
            bubble_plot = visualizer.create_bubble_map_plot(bubble_data)
            network_plot = visualizer.create_flow_network_plot(address_flows, test_address)
            
            print("Bubble map and network visualization created successfully!")
            print("You can now integrate these plots into your Flask app.")
            
            return {
                'bubble_plot': bubble_plot,
                'network_plot': network_plot,
                'address_flows': address_flows
            }
    
    print("Failed to create visualization.")
    return None

if __name__ == "__main__":
    main()