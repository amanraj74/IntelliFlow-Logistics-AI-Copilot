from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
from typing import List, Dict, Any, Optional
import pandas as pd

class RAGEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize RAG engine with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents: Dict[str, str] = {}
        self.embeddings: Optional[np.ndarray] = None
        self.doc_ids: List[str] = []

    def process_documents(self, documents: pd.DataFrame) -> None:
        """Process documents and create embeddings."""
        # Store original documents
        self.documents = dict(zip(documents['id'], documents['text']))
        self.doc_ids = list(documents['id'])
        
        # Generate embeddings
        texts = documents['text'].tolist()
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build index
        self.build_index()

    def build_index(self) -> None:
        """Build KNN index for document embeddings."""
        if self.embeddings is None:
            raise RuntimeError("No embeddings found. Process documents first.")
            
        self.index = NearestNeighbors(
            n_neighbors=5,
            metric='cosine'
        ).fit(self.embeddings)

    def query(self, question: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query the RAG engine with a question."""
        if not self.index or self.embeddings is None:
            raise RuntimeError("Index not built. Process documents first.")
            
        # Get question embedding
        query_embedding = self.model.encode([question])[0].reshape(1, -1)
        
        # Query the index
        distances, indices = self.index.kneighbors(
            query_embedding,
            n_neighbors=k
        )
        
        # Convert distances to similarities (cosine distance to similarity)
        similarities = 1 - distances[0]
        
        # Format results
        return [
            {
                "id": self.doc_ids[idx],
                "text": self.documents[self.doc_ids[idx]],
                "score": float(score)
            }
            for idx, score in zip(indices[0], similarities)
        ]

def setup_rag_pipeline(
    driver_data: pd.DataFrame,
    incident_data: pd.DataFrame,
    alert_data: pd.DataFrame,
    model_name: str = "all-MiniLM-L6-v2"
) -> RAGEngine:
    """Set up RAG pipeline for logistics data."""
    rag = RAGEngine(model_name=model_name)
    
    # Prepare documents from each data source
    driver_docs = pd.DataFrame({
        'id': ['driver_' + str(x) for x in driver_data['id']],
        'text': driver_data.apply(
            lambda row: f"Driver {row['name']} (ID: {row['id']}) has "
                      f"license number {row['license_number']} and "
                      f"risk score {row['risk_score']}", 
            axis=1
        )
    })
    
    incident_docs = pd.DataFrame({
        'id': ['incident_' + str(x) for x in incident_data['id']],
        'text': incident_data.apply(
            lambda row: f"Incident {row['id']} involving driver "
                      f"{row['driver_id']}: {row['description']} "
                      f"(Severity: {row['severity']})",
            axis=1
        )
    })
    
    alert_docs = pd.DataFrame({
        'id': ['alert_' + str(x) for x in alert_data['id']],
        'text': alert_data['message']
    })
    
    # Combine all documents
    all_docs = pd.concat([driver_docs, incident_docs, alert_docs])
    
    # Process documents and build index
    rag.process_documents(all_docs)
    
    return rag