# IntelliFlow Logistics AI - Beginner's Guide

Welcome to IntelliFlow Logistics AI! This guide will help you understand the project structure, features, and how to get started.

## Project Overview

IntelliFlow Logistics AI is a real-time logistics intelligence system that helps logistics companies monitor their operations, detect anomalies, and make data-driven decisions. The system processes data from various sources (drivers, vehicles, shipments, incidents) and provides insights through an interactive dashboard.

## Key Features

1. **Real-Time Dashboard**: View logistics data and metrics in real-time
2. **Shipment Anomaly Detection**: Automatically detect issues with shipments
3. **Driver Risk Assessment**: Monitor driver behavior and risk scores
4. **AI-Powered Chat**: Ask questions about your logistics data
5. **Interactive Maps**: Visualize routes and incidents geographically

## Project Structure

- **backend/**: API and data processing logic
  - **api/**: FastAPI endpoints
  - **analytics/**: Data analysis modules
  - **models/**: Data models and schemas
  - **services/**: Business logic services

- **frontend/**: Streamlit dashboard and UI components
  - **components/**: Reusable UI components
  - **dashboard.py**: Main dashboard application

- **data/**: Data storage and processing
  - **streams/**: Input data streams (CSV, JSON)
  - **processed/**: Processed data outputs
  - **schemas/**: Data validation schemas

- **scripts/**: Utility scripts for demos and data generation

- **docs/**: Documentation and guides

## Getting Started

### For Windows Users

The easiest way to get started is to use our Windows scripts:

1. Run `fix-windows.bat` to set up the necessary directories and configurations
2. Run `run-windows.bat` to start both the backend and frontend services

For more detailed instructions, see [WINDOWS_GUIDE.md](../WINDOWS_GUIDE.md).

### Understanding the Data Flow

1. **Data Ingestion**: Raw data enters through the `data/streams` directory
2. **Processing**: Backend services process and analyze the data
3. **Storage**: Processed results are stored in `data/processed`
4. **Visualization**: The frontend dashboard displays insights from the processed data

## Key Features Explained

### Shipment Anomaly Detection

The system can detect various anomalies in shipment data, including:
- Delays
- Route deviations
- Hazardous material issues

To try this feature:
```
python scripts/demo_shipment_anomalies.py --shipments 20
```

### AI-Powered Chat

The dashboard includes a chat interface where you can ask questions about your logistics data. For example:
- "Which drivers have the highest risk scores?"
- "Show me delayed shipments from last week"
- "What's the average delivery time for route X?"

## Next Steps

Once you're familiar with the basic features, you can:

1. **Explore the Dashboard**: Navigate through different tabs and visualizations
2. **Run Demo Scripts**: Try the various demo scripts in the `scripts` directory
3. **Review Documentation**: Check out the detailed documentation in the `docs` directory
4. **Modify Data**: Try changing the input data to see how the system responds

## Troubleshooting

If you encounter issues:

1. Check that both the backend and frontend services are running
2. Ensure all required directories exist (run `fix-windows.bat` if needed)
3. Check the console output for error messages
4. Restart the services if necessary

## Getting Help

If you need further assistance, check the following resources:
- Documentation in the `docs` directory
- Comments in the source code
- Issue tracker on the project repository