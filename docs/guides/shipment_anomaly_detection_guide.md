# Step-by-Step Guide: Shipment Anomaly Detection

This guide provides detailed instructions on how to use the Shipment Anomaly Detection system in the IntelliFlow Logistics AI platform.

## Prerequisites

- Python 3.8+
- IntelliFlow Logistics AI environment set up (see main README.md)
- Required packages installed via `pip install -r requirements.txt`

## Quick Start

The fastest way to see the system in action is to run the demo script:

```bash
python scripts/demo_shipment_anomalies.py --shipments 20
```

This will:
1. Generate 20 sample shipment records
2. Process them to detect anomalies
3. Display a summary of detected anomalies

## Detailed Usage Guide

### 1. Generate Sample Data (Optional)

If you don't have existing shipment data, you can generate sample data:

```bash
python -c "from utils.data_generator import DataGenerator; generator = DataGenerator(output_dir='data/streams'); generator.generate_shipments(30)"
```

This will create sample shipment data in both CSV and JSON formats in the `data/streams/shipments` directory.

### 2. Process Shipment Data

#### Process a Directory of Shipment Files

```bash
python backend/analytics/shipment_anomaly_detector.py --input data/streams/shipments --output data/processed/shipments
```

This will process all shipment files (both JSON and CSV) in the input directory and save the results to the output directory.

#### Process a Single Shipment File

```bash
python backend/analytics/shipment_anomaly_detector.py --file data/streams/shipments/shipment.json --output data/processed/shipments
```

### 3. View and Analyze Results

The processed results are stored as JSON files in the output directory. You can view them using any text editor or JSON viewer.

For a quick summary of the anomalies, you can use the following command:

```bash
python -c "import json; f = open('data/processed/shipments/shipments_processed.json'); data = json.load(f); anomalies = sum(1 for s in data if s.get('anomalies') and len(s.get('anomalies', [])) > 0); print(f'Shipments with anomalies: {anomalies} out of {len(data)} ({anomalies/len(data)*100:.1f}%)')"
```

## Integrating with the Dashboard

The anomaly detection results can be integrated with the main dashboard:

1. Start the backend API:
   ```bash
   python -m backend.api.main
   ```

2. Start the frontend dashboard:
   ```bash
   streamlit run frontend/dashboard.py
   ```

3. Navigate to the Shipment Analytics section to view anomaly detection results.

## Customizing Anomaly Detection

To customize the anomaly detection logic, you can modify the `ShipmentAnomalyDetector` class in `backend/analytics/shipment_anomaly_detector.py`.

Key methods that can be customized:

- `detect_anomalies`: Main method that orchestrates anomaly detection
- `_detect_route_deviations`: Detects deviations from planned routes
- `_detect_unusual_stops`: Identifies unplanned or suspicious stops
- `_detect_speed_violations`: Flags unusually fast or slow segments
- `_detect_potential_fraud`: Identifies potential fraudulent activities
- `_detect_delays`: Detects shipments that are behind schedule
- `_detect_temperature_breaches`: Monitors temperature for sensitive cargo

## Troubleshooting

### Common Issues

1. **File Encoding Issues**
   
   If you encounter encoding errors with CSV files, try specifying the encoding:
   ```bash
   python backend/analytics/shipment_anomaly_detector.py --input data/streams/shipments --output data/processed/shipments --encoding latin1
   ```

2. **Missing Dependencies**
   
   Ensure all required packages are installed:
   ```bash
   pip install pandas numpy geopy
   ```

3. **No Anomalies Detected**
   
   Check that your data contains potential anomalies. You can modify the thresholds in the detector class to make it more or less sensitive.

## Next Steps

- Implement real-time anomaly detection using Pathway
- Connect anomaly detection to alert systems
- Train machine learning models for more sophisticated detection
- Integrate with external data sources (weather, traffic, etc.)