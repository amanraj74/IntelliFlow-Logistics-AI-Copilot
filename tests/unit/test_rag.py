import pytest
import pandas as pd
import numpy as np
from backend.ml.rag_engine import RAGEngine, setup_rag_pipeline

def test_rag_engine_setup():
    """Test RAG engine setup and basic functionality."""
    # Sample test data
    driver_data = pd.DataFrame({
        'id': [1, 2],
        'name': ['John Doe', 'Jane Smith'],
        'license_number': ['DL123', 'DL456'],
        'risk_score': [0.8, 0.2]
    })
    
    incident_data = pd.DataFrame({
        'id': [1],
        'driver_id': [1],
        'description': 'Late delivery',
        'severity': 'low'
    })
    
    alert_data = pd.DataFrame({
        'id': [1],
        'message': 'High risk driver detected'
    })
    
    # Initialize RAG pipeline
    rag = setup_rag_pipeline(driver_data, incident_data, alert_data)
    
    # Test querying
    results = rag.query("high risk driver")
    
    assert len(results) == 3, "Should return top 3 results"
    assert all(isinstance(r['id'], str) for r in results), "All IDs should be strings"
    assert all(isinstance(r['text'], str) for r in results), "All texts should be strings"
    assert all(isinstance(r['score'], float) for r in results), "All scores should be floats"
    assert all(0 <= r['score'] <= 1 for r in results), "Scores should be between 0 and 1"

def test_rag_engine_empty_data():
    """Test RAG engine with empty data."""
    empty_df = pd.DataFrame({'id': [], 'text': []})
    
    # Initialize RAG engine directly
    rag = RAGEngine()
    
    with pytest.raises(RuntimeError):
        # Should raise error when querying without processing documents
        rag.query("test query")

def test_rag_engine_custom_k():
    """Test RAG engine with custom number of results."""
    # Sample data
    data = pd.DataFrame({
        'id': ['1', '2', '3', '4', '5'],
        'text': [
            'High risk driver warning',
            'Delivery delayed by traffic',
            'Route optimization needed',
            'Vehicle maintenance alert',
            'Driver performance review'
        ]
    })
    
    # Initialize RAG engine
    rag = RAGEngine()
    rag.process_documents(data)
    
    # Test with different k values
    results_2 = rag.query("driver", k=2)
    results_4 = rag.query("driver", k=4)
    
    assert len(results_2) == 2, "Should return exactly 2 results"
    assert len(results_4) == 4, "Should return exactly 4 results"
    
    # Check scores are sorted
    assert all(results_2[i]['score'] >= results_2[i+1]['score'] 
              for i in range(len(results_2)-1)), "Results should be sorted by score"