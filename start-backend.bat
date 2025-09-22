@echo off
echo 🚀 Starting IntelliFlow Backend with Pathway...

REM Activate virtual environment
call pathway_env\Scripts\activate

REM Set Python path
set PYTHONPATH=.
set PATHWAY_CACHE=.\cache\pathway_storage

REM Start Pathway pipeline in new window
start "Pathway Pipeline" cmd /k python -m backend.pathway.streaming_pipeline

REM Start FastAPI server in new window
start "FastAPI Server" cmd /k uvicorn backend.api.main:app --host 0.0.0.0 --port 9000 --reload

echo Backend started!
echo API available at: http://localhost:9000
pause
