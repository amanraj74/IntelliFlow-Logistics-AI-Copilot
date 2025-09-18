"""Example usage of RAG engine for logistics data."""
import pandas as pd
from backend.ml.rag_engine import setup_rag_pipeline

def load_sample_data():
    """Load sample data for demonstration."""
    # Sample drivers data
    drivers = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
        'license_number': ['DL123', 'DL456', 'DL789'],
        'risk_score': [0.8, 0.2, 0.5]
    })
    
    # Sample incidents data
    incidents = pd.DataFrame({
        'id': [1, 2],
        'driver_id': [1, 3],
        'description': [
            'Late delivery due to heavy traffic',
            'Package damaged during unloading'
        ],
        'severity': ['low', 'medium']
    })
    
    # Sample alerts data
    alerts = pd.DataFrame({
        'id': [1, 2, 3],
        'message': [
            'High risk driver John Doe requires attention',
            'Route optimization needed for delivery zone A',
            'Vehicle maintenance overdue for truck T123'
        ]
    })
    
    return drivers, incidents, alerts

def main():
    """Run RAG engine demonstration."""
    # Load sample data
    print("Loading sample data...")
    drivers, incidents, alerts = load_sample_data()
    
    # Initialize RAG pipeline
    print("\nInitializing RAG engine...")
    rag = setup_rag_pipeline(drivers, incidents, alerts)
    
    # Example queries
    example_queries = [
        "high risk drivers",
        "late deliveries",
        "maintenance issues",
        "driver performance",
    ]
    
    print("\nTesting example queries:")
    for query in example_queries:
        print(f"\nQuery: {query}")
        results = rag.query(query)
        
        print("Top 3 relevant documents:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['score']:.3f}")
            print(f"   Document: {result['text']}")

if __name__ == "__main__":
    main()