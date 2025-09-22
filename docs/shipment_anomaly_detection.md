# Shipment Anomaly Detection

> **Quick Links**: [Step-by-Step Guide](guides/shipment_anomaly_detection_guide.md) | [API Documentation](api/endpoints.md) | [Dashboard Guide](user_guides/dashboard_guide.md)

## Overview

The Shipment Anomaly Detection system is designed to identify unusual patterns, potential issues, and suspicious activities in shipment data. This system helps logistics managers proactively address problems before they impact delivery timelines or customer satisfaction.

## Features

- **Multi-format Support**: Process both JSON and CSV shipment data files
- **Anomaly Detection Types**:
  - Route deviations from optimal paths
  - Unusual stops or unplanned locations
  - Speed violations (too fast or too slow)
  - Potential fraud indicators
  - Delivery delays
  - Temperature breaches for sensitive cargo
- **Severity Classification**: Anomalies are classified as low, medium, or high severity
- **Batch Processing**: Process entire directories of shipment files
- **Robust Error Handling**: Handles encoding issues and malformed data

## Usage

### Command Line Interface

Process a directory of shipment files:

```bash
python backend/analytics/shipment_anomaly_detector.py --input data/streams/shipments --output data/processed/shipments
```

Process a single shipment file:

```bash
python backend/analytics/shipment_anomaly_detector.py --file data/streams/shipments/shipment.json --output data/processed/shipments
```

### Demo Script

Run the demo script to see the complete workflow in action:

```bash
python scripts/demo_shipment_anomalies.py --shipments 20
```

This script:
1. Generates sample shipment data
2. Processes shipments to detect anomalies
3. Displays a summary of detected anomalies

## Implementation Details

### ShipmentAnomalyDetector Class

The core of the anomaly detection system is the `ShipmentAnomalyDetector` class in `backend/analytics/shipment_anomaly_detector.py`. This class:

- Loads historical shipment data to establish baseline thresholds
- Provides methods to detect various types of anomalies
- Returns detailed anomaly information with severity levels

### Data Processing Flow

1. **Input Processing**: Handles both JSON and CSV files with robust error handling
2. **Anomaly Detection**: Applies multiple detection algorithms to identify issues
3. **Result Generation**: Creates structured output with anomaly details
4. **Output Storage**: Saves processed results as JSON files

## Integration Points

- **Frontend Dashboard**: Anomaly results can be displayed in the logistics dashboard
- **Alert System**: High-severity anomalies can trigger alerts to logistics managers
- **Analytics Pipeline**: Results can feed into broader analytics systems

## Future Enhancements

- Machine learning models for more sophisticated anomaly detection
- Real-time processing using streaming data
- Integration with external data sources (weather, traffic, etc.)
- Customizable thresholds and detection rules