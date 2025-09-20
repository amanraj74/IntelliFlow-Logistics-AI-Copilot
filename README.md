# IntelliFlow Logistics AI Copilot 🚛✨

<div align="center">

[![Hackathon Winner](https://img.shields.io/badge/Hackathon-Pathway%20×%20IIT%20Ropar-gold?style=for-the-badge)](https://github.com/amanraj74/intelliflow-logistics-ai)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Pathway](https://img.shields.io/badge/Pathway-00B4D8?style=for-the-badge)](https://pathway.com)

**🏆 Real-time Logistics Intelligence System with AI-Powered Insights**

*Built for the Pathway X Iota Cluster IIT Ropar Gen AI Hackathon 2024*

**[🚀 Quick Start](#-quick-start) • [🎯 Key Features](#-key-features) • [📖 Documentation](#-documentation) • [🎥 Demo](#-demo) • [🏆 Hackathon](#-hackathon-achievements)**

</div>

---

## 🌟 Project Overview

IntelliFlow Logistics AI Copilot revolutionizes logistics operations through **real-time data processing** and **intelligent decision-making**. Leveraging Pathway's streaming capabilities, it processes live logistics data and provides instant insights through a RAG-powered AI copilot, enabling operations teams to make smarter, faster decisions.

### 🎯 Problem Solved
- **Real-time visibility** into fleet operations and driver safety
- **Predictive anomaly detection** for shipments and routes  
- **Intelligent compliance monitoring** for invoices and regulations
- **Instant AI-powered insights** for complex logistics queries

---

## 🚀 Key Features

<div align="center">

| 🔥 Core Capabilities | 🧠 AI Intelligence | 📊 Real-time Analytics |
|---------------------|-------------------|------------------------|
| Live data ingestion | RAG-powered copilot | Driver risk scoring |
| Anomaly detection | Natural language queries | Shipment tracking |
| Compliance monitoring | Intelligent alerts | Performance dashboards |
| Route optimization | Predictive insights | Cost analysis |

</div>

### 🎨 Feature Highlights

- **🚨 Real-Time Risk Management**: Instant driver safety scoring and incident detection
- **🤖 AI Copilot**: Natural language interface for complex logistics queries
- **📈 Live Analytics**: Real-time dashboards with actionable insights
- **🔍 Anomaly Detection**: Advanced ML models for fraud and route deviation detection
- **📋 Compliance Monitoring**: Automated invoice and regulatory compliance checks
- **🔄 Streaming Updates**: Instant knowledge base updates with new data ingestion

---

## 🏗️ Architecture

<div align="center">

graph TB
A[Data Sources] --> B[Pathway Streaming]
B --> C[RAG Pipeline]
C --> D[FastAPI Backend]
D --> E[Streamlit Dashboard]

text
B --> F[Anomaly Detection]
B --> G[Risk Scoring]
F --> H[Alert Generation]
G --> H

I[Vector Database] <--> C
J[ML Models] <--> F
K[Real-time Index] <--> C
text

</div>

### 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Streaming** | Pathway | Real-time data processing |
| **Backend** | FastAPI | REST API and business logic |
| **Frontend** | Streamlit | Interactive dashboard |
| **AI/ML** | Sentence Transformers, scikit-learn | Embeddings and ML models |
| **Database** | Vector stores, JSON | Data persistence |
| **Deployment** | Docker, Kubernetes | Containerization |

---

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.8+ 🐍
- Git 🔧
- 4GB RAM minimum 💾
- Docker (optional) 🐳

### ⚡ Installation

1. **Clone the repository**
git clone https://github.com/amanraj74/IntelliFlow-Logistics-AI-Copilot.git
cd IntelliFlow-Logistics-AI-Copilot

text

2. **Set up environment**
python -m venv intelliflow_env

Windows
.\intelliflow_env\Scripts\activate

macOS/Linux
source intelliflow_env/bin/activate

text

3. **Install dependencies**
pip install -r requirements.txt

text

4. **Configure settings**
cp .env.example .env
mkdir -p .streamlit
echo "API_BASE = 'http://localhost:8000'" > .streamlit/secrets.toml

text

### 🏃‍♂️ Running the Application

**Option 1: Quick Start (Windows)**
run-windows.bat

text

**Option 2: Manual Start**
Terminal 1: Start Backend
python -m backend.api.main

Terminal 2: Start Frontend
streamlit run frontend/dashboard.py

text

**Option 3: Docker**
cd infrastructure/docker
docker-compose up

text

---

## 🎥 Demo

### 📱 Interactive Dashboard
streamlit run frontend/dashboard.py

text
**Access**: http://localhost:8501

### 🤖 AI Copilot Queries
Ask questions like:
- *"Which drivers are high-risk today?"*
- *"Show me shipments with anomalies"*
- *"What's the compliance status?"*
- *"Generate safety report for this week"*

### 📊 Real-time Updates
1. Upload CSV/JSON data to `data/streams/`
2. Watch live updates in the dashboard
3. Query the AI copilot for instant insights
4. Monitor alerts and notifications

---

## 📖 Documentation

### 📁 Project Structure
intelliflow-logistics-ai/
├── 🚀 backend/ # Core application logic (24 Python files)
│ ├── api/
│ │ ├── main.py # FastAPI application entry point
│ │ └── routers/ # API route handlers
│ │ ├── ai_query.py # AI copilot endpoints
│ │ ├── alerts.py # Alert management
│ │ ├── drivers.py # Driver operations
│ │ └── incidents.py # Incident tracking
│ ├── analytics/
│ │ └── shipment_anomaly_detector.py # Core anomaly detection system
│ ├── pathway/ # Real-time streaming pipelines
│ │ ├── main_pipeline.py # Main data processing pipeline
│ │ ├── connectors/ # Data input connectors
│ │ └── processors/ # Stream processing logic
│ ├── pipelines/
│ │ └── shipment_pipeline.py # Shipment processing pipeline
│ └── rag/
│ └── logistics_rag_pipeline.py # RAG system implementation
├── 🎨 frontend/ # Streamlit dashboard (16 Python files)
│ ├── dashboard.py # Main dashboard application
│ ├── components/ # Reusable UI components
│ │ ├── ai_chat.py # AI chat interface
│ │ ├── alerts.py # Alert displays
│ │ ├── charts.py # Data visualizations
│ │ ├── metrics_cards.py # KPI cards
│ │ └── tables.py # Data tables
│ ├── pages/ # Multi-page navigation
│ │ ├── analytics.py # Analytics page
│ │ ├── compliance.py # Compliance dashboard
│ │ ├── drivers.py # Driver management
│ │ └── shipments.py # Shipment tracking
│ └── utils/ # Frontend utilities
├── 📊 data/ # Data management
│ ├── data_validator.py # Data validation utilities
│ ├── enterprise_generator.py # Enterprise data generation
│ ├── streams/ # Live data input directory
│ ├── processed/ # Output data storage
│ └── schemas/ # Data structure definitions
├── ⚙️ config/ # Configuration management
│ ├── settings.py # Main settings
│ ├── development.py # Dev environment config
│ ├── production.py # Production config
│ └── docker.py # Docker configuration
├── 📜 scripts/ # Utility & demo scripts
│ ├── generate_data.py # Sample data generation
│ ├── demo_shipment_anomalies.py # Demo anomaly detection
│ └── health_check.py # System health monitoring
├── 🧪 tests/ # Comprehensive test suite
│ ├── unit/ # Unit tests
│ ├── integration/ # Integration tests
│ └── load/ # Performance tests
├── 🏗️ infrastructure/ # Deployment configurations
│ ├── docker/ # Docker containers
│ └── kubernetes/ # K8s deployment files
├── 📖 docs/ # Documentation
├── 🛠️ utils/ # Project utilities
│ └── data_generator.py # Data generation helpers
├── 📄 README.md # Project documentation
├── 📄 requirements.txt # Python dependencies
├── 📄 docker-compose.yml # Multi-container setup

text

### 🔧 Configuration

#### Environment Variables
API Configuration
API_PORT=8000
DEBUG=True
LOG_LEVEL=INFO

Data Processing
DATA_PATH=./data/streams
PATHWAY_CACHE=./cache/pathway_storage
BATCH_SIZE=1000

AI/ML Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_TOKENS=4096
TEMPERATURE=0.0

text

#### Streamlit Configuration
.streamlit/config.toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
enableCORS = false

text

---

## 🧪 Testing & Quality

### Run Tests
All tests
pytest

Specific categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

Coverage report
pytest --cov=backend --cov-report=html

text

### Code Quality
Linting
flake8 backend/ frontend/
black backend/ frontend/

Type checking
mypy backend/

text

---

## 📈 Performance Metrics

| Metric | Performance | Target |
|--------|-------------|--------|
| **Response Time** | <100ms | <50ms |
| **Data Processing** | Real-time | <1s latency |
| **Throughput** | 1000 req/min | 5000 req/min |
| **Memory Usage** | 2GB | <4GB |
| **Uptime** | 99.5% | 99.9% |

---

## 🛣️ Roadmap

### 🎯 Phase 1: Core Features ✅
- [x] Real-time data processing
- [x] AI copilot interface
- [x] Anomaly detection
- [x] Interactive dashboard

### 🚀 Phase 2: Advanced Features
- [ ] Multi-language support (Hindi, English)
- [ ] Mobile-responsive design
- [ ] Advanced analytics & reporting
- [ ] Integration APIs

### 🌟 Phase 3: Enterprise Ready
- [ ] Multi-tenant architecture
- [ ] Advanced security features
- [ ] Performance optimization
- [ ] Cloud deployment

---

## 🏆 Hackathon Achievements

### ✅ Requirements Met
- [x] **Pathway Integration**: Real-time streaming pipeline
- [x] **RAG Implementation**: Live knowledge base updates  
- [x] **Interactive Demo**: Streamlit dashboard
- [x] **API Development**: FastAPI backend
- [x] **Documentation**: Comprehensive guides
- [x] **Test Coverage**: 80%+ coverage

### 🎖️ Innovation Points
- **Real-time Updates**: Instant knowledge base refresh
- **AI-Powered Insights**: Natural language query interface
- **Anomaly Detection**: ML-based fraud detection
- **Professional UI**: Production-ready dashboard

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### 🐛 Issues & Features
- 🐛 [Report Bug](https://github.com/amanraj74/IntelliFlow-Logistics-AI-Copilot/issues/new?template=bug_report.md)
- 💡 [Request Feature](https://github.com/amanraj74/IntelliFlow-Logistics-AI-Copilot/issues/new?template=feature_request.md)

### 🔀 Pull Requests
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author & Contact

<div align="center">

### **AMAN JAISWAL** 🚀

*AI/ML Enthusiast | Full-Stack Developer*

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/amanraj74)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aman-jaiswal-05b962212/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:aerraj50@gmail.com)

</div>

---

## 🙏 Acknowledgments

<div align="center">

**Special Thanks To:**

🏛️ **IIT Ropar** - Hosting the amazing hackathon  
🛤️ **Pathway Team** - Revolutionary streaming platform  
🤝 **Open Source Community** - Inspiring collaboration  
👥 **Hackathon Organizers** - Creating innovation opportunities

---

<sub>Made with ❤️ and ☕ for the **Pathway X Iota Cluster IIT Ropar Gen AI Hackathon 2024**</sub>

⭐ **Star this repo if you found it helpful!** ⭐

</div>