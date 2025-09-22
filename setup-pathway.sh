#!/bin/bash

# IntelliFlow Logistics AI - Pathway Setup Script
# This script sets up the project with Pathway integration in WSL/Linux

echo "🚛 IntelliFlow Logistics AI - Pathway Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in WSL/Linux
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    print_error "This script must be run in WSL or Linux environment"
    print_warning "Please run this in WSL Ubuntu or Linux terminal"
    exit 1
fi

print_status "Detected Linux/WSL environment ✅"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ -z "$PYTHON_VERSION" ]]; then
    print_error "Python3 not found. Please install Python 3.8 or higher"
    exit 1
fi

print_status "Python version: $PYTHON_VERSION ✅"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv pathway_env

# Activate virtual environment
print_status "Activating virtual environment..."
source pathway_env/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
if [[ -f "requirements-pathway.txt" ]]; then
    pip install -r requirements-pathway.txt
else
    print_error "requirements-pathway.txt not found!"
    print_warning "Creating basic requirements file..."
    cat > requirements-pathway.txt << EOF
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
streamlit==1.38.0
requests==2.32.3
numpy==1.26.4
pandas==2.2.2
python-dotenv==1.0.1
pathway>=0.7.0
geopy>=2.2.0
EOF
    pip install -r requirements-pathway.txt
fi

print_status "Dependencies installed ✅"

# Create directory structure
print_status "Creating directory structure..."
mkdir -p data/streams/drivers
mkdir -p data/streams/shipments  
mkdir -p data/streams/incidents
mkdir -p data/processed
mkdir -p cache/pathway_storage
mkdir -p scripts
mkdir -p backend/pathway
mkdir -p backend/rag

print_status "Directory structure created ✅"

# Create .env file
print_status "Creating environment configuration..."
cat > .env << EOF
# IntelliFlow Logistics AI Configuration
ENVIRONMENT=development
API_PORT=9000
PATHWAY_CACHE=./cache/pathway_storage
PATHWAY_PERSISTENT_STORAGE=./data/pathway_storage
PYTHONPATH=.
DEBUG=True
EOF

# Create Streamlit secrets
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
API_BASE = "http://localhost:9000"
EOF

print_status "Configuration files created ✅"

# Test Pathway installation
print_status "Testing Pathway installation..."
python3 -c "import pathway as pw; print('Pathway version:', pw.__version__)" 2>/dev/null
if [[ $? -eq 0 ]]; then
    print_status "Pathway installation verified ✅"
else
    print_error "Pathway installation failed ❌"
    print_warning "Try: pip install --upgrade pathway"
fi

# Create startup script
print_status "Creating startup scripts..."

# Backend startup script
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting IntelliFlow Backend with Pathway..."
source pathway_env/bin/activate
export PYTHONPATH=.
export PATHWAY_CACHE=./cache/pathway_storage

# Start Pathway pipeline in background
echo "Starting Pathway streaming pipeline..."
python -m backend.pathway.streaming_pipeline &
PIPELINE_PID=$!

# Start FastAPI server
echo "Starting FastAPI server..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 9000 --reload &
API_PID=$!

echo "Backend started!"
echo "Pipeline PID: $PIPELINE_PID"
echo "API PID: $API_PID"
echo "API available at: http://localhost:9000"
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap 'kill $PIPELINE_PID $API_PID; exit' INT
wait
EOF

chmod +x start-backend.sh

# Frontend startup script  
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting IntelliFlow Frontend..."
source pathway_env/bin/activate
export PYTHONPATH=.
streamlit run frontend/dashboard.py --server.port=8501 --server.address=0.0.0.0
EOF

chmod +x start-frontend.sh

# Demo data script
cat > generate-demo.sh << 'EOF'
#!/bin/bash
echo "📊 Generating demo data..."
source pathway_env/bin/activate
export PYTHONPATH=.
python scripts/generate_demo_data.py --mode scenario
echo "Demo data generated! Check data/streams/ folder"
EOF

chmod +x generate-demo.sh

print_status "Startup scripts created ✅"

# Create test script
cat > test-setup.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing setup..."
source pathway_env/bin/activate

echo "Testing imports..."
python3 -c "
import pathway as pw
import fastapi
import streamlit
print('✅ All imports successful')
print(f'Pathway version: {pw.__version__}')
"

echo "Testing API..."
python3 -c "
from backend.api.main import create_app
app = create_app()
print('✅ API creation successful')
"

echo "✅ Setup test completed!"
EOF

chmod +x test-setup.sh

print_status "Test script created ✅"

# Run setup test
print_status "Running setup test..."
./test-setup.sh

if [[ $? -eq 0 ]]; then
    print_status "Setup completed successfully! 🎉"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Generate demo data:    ${BLUE}./generate-demo.sh${NC}"
    echo "2. Start backend:         ${BLUE}./start-backend.sh${NC}"
    echo "3. Start frontend:        ${BLUE}./start-frontend.sh${NC}"
    echo "4. Open dashboard:        ${BLUE}http://localhost:8501${NC}"
    echo ""
    echo -e "${GREEN}Docker option:${NC}"
    echo "Run with Docker:          ${BLUE}docker-compose -f docker-compose-pathway.yml up${NC}"
    echo ""
    echo -e "${GREEN}For demo video:${NC}"
    echo "1. Run all components"
    echo "2. Add files to data/streams/ folder"  
    echo "3. Watch real-time updates in dashboard"
    echo "4. Query AI copilot for insights"
    echo "=========================================="
else
    print_error "Setup test failed. Please check the logs above."
    exit 1
fi 