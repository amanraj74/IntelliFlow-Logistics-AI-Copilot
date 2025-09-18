#!/bin/bash

# IntelliFlow Logistics AI - Quick Start Script
# This script sets up and runs the entire application

set -e  # Exit on any error

echo "🚛 IntelliFlow Logistics AI - Quick Start"
echo "========================================"

# Check if we're in WSL or Linux
if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
    echo "✅ Running in WSL"
    PLATFORM="wsl"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Running on Linux"
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Running on macOS"
    PLATFORM="macos"
else
    echo "⚠️  Unknown platform: $OSTYPE"
    PLATFORM="unknown"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
echo "🐍 Checking Python installation..."
if command_exists python3.11; then
    PYTHON_CMD="python3.11"
elif command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "intelliflow_env" ]; then
    echo "🔨 Creating virtual environment..."
    $PYTHON_CMD -m venv intelliflow_env
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source intelliflow_env/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/streams/drivers data/streams/incidents data/streams/vehicles
mkdir -p data/output/alerts data/output/driver_analytics data/output/processed_incidents
mkdir -p cache/pathway_storage
mkdir -p .streamlit

# Setup environment files
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "DEBUG=True" > .env
fi

# Setup Streamlit config
echo 'API_BASE = "http://localhost:8000"' > .streamlit/secrets.toml

# Create sample data if not exists
echo "📝 Creating sample data..."
if [ ! -f "data/streams/drivers/drivers.csv" ]; then
    cat > data/streams/drivers/drivers.csv << 'EOF'
id,name,license_number,risk_score
D001,Aman Singh,PB12-3456,0.12
D002,Priya Verma,PB09-7890,0.45
D003,Rajesh Kumar,HR05-1234,0.78
D004,Sunita Devi,UP14-5678,0.25
D005,Mohammed Ali,MH20-9012,0.82
EOF
fi

if [ ! -f "data/streams/incidents/incidents.csv" ]; then
    cat > data/streams/incidents/incidents.csv << 'EOF'
id,driver_id,date,severity,description,location
I1001,D001,2024-09-15,medium,Harsh braking detected on highway,Highway NH-1
I1002,D002,2024-09-16,low,Late delivery due to traffic congestion,Delhi NCR
I1003,D003,2024-09-17,high,Speed limit violation on city roads,Mumbai
I1004,D005,2024-09-18,high,Aggressive driving behavior reported,Bangalore
I1005,D004,2024-09-19,low,Minor route deviation,Chandigarh
EOF
fi

# Test installation
echo "🧪 Testing installation..."
$PYTHON_CMD -c "import fastapi, streamlit, pathway; print('✅ All main packages imported successfully')"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   Terminal 1: $PYTHON_CMD -m backend.api.main"
echo "   Terminal 2: streamlit run frontend/dashboard.py"
echo ""
echo "🌐 Access URLs:"
echo "   Dashboard: http://localhost:8501"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/health"
echo ""

# Ask if user wants to start the services
read -p "🤖 Would you like to start the services now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting services..."
    
    # Start API in background
    echo "🔧 Starting API server..."
    $PYTHON_CMD -m backend.api.main &
    API_PID=$!
    
    # Wait a moment for API to start
    sleep 3
    
    # Test API
    echo "🔍 Testing API connection..."
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is running!"
    else
        echo "⚠️  API might still be starting..."
    fi
    
    echo "🎨 Starting Streamlit dashboard..."
    echo "   Press Ctrl+C to stop both services"
    
    # Start Streamlit (this will run in foreground)
    streamlit run frontend/dashboard.py
    
    # Kill API when Streamlit stops
    echo "🛑 Stopping services..."
    kill $API_PID 2>/dev/null || true
    
else
    echo "👍 Services not started. Run them manually when ready!"
fi

echo "✨ Done!"