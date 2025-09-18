# IntelliFlow Logistics AI Copilot

## Hackathon Track
**Track 3: Logistics Pulse Copilot**  
Pathway X Iota Cluster IIT Ropar Gen AI Hackathon

---

## Project Overview
A real-time RAG application for logistics, powered by Pathway, FastAPI, and Streamlit. It ingests live data, updates its knowledge base instantly, and provides actionable insights for logistics teams.

---

## Features
- **Driver Safety & Risk Management**: Flags high-risk drivers as new incidents are ingested.
- **Invoice & Payment Compliance**: Monitors invoices for compliance, updating recommendations as new documents arrive.
- **Shipment Anomaly & Fraud Detection**: Detects route deviations and suspicious shipment activity in real time.
- **Live RAG Pipeline**: Combines vector and keyword search for up-to-date answers.
- **Interactive Dashboard**: Query the AI copilot, view alerts, and monitor driver status.

---

## Architecture
- **Pathway**: Streaming ETL, live indexing, RAG pipeline
- **FastAPI**: Backend API for data and AI queries
- **Streamlit**: Frontend dashboard for user interaction
- **Docker**: Optional containerization for deployment

---

## File Structure
```
intelliflow-logistics-ai/
├── backend/
│   ├── api/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── drivers.py
│   │   │   ├── incidents.py
│   │   │   ├── alerts.py
│   │   │   ├── ai_query.py
│   ├── database/
│   ├── ml/
│   ├── pathway/
│   ├── services/
├── frontend/
│   ├── dashboard.py
│   ├── components/
│   ├── pages/
│   ├── utils/
├── data/
│   ├── streams/
│   ├── output/
│   ├── schemas/
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── terraform/
├── tests/
├── scripts/
├── config/
├── docs/
├── .streamlit/
│   └── secrets.toml
├── README.md
├── HACKATHON_DEMO.md
├── PRESENTATION.md
```

---

## Demo Flow
1. Start backend API: `python -m backend.api.main`
2. Start dashboard: `streamlit run frontend/dashboard.py`
3. Upload or edit a CSV/PDF in `data/streams/`
4. Ask a query in the dashboard (e.g., "Which drivers are high-risk today?")
5. Change the data (e.g., add a new incident for a driver)
6. Ask the same query again—see the answer update instantly!
7. Show alerts and compliance checks in real time

---

## Hackathon Requirements Checklist
- [x] Real-time updates with Pathway
- [x] RAG pipeline for live answers
- [x] Streamlit dashboard for queries
- [x] API endpoints for drivers, incidents, alerts, AI
- [x] Demo video (to be added)

---

## About Me
Solo developer, GenAI enthusiast, and hackathon participant.

---

## Contact
- [LinkedIn](#)
- [GitHub](#)
