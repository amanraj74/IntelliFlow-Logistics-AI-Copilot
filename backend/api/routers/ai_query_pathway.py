from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIQuery(BaseModel):
    question: str

class AIAnswer(BaseModel):
    answer: str
    sources: List[str]
    confidence: float = 0.0

router = APIRouter()

def get_real_data():
    """Get real data from files - this replaces all mock data"""
    data = {
        "drivers": [],
        "incidents": [],
        "shipments": []
    }
    
    try:
        # Load drivers from CSV files
        drivers_dir = "./data/streams/drivers"
        if os.path.exists(drivers_dir):
            for filename in os.listdir(drivers_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(drivers_dir, filename)
                    try:
                        df = pd.read_csv(filepath)
                        for _, row in df.iterrows():
                            driver_data = {
                                "id": row.get('id', 'Unknown'),
                                "name": row.get('name', 'Unknown Driver'),
                                "license_number": row.get('license_number', 'N/A'),
                                "risk_score": float(row.get('risk_score', 0)),
                                "status": row.get('status', 'active')
                            }
                            data["drivers"].append(driver_data)
                        logger.info(f"Loaded {len(df)} drivers from {filename}")
                    except Exception as e:
                        logger.error(f"Error reading {filename}: {e}")
        
        # Load incidents from JSONL files
        incidents_dir = "./data/streams/incidents"
        if os.path.exists(incidents_dir):
            for filename in os.listdir(incidents_dir):
                if filename.endswith('.jsonl'):
                    filepath = os.path.join(incidents_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            for line_num, line in enumerate(f, 1):
                                if line.strip():
                                    incident = json.loads(line)
                                    data["incidents"].append(incident)
                        logger.info(f"Loaded incidents from {filename}")
                    except Exception as e:
                        logger.error(f"Error reading {filename}: {e}")
        
        logger.info(f"Total loaded: {len(data['drivers'])} drivers, {len(data['incidents'])} incidents")
        return data
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return data

def answer_question(question: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate real answers based on actual data"""
    question_lower = question.lower()
    drivers = data.get("drivers", [])
    incidents = data.get("incidents", [])
    
    # High-risk driver questions
    if any(word in question_lower for word in ['high risk', 'risky', 'dangerous']):
        high_risk_drivers = [d for d in drivers if d['risk_score'] > 0.7]
        
        if high_risk_drivers:
            answer = f"🚨 **REAL DATA ALERT**: Found {len(high_risk_drivers)} high-risk drivers requiring immediate attention!\n\n"
            
            for driver in high_risk_drivers:
                answer += f"🔴 **{driver['name']}** (ID: {driver['id']})\n"
                answer += f"   • Risk Score: **{driver['risk_score']:.2f}**\n"
                answer += f"   • License: {driver['license_number']}\n"
                answer += f"   • Status: {driver['status']}\n\n"
            
            # Check if these drivers have incidents
            driver_ids = [d['id'] for d in high_risk_drivers]
            related_incidents = [i for i in incidents if i.get('driver_id') in driver_ids]
            
            if related_incidents:
                answer += f"⚠️ **CRITICAL**: These drivers also have {len(related_incidents)} recent incidents!\n"
                for incident in related_incidents[:2]:
                    answer += f"   • {incident.get('description', 'Incident reported')}\n"
            
            answer += f"\n💡 **IMMEDIATE ACTION**: Schedule safety review for all high-risk drivers."
            
            return {
                "answer": answer,
                "sources": [f"live_driver_data_{datetime.now().strftime('%Y%m%d_%H%M')}"],
                "confidence": 0.95
            }
        else:
            return {
                "answer": f"✅ **GOOD NEWS**: No high-risk drivers found!\n\nAnalyzed {len(drivers)} active drivers. All risk scores are within acceptable limits (< 0.7).",
                "sources": [f"driver_safety_analysis_{datetime.now().strftime('%H%M')}"],
                "confidence": 0.90
            }
    
    # Incident questions
    elif any(word in question_lower for word in ['incident', 'problem', 'accident']):
        if incidents:
            high_severity = [i for i in incidents if i.get('severity', '').lower() == 'high']
            
            answer = f"📋 **INCIDENT REPORT** (Real-time data):\n\n"
            answer += f"**Total Incidents:** {len(incidents)}\n"
            answer += f"**High Severity:** {len(high_severity)}\n\n"
            
            answer += f"**Recent Incidents:**\n"
            for i, incident in enumerate(incidents[:3], 1):
                severity = incident.get('severity', 'unknown')
                description = incident.get('description', 'No description')
                driver_id = incident.get('driver_id', 'Unknown')
                
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity.lower(), "⚪")
                answer += f"{severity_emoji} **{i}.** Driver {driver_id}: {description}\n"
            
            if high_severity:
                answer += f"\n🚨 **URGENT**: {len(high_severity)} critical incidents need immediate response!"
            
            return {
                "answer": answer,
                "sources": [f"incident_monitoring_{datetime.now().strftime('%H%M')}"],
                "confidence": 0.92
            }
        else:
            return {
                "answer": "✅ **NO INCIDENTS**: No incidents reported in the monitoring period.",
                "sources": ["incident_system"],
                "confidence": 0.80
            }
    
    # Status/summary questions
    elif any(word in question_lower for word in ['status', 'summary', 'today']):
        high_risk_count = len([d for d in drivers if d['risk_score'] > 0.7])
        high_incidents = len([i for i in incidents if i.get('severity', '').lower() == 'high'])
        
        answer = f"📊 **FLEET STATUS REPORT** (Live Data)\n\n"
        answer += f"**📈 Current Metrics:**\n"
        answer += f"• Active Drivers: **{len(drivers)}**\n"
        answer += f"• High-Risk Drivers: **{high_risk_count}**\n"
        answer += f"• Total Incidents: **{len(incidents)}**\n"
        answer += f"• Critical Incidents: **{high_incidents}**\n\n"
        
        # Calculate fleet health
        if drivers:
            avg_risk = sum(d['risk_score'] for d in drivers) / len(drivers)
            health = "🟢 Excellent" if avg_risk < 0.3 else "🟡 Fair" if avg_risk < 0.6 else "🔴 Needs Attention"
            answer += f"**Fleet Health:** {health} (Avg Risk: {avg_risk:.2f})\n\n"
        
        if high_risk_count > 0 or high_incidents > 0:
            answer += f"⚠️ **ACTION ITEMS:**\n"
            if high_risk_count > 0:
                answer += f"• Review {high_risk_count} high-risk drivers\n"
            if high_incidents > 0:
                answer += f"• Address {high_incidents} critical incidents\n"
        else:
            answer += f"✅ **ALL CLEAR**: No critical issues detected!"
        
        return {
            "answer": answer,
            "sources": [f"real_time_dashboard_{datetime.now().strftime('%H%M')}"],
            "confidence": 0.98
        }
    
    # Default response with current data
    else:
        answer = f"🤖 **AI ASSISTANT** - Data Updated: {datetime.now().strftime('%H:%M:%S')}\n\n"
        answer += f"**Current System Status:**\n"
        answer += f"• Monitoring: {len(drivers)} drivers\n"
        answer += f"• Recent incidents: {len(incidents)}\n"
        answer += f"• Data source: Live file system\n\n"
        answer += f"**Your question:** \"{question}\"\n\n"
        answer += f"**Try asking:**\n"
        answer += f"• 'Which drivers are high-risk?'\n"
        answer += f"• 'Show recent incidents'\n"
        answer += f"• 'Fleet status summary'\n"
        
        return {
            "answer": answer,
            "sources": ["live_ai_assistant"],
            "confidence": 0.75
        }

@router.post("/query", response_model=AIAnswer)
def query_ai(payload: AIQuery) -> AIAnswer:
    """Main AI query endpoint - now with REAL data"""
    try:
        if not payload.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"🤖 Processing query: {payload.question}")
        
        # Get real data from files
        real_data = get_real_data()
        
        # Generate answer based on real data
        result = answer_question(payload.question, real_data)
        
        logger.info(f"✅ Generated answer with {result['confidence']:.0%} confidence")
        
        return AIAnswer(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
        
    except Exception as e:
        logger.error(f"❌ AI query error: {e}")
        
        # Provide helpful error message
        error_msg = f"🔧 **System Status**: {str(e)}\n\n"
        error_msg += f"**Data Check:**\n"
        error_msg += f"• Looking for data in: `./data/streams/`\n"
        error_msg += f"• Driver files: `./data/streams/drivers/*.csv`\n"
        error_msg += f"• Incident files: `./data/streams/incidents/*.jsonl`\n\n"
        error_msg += f"**Quick Fix:**\n"
        error_msg += f"1. Create the data files as shown in instructions\n"
        error_msg += f"2. Restart the application\n"
        error_msg += f"3. Try your query again"
        
        return AIAnswer(
            answer=error_msg,
            sources=["system_diagnostics"],
            confidence=0.1
        )

@router.get("/status")
def ai_status():
    """Get AI system status with real data counts"""
    try:
        real_data = get_real_data()
        
        return {
            "status": "operational",
            "data_sources": {
                "drivers": len(real_data.get("drivers", [])),
                "incidents": len(real_data.get("incidents", [])),
                "shipments": len(real_data.get("shipments", []))
            },
            "mode": "real_data_analysis",
            "last_updated": datetime.now().isoformat(),
            "data_available": len(real_data.get("drivers", [])) > 0 or len(real_data.get("incidents", [])) > 0
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "mode": "diagnostics",
            "last_updated": datetime.now().isoformat()
        }