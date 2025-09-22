

## 🚀 Pathway Integration (NEW)

### Real-time Streaming with Pathway

This project now includes Pathway integration for real-time data processing:

#### Quick Start with Pathway (WSL/Linux)
```bash
# 1. Setup (one-time)
chmod +x setup-pathway.sh
./setup-pathway.sh

# 2. Generate demo data
./generate-demo.sh

# 3. Start backend (Pathway + API)
./start-backend.sh

# 4. Start frontend
./start-frontend.sh

# 5. Open dashboard
open http://localhost:8501
```

#### Docker with Pathway
```bash
docker-compose -f docker-compose-pathway.yml up --build
```

#### Real-time Demo
1. Start all services
2. Add CSV/JSON files to `data/streams/` folders
3. Watch dashboard update automatically
4. Query AI copilot for real-time insights

### Architecture
```
Data Files → Pathway Streaming → Vector Store → AI Copilot
     ↓              ↓               ↓            ↓
Live Updates   Real-time ETL   Dynamic Index  Live Responses
```

**Requirements Met:**
- ✅ Pathway-powered streaming ETL
- ✅ Dynamic indexing (no rebuilds)
- ✅ Live retrieval/generation interface
- ✅ Real-time updates (T+0 to T+1)

