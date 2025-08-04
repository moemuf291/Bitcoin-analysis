#!/usr/bin/env python3
import os
import json
import glob
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import plotly.graph_objs as go
import plotly.utils
import networkx as nx
from collections import defaultdict
from bubble_map_visualizer import BitcoinBubbleMapVisualizer

app = Flask(__name__)
app.secret_key = 'bitcoin_analysis_secret_key'

class BitcoinVisualizationApp:
    def __init__(self):
        self.json_files = self.get_json_files()
    
    def get_json_files(self):
        """Get all JSON analysis files in the current directory"""
        pattern = "bitcoin_analysis_*.json"
        return glob.glob(pattern)
    
    def load_json_data(self, filename):
        """Load and parse JSON analysis data"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def create_transaction_timeline_plot(self, data):
        """Create interactive timeline of transactions"""
        # Try to get timeline data from different possible keys
        timeline_data = None
        if 'transaction_timeline' in data:
            timeline_data = data['transaction_timeline']
        elif 'recent_transactions' in data:
            timeline_data = data['recent_transactions']
            print("Using recent_transactions for timeline plot")
        else:
            print(f"Warning: No timeline data found. Available keys: {list(data.keys())}")
            return None
        
        # Check if timeline_data is a list
        if not isinstance(timeline_data, list):
            print(f"Warning: timeline_data is not a list, it's {type(timeline_data)}")
            # If it's a dict, try to extract the list from it
            if isinstance(timeline_data, dict):
                # Look for common keys that might contain the list
                for key in ['transactions', 'data', 'items', 'list']:
                    if key in timeline_data and isinstance(timeline_data[key], list):
                        timeline_data = timeline_data[key]
                        print(f"Found timeline data in key: {key}")
                        break
                else:
                    print("Could not find list data in timeline_data dict")
                    return None
            else:
                return None
        
        dates = []
        amounts = []
        tx_types = []
        
        for tx in timeline_data:
            # Check if tx is a dictionary
            if not isinstance(tx, dict):
                print(f"Warning: transaction item is not a dict: {type(tx)}")
                continue
                
            # Handle different date field names and formats
            date_str = tx.get('date') or tx.get('formatted_date') or tx.get('timestamp')
            if date_str:
                try:
                    if isinstance(date_str, (int, float)):
                        dates.append(datetime.fromtimestamp(date_str))
                    else:
                        dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
                except (ValueError, TypeError):
                    continue
            
            amounts.append(tx.get('net_amount_btc', 0))
            tx_types.append(tx.get('transaction_type', 'Unknown'))
        
        if not dates:
            print("Warning: No valid dates found in timeline data")
            return None
        
        # Create color mapping
        colors = ['green' if t == 'Received' else 'red' for t in tx_types]
        
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=dates,
            y=amounts,
            mode='markers+lines',
            marker=dict(
                color=colors,
                size=8,
                line=dict(width=1, color='black')
            ),
            line=dict(width=2, color='blue'),
            text=[f"Type: {t}<br>Amount: {a:.8f} BTC" for t, a in zip(tx_types, amounts)],
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>Date: %{x}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Bitcoin Transaction Timeline",
            xaxis_title="Date",
            yaxis_title="Amount (BTC)",
            hovermode='closest',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_balance_over_time_plot(self, data):
        """Create cumulative balance over time plot"""
        # Try to get timeline data from different possible keys
        timeline_data = None
        if 'transaction_timeline' in data:
            timeline_data = data['transaction_timeline']
        elif 'recent_transactions' in data:
            timeline_data = data['recent_transactions']
            print("Using recent_transactions for balance plot")
        else:
            print(f"Warning: No timeline data found. Available keys: {list(data.keys())}")
            return None
        
        # Check if timeline_data is a list
        if not isinstance(timeline_data, list):
            print(f"Warning: timeline_data is not a list, it's {type(timeline_data)}")
            # If it's a dict, try to extract the list from it
            if isinstance(timeline_data, dict):
                # Look for common keys that might contain the list
                for key in ['transactions', 'data', 'items', 'list']:
                    if key in timeline_data and isinstance(timeline_data[key], list):
                        timeline_data = timeline_data[key]
                        print(f"Found timeline data in key: {key}")
                        break
                else:
                    print("Could not find list data in timeline_data dict")
                    return None
            else:
                return None
        
        # Sort by date with robust date handling
        def get_date(tx):
            if not isinstance(tx, dict):
                return datetime.min
            date_str = tx.get('date') or tx.get('formatted_date') or tx.get('timestamp')
            if date_str:
                try:
                    if isinstance(date_str, (int, float)):
                        return datetime.fromtimestamp(date_str)
                    else:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    return datetime.min
            return datetime.min
        
        timeline_data = sorted(timeline_data, key=get_date)
        
        dates = []
        cumulative_balance = 0
        balances = []
        
        for tx in timeline_data:
            if not isinstance(tx, dict):
                continue
            date_obj = get_date(tx)
            if date_obj != datetime.min:
                dates.append(date_obj)
                cumulative_balance += tx.get('net_amount_btc', 0)
                balances.append(cumulative_balance)
        
        if not dates:
            print("Warning: No valid dates found in timeline data")
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=balances,
            mode='lines+markers',
            fill='tonexty',
            marker=dict(size=6, color='blue'),
            line=dict(width=3, color='blue'),
            hovertemplate="<b>Balance: %{y:.8f} BTC</b><br>Date: %{x}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Cumulative Balance Over Time",
            xaxis_title="Date",
            yaxis_title="Balance (BTC)",
            hovermode='closest',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_transaction_volume_plot(self, data):
        """Create transaction volume analysis"""
        # Try to get transactions from different possible keys
        transactions = None
        if 'recent_transactions' in data:
            transactions = data['recent_transactions']
        elif 'all_transactions' in data:
            transactions = data['all_transactions']
            print("Using all_transactions for volume plot")
        else:
            print(f"Warning: No transaction data found for volume plot. Available keys: {list(data.keys())}")
            return None
        
        # Group by transaction type
        received_amounts = []
        sent_amounts = []
        
        for tx in transactions:
            if tx['transaction_type'] == 'Received':
                received_amounts.append(abs(tx['net_amount_btc']))
            else:
                sent_amounts.append(abs(tx['net_amount_btc']))
        
        fig = go.Figure()
        
        if received_amounts:
            fig.add_trace(go.Histogram(
                x=received_amounts,
                name='Received',
                opacity=0.7,
                marker_color='green',
                nbinsx=20
            ))
        
        if sent_amounts:
            fig.add_trace(go.Histogram(
                x=sent_amounts,
                name='Sent',
                opacity=0.7,
                marker_color='red',
                nbinsx=20
            ))
        
        fig.update_layout(
            title="Transaction Volume Distribution",
            xaxis_title="Amount (BTC)",
            yaxis_title="Frequency",
            barmode='overlay',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_network_graph(self, data):
        """Create interactive network graph"""
        if 'network_graph' not in data or not data['network_graph']:
            return None
        
        network_data = data['network_graph']
        
        # Create networkx graph
        G = nx.Graph()
        
        # Add nodes and edges from the network data
        if 'nodes' in network_data:
            for node in network_data['nodes']:
                G.add_node(node['id'], **node)
        
        if 'edges' in network_data:
            for edge in network_data['edges']:
                G.add_edge(edge['source'], edge['target'], **edge)
        
        # Create layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Extract node and edge positions
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
        node_colors = []
        node_addresses = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Address: {node[:8]}...")
            node_addresses.append(node)  # Store full address
            # Color based on node type or transaction count
            node_colors.append(len(list(G.neighbors(node))))
        
        # Create plotly figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightgray'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=10,
                color=node_colors,
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Connections")
            ),
            text=node_text,
            textposition="middle center",
            hovertemplate="<b>Bitcoin Address</b><br>" +
                         "Full Address: %{customdata}<br>" +
                         "Connections: %{marker.color}<br>" +
                         "<i>Click to copy address</i><extra></extra>",
            customdata=node_addresses
        ))
        
        fig.update_layout(
            title="Bitcoin Address Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Network visualization of connected Bitcoin addresses",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_statistics_summary(self, data):
        """Create summary statistics"""
        stats = {}
        
        if 'address_stats' in data:
            stats.update(data['address_stats'])
        
        if 'recent_transactions' in data:
            transactions = data['recent_transactions']
            stats['total_transactions_analyzed'] = len(transactions)
            
            received_count = sum(1 for tx in transactions if tx['transaction_type'] == 'Received')
            sent_count = len(transactions) - received_count
            
            stats['received_transactions'] = received_count
            stats['sent_transactions'] = sent_count
            
            total_received = sum(tx['net_amount_btc'] for tx in transactions if tx['transaction_type'] == 'Received')
            total_sent = sum(abs(tx['net_amount_btc']) for tx in transactions if tx['transaction_type'] == 'Sent')
            
            stats['total_received_btc'] = total_received
            stats['total_sent_btc'] = total_sent
        
        return stats
    
    def analyze_top_addresses(self, data):
        """Analyze and find addresses that sent/received the most funds"""
        # Try to get transactions from different possible keys
        transactions = None
        if 'all_transactions' in data:
            transactions = data['all_transactions']
        elif 'recent_transactions' in data:
            transactions = data['recent_transactions']
            print("Using recent_transactions instead of all_transactions")
        else:
            print(f"Warning: No transaction data found. Available keys: {list(data.keys())}")
            return None
        
        # Check if transactions is a list
        if not isinstance(transactions, list):
            print(f"Warning: transactions is not a list, it's {type(transactions)}")
            return None
        
        address_flows = defaultdict(lambda: {
            'total_received': 0,
            'total_sent': 0,
            'transaction_count': 0,
            'address': ''
        })
        
        # Analyze each transaction to find address flows
        for tx in transactions:
            if not isinstance(tx, dict):
                print(f"Warning: transaction item is not a dict: {type(tx)}")
                continue
                
            # Get transaction details
            tx_details = self.get_transaction_details(tx.get('txid', ''))
            if not tx_details:
                continue
            
            # Analyze inputs (addresses that sent funds)
            for vin in tx_details.get('vin', []):
                if isinstance(vin, dict) and 'prevout' in vin and 'scriptpubkey_address' in vin['prevout']:
                    input_address = vin['prevout']['scriptpubkey_address']
                    input_amount = vin['prevout'].get('value', 0) / 100000000  # Convert to BTC
                    
                    address_flows[input_address]['total_sent'] += input_amount
                    address_flows[input_address]['transaction_count'] += 1
                    address_flows[input_address]['address'] = input_address
            
            # Analyze outputs (addresses that received funds)
            for vout in tx_details.get('vout', []):
                if isinstance(vout, dict) and 'scriptpubkey_address' in vout:
                    output_address = vout['scriptpubkey_address']
                    output_amount = vout.get('value', 0) / 100000000  # Convert to BTC
                    
                    address_flows[output_address]['total_received'] += output_amount
                    address_flows[output_address]['transaction_count'] += 1
                    address_flows[output_address]['address'] = output_address
        
        # Find top addresses
        top_senders = sorted(
            [(addr, data) for addr, data in address_flows.items() if data['total_sent'] > 0],
            key=lambda x: x[1]['total_sent'],
            reverse=True
        )[:10]
        
        top_receivers = sorted(
            [(addr, data) for addr, data in address_flows.items() if data['total_received'] > 0],
            key=lambda x: x[1]['total_received'],
            reverse=True
        )[:10]
        
        return {
            'top_senders': top_senders,
            'top_receivers': top_receivers,
            'total_addresses_analyzed': len(address_flows)
        }
    
    def get_transaction_details(self, txid):
        """Get detailed transaction information"""
        try:
            response = requests.get(f"https://blockstream.info/api/tx/{txid}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching transaction details: {e}")
            return None
    
    def create_bubble_map_visualization(self, address):
        """Create bubble map visualization for a Bitcoin address"""
        try:
            visualizer = BitcoinBubbleMapVisualizer()
            
            # Analyze transaction flow
            address_flows = visualizer.analyze_transaction_flow(address, max_transactions=30)
            
            if not address_flows:
                return None, None
            
            # Create bubble map data
            bubble_data = visualizer.create_bubble_map_data(address_flows, address)
            
            if not bubble_data:
                return None, None
            
            # Create plots
            bubble_plot = visualizer.create_bubble_map_plot(bubble_data)
            network_plot = visualizer.create_flow_network_plot(address_flows, address)
            
            return bubble_plot, network_plot
            
        except Exception as e:
            print(f"Error creating bubble map visualization: {e}")
            return None, None

# Initialize the visualization app
viz_app = BitcoinVisualizationApp()

@app.route('/')
def index():
    """Main page showing available JSON files"""
    viz_app.json_files = viz_app.get_json_files()  # Refresh file list
    return render_template('index.html', json_files=viz_app.json_files)

@app.route('/analyze/<filename>')
def analyze(filename):
    """Analyze and visualize a specific JSON file"""
    if filename not in viz_app.json_files:
        flash('File not found!', 'error')
        return redirect(url_for('index'))
    
    data = viz_app.load_json_data(filename)
    if not data:
        flash('Error loading JSON data!', 'error')
        return redirect(url_for('index'))
    
    # Create all visualizations with error handling
    timeline_plot = None
    balance_plot = None
    volume_plot = None
    network_plot = None
    statistics = None
    top_addresses = None
    
    try:
        timeline_plot = viz_app.create_transaction_timeline_plot(data)
    except Exception as e:
        print(f"Error creating timeline plot: {e}")
        
    try:
        balance_plot = viz_app.create_balance_over_time_plot(data)
    except Exception as e:
        print(f"Error creating balance plot: {e}")
        
    try:
        volume_plot = viz_app.create_transaction_volume_plot(data)
    except Exception as e:
        print(f"Error creating volume plot: {e}")
        
    try:
        network_plot = viz_app.create_network_graph(data)
    except Exception as e:
        print(f"Error creating network plot: {e}")
        
    try:
        statistics = viz_app.create_statistics_summary(data)
    except Exception as e:
        print(f"Error creating statistics: {e}")
        statistics = {}
    
    try:
        top_addresses = viz_app.analyze_top_addresses(data)
        if top_addresses and (not top_addresses.get('top_senders') and not top_addresses.get('top_receivers')):
            print("No top addresses found in analysis")
            top_addresses = None
    except Exception as e:
        print(f"Error analyzing top addresses: {e}")
        top_addresses = None
    
    return render_template('analysis.html', 
                         filename=filename,
                         timeline_plot=timeline_plot,
                         balance_plot=balance_plot,
                         volume_plot=volume_plot,
                         network_plot=network_plot,
                         statistics=statistics,
                         top_addresses=top_addresses,
                         address=data.get('metadata', {}).get('address', 'Unknown'))

@app.route('/api/refresh_files')
def refresh_files():
    """API endpoint to refresh the file list"""
    viz_app.json_files = viz_app.get_json_files()
    return jsonify({'files': viz_app.json_files})

@app.route('/bubble_map')
def bubble_map():
    """Bubble map visualization page"""
    return render_template('bubble_map.html')

@app.route('/api/bubble_map/<address>')
def get_bubble_map(address):
    """API endpoint to get bubble map data for an address"""
    try:
        bubble_plot, network_plot = viz_app.create_bubble_map_visualization(address)
        
        if bubble_plot and network_plot:
            return jsonify({
                'success': True,
                'bubble_plot': bubble_plot,
                'network_plot': network_plot
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create bubble map visualization'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)