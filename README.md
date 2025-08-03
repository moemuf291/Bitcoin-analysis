# Bitcoin Address Analyzer

A comprehensive Bitcoin address analysis tool that generates interactive HTML visualizations.

## Features

- **Address Statistics**: Total received, sent, current balance, and transaction count
- **Transaction History**: Recent transactions with timestamps and amounts
- **Address Clustering**: Analysis of related addresses and connection patterns
- **Interactive Network Graph**: Visual representation of address relationships (saved as `bitcoin_network_graph.html`)
- **Transaction Timeline**: Time-series visualization of transaction activity (saved as `bitcoin_timeline.html`)

## Requirements

The following Python packages are required and should be installed:
- plotly
- pandas
- networkx
- requests
- rich
- matplotlib

## Installation

On Ubuntu/Debian systems, install the required packages:

```bash
sudo apt update
sudo apt install -y python3-plotly python3-pandas python3-networkx python3-requests python3-rich python3-matplotlib
```

## Usage

### Interactive Mode

Run the script interactively to analyze any Bitcoin address:

```bash
python3 bitcoin_analysis.py
```

The program will prompt you to enter a Bitcoin address. After analysis, it will generate two HTML files:

1. **`bitcoin_network_graph.html`** - Interactive network visualization showing the analyzed address and its connections
2. **`bitcoin_timeline.html`** - Interactive timeline chart showing transaction history over time

### Example Analysis

The app has been tested with the Genesis block coinbase address (Satoshi's address):
`1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`

## Output Files

After running an analysis, you'll find the following HTML files in the current directory:

- **`bitcoin_network_graph.html`** - Network graph showing address relationships
- **`bitcoin_timeline.html`** - Timeline chart of transactions

These files can be opened in any web browser to view the interactive visualizations.

## How It Works

1. **Data Fetching**: Uses the Blockstream API to fetch address information and transaction data
2. **Analysis**: Processes transactions to identify patterns and related addresses
3. **Visualization**: Creates interactive plots using Plotly
4. **HTML Generation**: Saves visualizations as standalone HTML files

## Troubleshooting

If the app is not generating HTML files:

1. Ensure all required packages are installed
2. Check that you have write permissions in the current directory
3. Verify the Bitcoin address format is valid (25-62 characters)
4. Check your internet connection for API access

## API Rate Limits

The app uses the free Blockstream API which may have rate limits. If you encounter errors, try waiting a few moments between requests.