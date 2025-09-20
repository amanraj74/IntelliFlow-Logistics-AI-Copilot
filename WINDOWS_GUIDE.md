# Windows Setup Guide for IntelliFlow Logistics AI

This guide provides step-by-step instructions for setting up and running the IntelliFlow Logistics AI project on Windows.

## Prerequisites

- **Python 3.8+**: [Download from python.org](https://www.python.org/downloads/)
- **Git**: [Download from git-scm.com](https://git-scm.com/download/win)
- **Visual Studio Code** (recommended): [Download from code.visualstudio.com](https://code.visualstudio.com/download)

## Step 1: Clone the Repository

1. Open Command Prompt or PowerShell
2. Navigate to the directory where you want to clone the project
3. Run the following command:
   ```
   git clone https://github.com/yourusername/intelliflow-logistics-ai.git
   cd intelliflow-logistics-ai
   ```

## Step 2: Set Up Python Environment

1. Create a virtual environment:
   ```
   python -m venv intelliflow_env
   ```

2. Activate the virtual environment:
   ```
   .\intelliflow_env\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Step 3: Fix Windows-Specific Issues

Run the included Windows fix script:
```
fix-windows.bat
```

This script will:
- Create necessary directories
- Set up the Streamlit configuration
- Generate sample data files

## Step 4: Running the Application

### Option 1: Run Services Separately

1. Start the Backend API (keep this terminal window open):
   ```
   python -m backend.api.main
   ```

2. Open a new Command Prompt or PowerShell window, activate the virtual environment, and start the Frontend Dashboard:
   ```
   .\intelliflow_env\Scripts\activate
   streamlit run frontend/dashboard.py
   ```

3. Open your browser and navigate to:
   - Frontend Dashboard: http://localhost:8501
   - Backend API Documentation: http://localhost:8000/docs

### Option 2: Run Demo Scripts

To test the shipment anomaly detection feature:
```
python scripts/demo_shipment_anomalies.py --shipments 20
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in the command: `python -m backend.api.main --port 8001`
   - For Streamlit: `streamlit run frontend/dashboard.py --server.port 8502`

2. **Module Not Found Errors**
   - Ensure you've activated the virtual environment
   - Try reinstalling dependencies: `pip install -r requirements.txt`

3. **Data Directory Issues**
   - Run `fix-windows.bat` again to recreate necessary directories

4. **Streamlit Configuration Error**
   - Manually create the `.streamlit/secrets.toml` file with the content: `API_BASE = "http://localhost:8000"`

## Next Steps

- Explore the dashboard at http://localhost:8501
- Try the shipment anomaly detection feature
- Check out the documentation in the `docs` folder

For more detailed information, refer to the main [README.md](README.md) file.