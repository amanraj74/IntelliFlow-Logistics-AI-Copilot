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
