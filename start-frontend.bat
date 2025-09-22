@echo off
echo 🎨 Starting IntelliFlow Frontend...

REM Activate virtual environment
call pathway_env\Scripts\activate

REM Set Python path
set PYTHONPATH=.

REM Run Streamlit
streamlit run frontend\dashboard.py --server.port=8502 --server.address=0.0.0.0
