from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd

# Remove all ML imports - using pure Python approach
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

def analyze_question(question: str) -> Dict[str, Any]:
    """Analyze question and generate intelligent response."""
    question_lower = question.lower()
    
    # High-risk driver queries
    if any(word in question_lower for word in ['high risk', 'risky', 'dangerous', 'unsafe']):
        high_risk_drivers = mock_driver_data[mock_driver_data['risk_score'] > 0.4]
        if not high_risk_drivers.empty:
            highest_risk = high_risk_drivers.loc[high_risk_drivers['risk_score'].idxmax()]
            answer = f"🚨 High-risk drivers identified: {len(high_risk_drivers)} total.\n\n"
            answer += f"**Highest Risk:** {highest_risk['name']} (ID: {highest_risk['id']})\n"
            answer += f"**Risk Score:** {highest_risk['risk_score']:.2f}\n"
            answer += f"**License:** {highest_risk['license_number']}\n\n"
            
            if len(high_risk_drivers) > 1:
                others = high_risk_drivers[high_risk_drivers['id'] != highest_risk['id']]
                answer += f"**Other high-risk drivers:**\n"
                for _, driver in others.iterrows():
                    answer += f"• {driver['name']} (Risk: {driver['risk_score']:.2f})\n"
            
            answer += "\n💡 **Recommendation:** Schedule immediate safety training and closer monitoring."
            
            return {
                "answer": answer,
                "sources": ["driver_risk_db", "safety_monitoring_system"],
                "confidence": 0.92
            }
    
    # Incident-related queries
    elif any(word in question_lower for word in ['incident', 'accident', 'violation', 'problem']):
        high_severity = mock_incident_data[mock_incident_data['severity'] == 'high']
        answer = f"📋 **Incident Analysis:**\n\n"
        answer += f"**Total Incidents:** {len(mock_incident_data)}\n"
        answer += f"**High Severity:** {len(high_severity)}\n\n"
        
        answer += "**Recent Incidents:**\n"
        for _, incident in mock_incident_data.head(3).iterrows():
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            answer += f"{severity_icon.get(incident['severity'], '⚪')} **{incident['severity'].title()}:** {incident['description']}\n"
        
        if len(high_severity) > 0:
            answer += f"\n⚠️ **Action Required:** {len(high_severity)} high-severity incidents need immediate attention."
        
        return {
            "answer": answer,
            "sources": ["incident_management_system", "safety_reports"],
            "confidence": 0.88
        }
    
    # Alert queries
    elif any(word in question_lower for word in ['alert', 'warning', 'notification', 'urgent']):
        answer = f"🚨 **Active Alerts Summary:**\n\n"
        answer += f"**Total Active Alerts:** {len(mock_alert_data)}\n\n"
        
        for i, (_, alert) in enumerate(mock_alert_data.head(3).iterrows(), 1):
            answer += f"**{i}.** {alert['message']}\n"
        
        answer += f"\n📊 **Alert Distribution:**\n"
        answer += f"• Safety Alerts: 2\n"
        answer += f"• Operational Alerts: 1\n"
        answer += f"• System Alerts: 0\n"
        
        return {
            "answer": answer,
            "sources": ["alert_management_system", "real_time_monitoring"],
            "confidence": 0.85
        }
    
    # Driver performance queries
    elif any(word in question_lower for word in ['performance', 'best', 'worst', 'driver', 'score']):
        best_driver = mock_driver_data.loc[mock_driver_data['risk_score'].idxmin()]
        worst_driver = mock_driver_data.loc[mock_driver_data['risk_score'].idxmax()]
        avg_score = mock_driver_data['risk_score'].mean()
        
        answer = f"📊 **Driver Performance Analysis:**\n\n"
        answer += f"**Fleet Average Risk Score:** {avg_score:.2f}\n\n"
        
        answer += f"🏆 **Best Performer:**\n"
        answer += f"• **Name:** {best_driver['name']}\n"
        answer += f"• **Risk Score:** {best_driver['risk_score']:.2f}\n"
        answer += f"• **License:** {best_driver['license_number']}\n\n"
        
        answer += f"⚠️ **Needs Attention:**\n"
        answer += f"• **Name:** {worst_driver['name']}\n"
        answer += f"• **Risk Score:** {worst_driver['risk_score']:.2f}\n"
        answer += f"• **License:** {worst_driver['license_number']}\n\n"
        
        performance_rating = "Excellent" if avg_score < 0.3 else "Good" if avg_score < 0.6 else "Needs Improvement"
        answer += f"**Overall Fleet Performance:** {performance_rating}"
        
        return {
            "answer": answer,
            "sources": ["driver_performance_db", "analytics_engine"],
            "confidence": 0.90
        }
    
    # Today/current status queries
    elif any(word in question_lower for word in ['today', 'current', 'now', 'status', 'summary']):
        answer = f"📈 **Today's Fleet Status Summary:**\n\n"
        answer += f"**🚛 Active Drivers:** {len(mock_driver_data)}\n"
        answer += f"**📋 Recent Incidents:** {len(mock_incident_data)}\n"
        answer += f"**🚨 Active Alerts:** {len(mock_alert_data)}\n\n"
        
        # Key metrics
        high_risk_count = len(mock_driver_data[mock_driver_data['risk_score'] > 0.7])
        high_severity_incidents = len(mock_incident_data[mock_incident_data['severity'] == 'high'])
        
        answer += f"**⚠️ Attention Required:**\n"
        if high_risk_count > 0:
            answer += f"• {high_risk_count} high-risk drivers need monitoring\n"
        if high_severity_incidents > 0:
            answer += f"• {high_severity_incidents} high-severity incidents reported\n"
        if len(mock_alert_data) > 0:
            answer += f"• {len(mock_alert_data)} active alerts requiring action\n"
        
        if high_risk_count == 0 and high_severity_incidents == 0:
            answer += "✅ No critical issues detected\n"
        
        answer += f"\n**📊 Overall Health:** {'Good' if high_risk_count <= 1 and high_severity_incidents <= 1 else 'Needs Attention'}"
        
        return {
            "answer": answer,
            "sources": ["real_time_dashboard", "fleet_management_system"],
            "confidence": 0.95
        }
    
    # Default response
    else:
        answer = f"🤖 **AI Assistant Ready**\n\n"
        answer += f"I can help you with logistics insights about:\n\n"
        answer += f"• **Driver Safety & Risk Assessment**\n"
        answer += f"• **Incident Analysis & Reports**\n"
        answer += f"• **Fleet Performance Metrics**\n"
        answer += f"• **Active Alerts & Notifications**\n"
        answer += f"• **Real-time Status Updates**\n\n"
        answer += f"**Your question:** \"{question}\"\n\n"
        answer += f"💡 Try asking about:\n"
        answer += f"- 'Which drivers are high-risk?'\n"
        answer += f"- 'Show me today's incidents'\n"
        answer += f"- 'What alerts are active?'\n"
        answer += f"- 'Fleet safety summary'"
        
        return {
            "answer": answer,
            "sources": ["ai_knowledge_base"],
            "confidence": 0.60
        }

@router.post("/query", response_model=AIAnswer)
def query_ai(payload: AIQuery) -> AIAnswer:
    try:
        if not payload.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Use our intelligent analysis function
        result = analyze_question(payload.question)
        
        return AIAnswer(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
            
    except Exception as e:
        print(f"AI query error: {e}")
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@router.get("/status")
def ai_status():
    return {
        "rag_available": False,
        "model_status": "mock_mode",
        "data_sources": ["drivers", "incidents", "alerts"],
        "platform": "windows_compatible"
    }