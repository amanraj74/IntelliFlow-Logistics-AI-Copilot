#!/bin/bash
echo "📊 Generating demo data..."
source pathway_env/bin/activate
export PYTHONPATH=.
python scripts/generate_demo_data.py --mode scenario
echo "Demo data generated! Check data/streams/ folder"
