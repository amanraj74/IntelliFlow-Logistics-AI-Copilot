#!/usr/bin/env python
"""
Shipment Anomaly Detection Demo Script

This script demonstrates the complete workflow for shipment anomaly detection:
1. Generate sample shipment data
2. Process shipments to detect anomalies
3. Display summary of detected anomalies
"""

import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_generator import DataGenerator
from backend.analytics.shipment_anomaly_detector import process_shipments_directory


def main():
    """Run the shipment anomaly detection demo."""
    parser = argparse.ArgumentParser(description='Shipment Anomaly Detection Demo')
    parser.add_argument('--shipments', type=int, default=20, help='Number of shipments to generate')
    parser.add_argument('--output-dir', default='data/streams', help='Directory to write generated data')
    parser.add_argument('--processed-dir', default='data/processed', help='Directory to write processed data')
    
    args = parser.parse_args()
    
    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.processed_dir, exist_ok=True)
    
    print("\n===== Shipment Anomaly Detection Demo =====\n")
    
    # Step 1: Generate sample shipment data
    print(f"Generating {args.shipments} sample shipments...")
    generator = DataGenerator(output_dir=args.output_dir)
    generator.generate_shipments(args.shipments)
    
    # Step 2: Process shipments to detect anomalies
    print("\nProcessing shipments to detect anomalies...")
    shipments_dir = os.path.join(args.output_dir, 'shipments')
    processed_dir = os.path.join(args.processed_dir, 'shipments')
    processed_count = process_shipments_directory(shipments_dir, processed_dir)
    
    # Step 3: Display summary of detected anomalies
    print(f"\nProcessed {processed_count} shipments. Analyzing results...")
    
    # Load processed shipments
    processed_file = os.path.join(processed_dir, 'shipments_processed.json')
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            processed_shipments = json.load(f)
        
        # Count anomalies by type and severity
        anomaly_types = {}
        severity_counts = {'low': 0, 'medium': 0, 'high': 0}
        shipments_with_anomalies = 0
        
        for shipment in processed_shipments:
            if shipment.get('anomalies') and len(shipment.get('anomalies', [])) > 0:
                shipments_with_anomalies += 1
                
                for anomaly in shipment.get('anomalies', []):
                    anomaly_type = anomaly.get('type', 'unknown')
                    severity = anomaly.get('severity', 'unknown')
                    
                    if anomaly_type not in anomaly_types:
                        anomaly_types[anomaly_type] = 0
                    anomaly_types[anomaly_type] += 1
                    
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        # Display summary
        print(f"\nSummary of Detected Anomalies:")
        print(f"  - Shipments with anomalies: {shipments_with_anomalies} out of {len(processed_shipments)} ({shipments_with_anomalies/len(processed_shipments)*100:.1f}%)")
        
        print("\nAnomaly Types:")
        for anomaly_type, count in anomaly_types.items():
            print(f"  - {anomaly_type}: {count}")
        
        print("\nAnomaly Severity:")
        for severity, count in severity_counts.items():
            if count > 0:
                print(f"  - {severity}: {count}")
        
        # Display sample anomalies
        print("\nSample Anomalies:")
        sample_count = 0
        for shipment in processed_shipments:
            if shipment.get('anomalies') and len(shipment.get('anomalies', [])) > 0:
                print(f"\nShipment {shipment.get('id')} ({shipment.get('status')})")
                print(f"  From: {shipment.get('origin')} To: {shipment.get('destination')}")
                print(f"  Anomalies:")
                
                for anomaly in shipment.get('anomalies', []):
                    print(f"    - {anomaly.get('type')} ({anomaly.get('severity')}): {anomaly.get('description')}")
                
                sample_count += 1
                if sample_count >= 3:  # Show at most 3 samples
                    break
    else:
        print(f"No processed shipments found at {processed_file}")
    
    print("\n===== Demo Complete =====\n")


if __name__ == "__main__":
    main()