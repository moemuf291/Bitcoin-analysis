#!/usr/bin/env python3
"""
Test script for the Bitcoin Bubble Map Visualizer
This script demonstrates the bubble map functionality with different Bitcoin addresses.
"""

from bubble_map_visualizer import BitcoinBubbleMapVisualizer
import json

def test_bubble_map():
    """Test the bubble map visualizer with different addresses"""
    
    visualizer = BitcoinBubbleMapVisualizer()
    
    # Test addresses
    test_addresses = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block address
        "17SkEw2md5avvnyEa7WQz4UKa2q3NaLDKy",  # Pizza transaction address
        "1FzWLkAahHooV3Rzq2yBNSByUVv5m1hZRo",  # Exchange address
    ]
    
    print("Bitcoin Bubble Map Visualizer Test")
    print("=" * 50)
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n{i}. Testing address: {address}")
        print("-" * 40)
        
        try:
            # Analyze transaction flow
            address_flows = visualizer.analyze_transaction_flow(address, max_transactions=15)
            
            if address_flows:
                print(f"✓ Found {len(address_flows)} connected addresses")
                
                # Create bubble map data
                bubble_data = visualizer.create_bubble_map_data(address_flows, address)
                
                if bubble_data:
                    print(f"✓ Created bubble map with {len(bubble_data['addresses'])} nodes")
                    
                    # Show some statistics
                    total_volume = sum(bubble_data['total_flows'])
                    avg_volume = total_volume / len(bubble_data['total_flows']) if bubble_data['total_flows'] else 0
                    
                    print(f"  - Total transaction volume: {total_volume:.8f} BTC")
                    print(f"  - Average volume per address: {avg_volume:.8f} BTC")
                    print(f"  - Main address net flow: {bubble_data['net_flows'][0]:.8f} BTC")
                    
                    # Count positive vs negative flows
                    positive_flows = sum(1 for flow in bubble_data['net_flows'] if flow > 0)
                    negative_flows = sum(1 for flow in bubble_data['net_flows'] if flow < 0)
                    
                    print(f"  - Addresses with positive net flow: {positive_flows}")
                    print(f"  - Addresses with negative net flow: {negative_flows}")
                    
                    # Create plots (optional - for testing)
                    bubble_plot = visualizer.create_bubble_map_plot(bubble_data)
                    network_plot = visualizer.create_flow_network_plot(address_flows, address)
                    
                    if bubble_plot and network_plot:
                        print("✓ Successfully created both bubble map and network visualizations")
                    else:
                        print("✗ Failed to create visualizations")
                else:
                    print("✗ Failed to create bubble map data")
            else:
                print("✗ No transaction flow data found")
                
        except Exception as e:
            print(f"✗ Error analyzing address: {e}")
        
        print()

def main():
    """Main function"""
    print("Starting Bitcoin Bubble Map Test...")
    test_bubble_map()
    print("\nTest completed!")

if __name__ == "__main__":
    main()