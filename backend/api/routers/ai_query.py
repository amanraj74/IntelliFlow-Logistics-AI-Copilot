from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os

try:
    from backend.ml.rag_engine import setup_rag_pipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

class AIQuery(BaseModel):
    question: str

class AIAnswer(BaseModel):
    answer: str
    sources: List[str]
    confidence: float = 0.0

router = APIRouter()

# Mock data for demonstration
mock_driver_data = pd.DataFrame({
    'id': ['D001', 'D002', 'D003'],
    'name': ['Aman Singh', 'Priya Verma', 'Rajesh Kumar'],
    'license_number': ['PB12-3456', 'PB09-7890', 'HR05-1234'],
    'risk_score': [0.12, 0.45, 0.78]
})

mock_incident_data = pd.DataFrame({
    'id': ['I1001', 'I1002', 'I1003'],
    'driver_id': ['D001', 'D002', 'D003'],
    'description': [
        'Harsh braking detected on highway',
        'Late delivery due to traffic congestion',
        'Speed limit violation on city roads'
    ],
    'severity': ['medium', 'low', 'high']
})

mock_alert_data = pd.DataFrame({
    'id': ['A001', 'A002', 'A003'],
    'message': [
        'Driver D002 risk score increased to 0.45',
        'Multiple incidents reported for driver D003',
        'Route optimization needed for zone A deliveries'
    ]
})

def get_mock_answer(question: str) -> AIAnswer:
    """Generate mock answers based on question patterns."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['high risk', 'risky', 'dangerous']):
        high_risk_drivers = mock_driver_data[mock_driver_data['risk_score'] > 0.4]
        answer = f"High-risk drivers today: {', '.join(high_risk_drivers['name'].tolist())}. "
        answer += f"Highest risk: {high_risk_drivers.loc[high_risk_drivers['risk_score'].idxmax(), 'name']} "
        answer += f"(score: {high_risk_drivers['risk_score'].max():.2f})"
        return AIAnswer(
            answer=answer,
            sources=["drivers_db", "risk_assessment"],
            confidence=0.85
        )
    
    elif any(word in question_lower for word in ['incident', 'accident', 'violation']):
        recent_incidents = mock_incident_data.head(2)
        answer = f"Recent incidents: {len(mock_incident_data)} total. "
        answer += f"Latest: {recent_incidents.iloc[0]['description']}"
        return AIAnswer(
            answer=answer,
            sources=["incidents_db", "safety_reports"],
            confidence=0.92
        )
    
    elif any(word in question_lower for word in ['alert', 'warning', 'notification']):
        answer = f"Active alerts: {len(mock_alert_data)}. "
        answer += f"Priority: {mock_alert_data.iloc[0]['message']}"
        return AIAnswer(
            answer=answer,
            sources=["alerts_system", "monitoring"],
            confidence=0.88
        )
    
    else:
        return AIAnswer(
            answer=f"I understand you're asking about: {question}. Based on current data, I can help with driver safety, incidents, and alerts. Please be more specific.",
            sources=["general_knowledge"],
            confidence=0.60
        )

@router.post("/query", response_model=AIAnswer)
def query_ai(payload: AIQuery) -> AIAnswer:
    try:
        if not payload.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if RAG_AVAILABLE:
            # Try to use real RAG pipeline
            try:
                rag = setup_rag_pipeline(
                    mock_driver_data, 
                    mock_incident_data, 
                    mock_alert_data
                )
                results = rag.query(payload.question, k=3)
                
                # Generate answer from RAG results
                context = " ".join([r['text'] for r in results[:2]])
                answer = f"Based on current data: {context[:200]}..."
                sources = [r['id'] for r in results]
                confidence = max([r['score'] for r in results]) if results else 0.5
                
                return AIAnswer(
                    answer=answer,
                    sources=sources,
                    confidence=confidence
                )
            except Exception as e:
                print(f"RAG pipeline error: {e}")
                return get_mock_answer(payload.question)
        else:
            # Fallback to mock answers
            return get_mock_answer(payload.question)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@router.get("/status")
def ai_status():
    return {
        "rag_available": RAG_AVAILABLE,
        "model_status": "active",
        "data_sources": ["drivers", "incidents", "alerts"]
    }