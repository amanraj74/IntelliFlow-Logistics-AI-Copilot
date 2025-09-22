#!/bin/bash
echo "🧪 Testing setup..."
source pathway_env/bin/activate

echo "Testing imports..."
python3 -c "
import pathway as pw
import fastapi
import streamlit
print('✅ All imports successful')
print(f'Pathway version: {pw.__version__}')
"

echo "Testing API..."
python3 -c "
from backend.api.main import create_app
app = create_app()
print('✅ API creation successful')
"

echo "✅ Setup test completed!"
