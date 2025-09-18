# Hackathon Demo Guide

## Demo Steps
1. Start backend API: `python -m backend.api.main`
2. Start dashboard: `streamlit run frontend/dashboard.py`
3. Upload or edit a CSV/PDF in `data/streams/`
4. Ask a query in the dashboard (e.g., "Which drivers are high-risk today?")
5. Change the data (e.g., add a new incident for a driver)
6. Ask the same query again—see the answer update instantly!
7. Show alerts and compliance checks in real time

## Checklist
- [x] Real-time updates with Pathway
- [x] RAG pipeline for live answers
- [x] Streamlit dashboard for queries
- [x] API endpoints for drivers, incidents, alerts, AI
- [x] Demo video (to be added)

## Tips
- Show "before/after" data change in your demo
- Keep the interface clean and simple
- Document your steps for judges
