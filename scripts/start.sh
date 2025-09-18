#!/bin/bash

# Start the FastAPI backend
python -m backend.api.main &

# Start the Streamlit frontend
streamlit run frontend/dashboard.py