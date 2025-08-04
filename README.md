# Bitcoin Address Analyzer

![Bitcoin Analysis Screenshot](https://raw.githubusercontent.com/moemuf291/Bitcoin-analysis/refs/heads/main/images/Screenshot%20(6).png)


A comprehensive Bitcoin address analysis tool that exports all data to structured JSON files and provides interactive web visualizations.

## Features

### Core Analysis
- **Address Statistics**: Total received, sent, current balance, and transaction count
- **Transaction History**: Detailed transaction data with timestamps and amounts
- **Address Clustering**: Analysis of related addresses and connection patterns
- **Network Graph Data**: Complete network structure data for address relationships
- **Transaction Timeline**: Time-series transaction data with monthly activity summaries
- **JSON Export**: All analysis data exported to structured JSON format

### Web Visualization (NEW! 🚀)
- **Interactive Charts**: Transaction timeline, balance over time, volume distribution
- **Network Visualization**: Interactive graph of connected Bitcoin addresses
- **Statistical Dashboard**: Real-time statistics and key metrics
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **File Management**: Easy selection and analysis of multiple JSON files

## Requirements

### For Bitcoin Analysis
- requests
- rich
- networkx

### For Web Visualization
- flask
- plotly

## Installation

### Install All Requirements

Install all required packages using pip:

```bash
pip install --break-system-packages requests rich networkx flask plotly
```

Or on Ubuntu/Debian systems:

```bash
sudo apt update
sudo apt install -y python3-requests python3-rich python3-networkx python3-flask python3-plotly
```

### Install Only Analysis Requirements

If you only want the command-line analysis tool:

```bash
pip install --break-system-packages requests rich networkx
```

## Usage

### 1. Bitcoin Address Analysis

Run the script interactively to analyze any Bitcoin address:

```bash
python3 bitcoin_analysis.py
```

The program will prompt you to enter a Bitcoin address. After analysis, it will generate a JSON file containing all the analyzed data.

### 2. Web Visualization 🌐

After generating JSON files, launch the interactive web visualizer:

```bash
python3 run_visualizer.py
```

Or manually start the Flask app:

```bash
python3 app.py
```

Then open your browser and go to: **http://localhost:5000**

#### Web Features:
- **Dashboard**: Browse and select analysis files
- **Interactive Charts**: 
  - Transaction timeline with hover details
  - Cumulative balance over time
  - Transaction volume distribution
  - Address network graph
- **Statistics Panel**: Key metrics and summaries
- **Responsive Design**: Works on all devices

### Example Analysis

The app has been tested with the Genesis block coinbase address (Satoshi's address):
`1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`

## Output Files

After running an analysis, you'll find a JSON file in the current directory:

**`bitcoin_analysis_[address_prefix].json`** - Complete analysis data in JSON format

### JSON Structure

The exported JSON file contains the following sections:

- **`address_stats`** - Summary statistics (balance, transaction count, etc.)
- **`address_info`** - Raw address information from the blockchain API
- **`recent_transactions`** - Processed recent transaction data
- **`all_transactions`** - Complete transaction history
- **`clustering_analysis`** - Related addresses and connection analysis
- **`network_graph`** - Network structure with nodes and edges
- **`transaction_timeline`** - Time-series transaction data with monthly summaries
- **`metadata`** - Analysis timestamp and source information

### Sample JSON Output

```json
{
  "address_stats": {
    "total_received_btc": 54.28756541,
    "total_sent_btc": 0.0,
    "current_balance_btc": 54.28756541,
    "transaction_count": 49579,
    "average_transaction_size_btc": 0.00054749
  },
  "network_graph": {
    "main_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "nodes": [...],
    "edges": [...],
    "graph_metrics": {
      "total_nodes": 21,
      "total_edges": 20
    }
  },
  "transaction_timeline": {
    "transactions": [...],
    "summary_stats": {
      "total_confirmed_transactions": 25,
      "monthly_activity": {...}
    }
  }
}
```

## How It Works

1. **Data Fetching**: Uses the Blockstream API to fetch address information and transaction data
2. **Analysis**: Processes transactions to identify patterns and related addresses
3. **Data Processing**: Creates structured network and timeline data
4. **JSON Export**: Saves all analysis data as a comprehensive JSON file

## Use Cases for JSON Data

The structured JSON output can be used for:

- **Web Visualizations**: Use our built-in Flask web app for interactive charts
- **Custom Visualizations**: Import into visualization libraries (D3.js, Chart.js, etc.)
- **Data Analysis**: Process with pandas, R, or other analysis tools
- **API Integration**: Serve data through web APIs
- **Machine Learning**: Feature extraction for blockchain analysis models
- **Database Storage**: Import into databases for further querying
- **Report Generation**: Create custom reports and dashboards

## Screenshots
![Bitcoin Analysis Screenshot 5](https://raw.githubusercontent.com/moemuf291/Bitcoin-analysis/refs/heads/main/images/Screenshot%20(7).png)


![Bitcoin Analysis Screenshot 2](https://raw.githubusercontent.com/moemuf291/Bitcoin-analysis/refs/heads/main/images/Screenshot%20(2).png)

![Bitcoin Analysis Screenshot 3](https://raw.githubusercontent.com/moemuf291/Bitcoin-analysis/refs/heads/main/images/Screenshot%20(3).png)

![Bitcoin Analysis Screenshot 4](https://raw.githubusercontent.com/moemuf291/Bitcoin-analysis/refs/heads/main/images/Screenshot%20(5).png)


### Web Dashboard
The interactive web interface provides an intuitive way to browse and visualize Bitcoin analysis data:

- **File Browser**: Select from available JSON analysis files
- **Transaction Timeline**: Interactive chart showing transactions over time
- **Balance Tracking**: Cumulative balance changes with hover details
- **Volume Analysis**: Distribution of transaction amounts
- **Network Graph**: Visual representation of address connections
- **Statistics Panel**: Key metrics and summary data

## Troubleshooting

If the app is not generating JSON files:

1. Ensure all required packages are installed
2. Check that you have write permissions in the current directory
3. Verify the Bitcoin address format is valid (25-62 characters)
4. Check your internet connection for API access

## API Rate Limits

The app uses the free Blockstream API which may have rate limits. If you encounter errors, try waiting a few moments between requests.

## License

[MIT](https://choosealicense.com/licenses/mit/)



