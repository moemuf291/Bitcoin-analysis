# Bitcoin Transaction Bubble Map Visualizer

A powerful interactive visualization tool that maps Bitcoin transaction flows as interconnected bubbles, showing the movement of funds between addresses in an intuitive and visually appealing way.

## Features

### 🎯 **Bubble Map Visualization**
- **Interactive Bubbles**: Each bubble represents a Bitcoin address
- **Size Encoding**: Bubble size indicates the number of transactions
- **Color Coding**: 
  - 🔵 Blue = Main analyzed address
  - 🟢 Green = Positive net flow (received > sent)
  - 🔴 Red = Negative net flow (sent > received)
- **Position Mapping**: 
  - X-axis = Net flow (received - sent)
  - Y-axis = Total transaction volume
- **Connection Lines**: Show relationships between addresses

### 🌐 **Network Graph View**
- **Force-directed Layout**: Addresses positioned based on transaction relationships
- **Interactive Nodes**: Click and drag to explore the network
- **Edge Visualization**: Lines show transaction connections
- **Hover Details**: Rich tooltips with transaction information

### 📊 **Real-time Analysis**
- **Live Data**: Fetches real-time transaction data from Blockstream API
- **Address Discovery**: Automatically finds all connected addresses
- **Flow Calculation**: Computes net flows and transaction volumes
- **Statistical Summary**: Provides detailed analysis metrics

## How It Works

### 1. **Address Input**
Enter any Bitcoin address in the web interface or use the API directly.

### 2. **Transaction Analysis**
The system fetches recent transactions and analyzes:
- Input addresses (sending funds)
- Output addresses (receiving funds)
- Transaction amounts and timestamps
- Address relationships and connections

### 3. **Flow Mapping**
Creates a comprehensive map showing:
- **Transaction Flows**: How money moves between addresses
- **Volume Distribution**: Which addresses handle the most funds
- **Network Topology**: How addresses are connected
- **Temporal Patterns**: When transactions occurred

### 4. **Visualization Generation**
Produces two complementary views:
- **Bubble Map**: Scatter plot with size and color encoding
- **Network Graph**: Force-directed graph with interactive nodes

## Usage

### Web Interface
1. Start the Flask application:
   ```bash
   python3 app.py
   ```
2. Navigate to `http://localhost:5001/bubble_map`
3. Enter a Bitcoin address and click "Analyze"
4. Explore the interactive visualizations

### API Usage
```python
from bubble_map_visualizer import BitcoinBubbleMapVisualizer

# Create visualizer instance
visualizer = BitcoinBubbleMapVisualizer()

# Analyze an address
address_flows = visualizer.analyze_transaction_flow("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

# Create bubble map data
bubble_data = visualizer.create_bubble_map_data(address_flows, "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

# Generate visualizations
bubble_plot = visualizer.create_bubble_map_plot(bubble_data)
network_plot = visualizer.create_flow_network_plot(address_flows, "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
```

### REST API
```bash
# Get bubble map data for an address
curl "http://localhost:5001/api/bubble_map/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
```

## Sample Addresses

Try these famous Bitcoin addresses:

- **Genesis Block**: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
- **Pizza Transaction**: `17SkEw2md5avvnyEa7WQz4UKa2q3NaLDKy`
- **Exchange Address**: `1FzWLkAahHooV3Rzq2yBNSByUVv5m1hZRo`

## Technical Details

### Data Sources
- **Blockstream API**: Real-time Bitcoin blockchain data
- **Transaction Details**: Full transaction information including inputs/outputs
- **Address Metadata**: Balance, transaction count, and activity history

### Visualization Technologies
- **Plotly.js**: Interactive charts and graphs
- **NetworkX**: Graph analysis and layout algorithms
- **Flask**: Web framework for the API and interface
- **Bootstrap**: Responsive web design

### Analysis Features
- **Rate Limiting**: Respects API limits with intelligent delays
- **Error Handling**: Graceful degradation for network issues
- **Data Validation**: Ensures data integrity and completeness
- **Caching**: Optimizes performance for repeated requests

## Understanding the Visualizations

### Bubble Map Interpretation
- **Large Bubbles**: Addresses with many transactions
- **Right Side**: Addresses that received more than they sent
- **Left Side**: Addresses that sent more than they received
- **Top**: Addresses with high total transaction volume
- **Bottom**: Addresses with low transaction volume

### Network Graph Interpretation
- **Central Node**: The main analyzed address
- **Connected Nodes**: Addresses involved in transactions
- **Edge Thickness**: Represents transaction volume
- **Node Size**: Indicates transaction count
- **Node Color**: Shows net flow direction

### Color Legend
- 🔵 **Blue**: Main analyzed address
- 🟢 **Green**: Positive net flow (net receiver)
- 🔴 **Red**: Negative net flow (net sender)

## Use Cases

### 🔍 **Forensic Analysis**
- Track fund movements through multiple addresses
- Identify exchange wallets and mixing services
- Analyze transaction patterns and behaviors

### 📈 **Investment Research**
- Monitor whale wallet activities
- Track institutional Bitcoin movements
- Analyze market participant behavior

### 🛡️ **Security Analysis**
- Detect suspicious transaction patterns
- Identify potential money laundering schemes
- Monitor known malicious addresses

### 📊 **Academic Research**
- Study Bitcoin network topology
- Analyze transaction graph properties
- Research cryptocurrency economics

## Performance Considerations

### Optimization Features
- **Limited Analysis**: Configurable transaction limit (default: 30)
- **Rate Limiting**: 0.1 second delays between API calls
- **Error Recovery**: Continues analysis even if some transactions fail
- **Memory Management**: Efficient data structures for large networks

### Scalability
- **Modular Design**: Easy to extend with new features
- **API Abstraction**: Can switch between different data sources
- **Caching Layer**: Reduces redundant API calls
- **Background Processing**: Non-blocking analysis for large datasets

## Future Enhancements

### Planned Features
- **Time-based Filtering**: Analyze specific time periods
- **Address Clustering**: Group related addresses automatically
- **Pattern Recognition**: Identify common transaction patterns
- **Export Functionality**: Save visualizations as images/PDFs
- **Mobile Support**: Responsive design for mobile devices

### Advanced Analytics
- **Machine Learning**: Predict transaction patterns
- **Anomaly Detection**: Identify unusual transaction behavior
- **Risk Scoring**: Calculate address risk levels
- **Temporal Analysis**: Track changes over time

## Contributing

### Development Setup
1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt --break-system-packages
   ```

2. Run tests:
   ```bash
   python3 test_bubble_map.py
   ```

3. Start development server:
   ```bash
   python3 app.py
   ```

### Code Structure
- `bubble_map_visualizer.py`: Core visualization logic
- `app.py`: Flask web application
- `templates/bubble_map.html`: Web interface
- `test_bubble_map.py`: Test suite

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or contributions, please open an issue on the project repository.

---

**Bitcoin Bubble Map Visualizer** - Making Bitcoin transaction analysis accessible and intuitive through powerful interactive visualizations.