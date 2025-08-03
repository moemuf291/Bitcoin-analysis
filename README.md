# Bitcoin Address Analyzer

A comprehensive Bitcoin address analysis tool that exports all data to structured JSON files.

## Features

- **Address Statistics**: Total received, sent, current balance, and transaction count
- **Transaction History**: Detailed transaction data with timestamps and amounts
- **Address Clustering**: Analysis of related addresses and connection patterns
- **Network Graph Data**: Complete network structure data for address relationships
- **Transaction Timeline**: Time-series transaction data with monthly activity summaries
- **JSON Export**: All analysis data exported to structured JSON format

## Requirements

The following Python packages are required:
- requests
- rich
- networkx

## Installation

Install the required packages using pip:

```bash
pip install --break-system-packages requests rich networkx
```

Or on Ubuntu/Debian systems:

```bash
sudo apt update
sudo apt install -y python3-requests python3-rich python3-networkx
```

## Usage

### Interactive Mode

Run the script interactively to analyze any Bitcoin address:

```bash
python3 bitcoin_analysis.py
```

The program will prompt you to enter a Bitcoin address. After analysis, it will generate a JSON file containing all the analyzed data.

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

- **Custom Visualizations**: Import into visualization libraries (D3.js, Chart.js, etc.)
- **Data Analysis**: Process with pandas, R, or other analysis tools
- **API Integration**: Serve data through web APIs
- **Machine Learning**: Feature extraction for blockchain analysis models
- **Database Storage**: Import into databases for further querying
- **Report Generation**: Create custom reports and dashboards

## Troubleshooting

If the app is not generating JSON files:

1. Ensure all required packages are installed
2. Check that you have write permissions in the current directory
3. Verify the Bitcoin address format is valid (25-62 characters)
4. Check your internet connection for API access

## API Rate Limits

The app uses the free Blockstream API which may have rate limits. If you encounter errors, try waiting a few moments between requests.