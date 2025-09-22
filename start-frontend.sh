#!/bin/bash
echo "🎨 Starting IntelliFlow Frontend..."
source pathway_env/bin/activate
export PYTHONPATH=.
streamlit run frontend/dashboard.py --server.port=8502 --server.address=0.0.0.0
