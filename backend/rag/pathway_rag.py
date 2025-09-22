import pathway as pw
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PathwayRAGSystem:
    """Real-time RAG system powered by Pathway for logistics queries"""
    
    def __init__(self, knowledge_base_path: str = "./data/processed/knowledge_base.jsonl"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_data = []
        logger.info(f"RAG system initialized with knowledge base: {knowledge_base_path}")
    
    def load_knowledge_base(self):
        """Load the latest knowledge base data"""
        try:
            if os.path.exists(self.knowledge_base_path):
                self.knowledge_data = []
                with open(self.knowledge_base_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                self.knowledge_data.append(data)
                            except json.JSONDecodeError:
                                continue
                logger.info(f"Loaded {len(self.knowledge_data)} knowledge entries")
            else:
                logger.warning(f"Knowledge base file not found: {self.knowledge_base_path}")
                self.knowledge_data = []
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_data = []
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        try:
            query_lower = query.lower()
            results = []
            
            # Simple keyword-based search (in production, use embeddings)
            for entry in self.knowledge_data:
                content = entry.get('content', '').lower()
                entry_type = entry.get('type', '')
                
                # Calculate relevance score
                score = 0
                
                # Keyword matching
                query_words = re.findall(r'\w+', query_lower)
                for word in query_words:
                    if word in content:
                        score += 1
                
                # Type-specific boosting
                if 'driver' in query_lower and entry_type == 'driver':
                    score += 2
                elif 'incident' in query_lower and entry_type == 'incident':
                    score += 2
                elif 'shipment' in query_lower and entry_type == 'shipment':
                    score += 2
                elif 'risk' in query_lower and 'risk' in content:
                    score += 3
                elif 'high' in query_lower and 'high' in content:
                    score += 2
                
                if score > 0:
                    results.append({
                        'content': entry.get('content', ''),
                        'type': entry_type,
                        'score': score,
                        'timestamp': entry.get('timestamp', '')
                    })
            
            # Sort by relevance score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer based on query and context"""
        try:
            if not context:
                return {
                    "answer": "I don't have enough information to answer that question. Please ensure data is being streamed to the system.",
                    "sources": [],
                    "confidence": 0.1
                }
            
            query_lower = query.lower()
            
            # Analyze query intent
            if any(word in query_lower for word in ['high risk', 'risky', 'dangerous']):
                return self._generate_risk_answer(context)
            elif any(word in query_lower for word in ['incident', 'accident', 'violation']):
                return self._generate_incident_answer(context)
            elif any(word in query_lower for word in ['driver', 'performance', 'best', 'worst']):
                return self._generate_driver_answer(context)
            elif any(word in query_lower for word in ['shipment', 'delivery', 'cargo']):
                return self._generate_shipment_answer(context)
            else:
                return self._generate_general_answer(query, context)
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def _generate_risk_answer(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk-related answers"""
        risk_entries = [c for c in context if 'risk' in c['content'].lower()]
        high_risk_entries = [c for c in risk_entries if 'high' in c['content'].lower() or any(score in c['content'] for score in ['0.7', '0.8', '0.9', '1.0'])]
        
        if high_risk_entries:
            answer = "🚨 **High-Risk Drivers Identified:**\n\n"
            for entry in high_risk_entries[:3]:
                answer += f"• {entry['content']}\n"
            
            if len(high_risk_entries) > 3:
                answer += f"\n... and {len(high_risk_entries) - 3} more high-risk drivers."
            
            answer += "\n💡 **Recommendation:** Immediate safety review and training required for high-risk drivers."
        else:
            answer = "✅ No high-risk drivers currently identified in the system."
        
        return {
            "answer": answer,
            "sources": [f"real_time_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}"],
            "confidence": 0.9 if high_risk_entries else 0.7
        }
    
    def _generate_incident_answer(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate incident-related answers"""
        incident_entries = [c for c in context if c['type'] == 'incident']
        high_severity = [c for c in incident_entries if 'high' in c['content'].lower()]
        
        if incident_entries:
            answer = f"📋 **Incident Analysis (Real-time Data):**\n\n"
            answer += f"**Total Recent Incidents:** {len(incident_entries)}\n"
            answer += f"**High Severity:** {len(high_severity)}\n\n"
            
            answer += "**Recent Incidents:**\n"
            for i, entry in enumerate(incident_entries[:3], 1):
                severity_icon = "🔴" if "high" in entry['content'].lower() else "🟡" if "medium" in entry['content'].lower() else "🟢"
                answer += f"{severity_icon} {entry['content']}\n"
            
            if len(high_severity) > 0:
                answer += f"\n⚠️ **Action Required:** {len(high_severity)} high-severity incidents need immediate attention."
        else:
            answer = "✅ No recent incidents found in the real-time data stream."
        
        return {
            "answer": answer,
            "sources": [f"live_incident_stream_{datetime.now().strftime('%Y%m%d_%H%M')}"],
            "confidence": 0.85 if incident_entries else 0.6
        }
    
    def _generate_driver_answer(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate driver performance answers"""
        driver_entries = [c for c in context if c['type'] == 'driver']
        
        if driver_entries:
            # Extract risk scores and find best/worst
            risk_info = []
            for entry in driver_entries:
                content = entry['content']
                # Try to extract risk score and driver name
                import re
                risk_match = re.search(r'risk score (\d+\.\d+)', content)
                name_match = re.search(r'Driver (\w+(?:\s+\w+)*)', content)
                
                if risk_match and name_match:
                    risk_info.append({
                        'name': name_match.group(1),
                        'risk_score': float(risk_match.group(1)),
                        'content': content
                    })
            
            if risk_info:
                # Sort by risk score
                risk_info.sort(key=lambda x: x['risk_score'])
                best_driver = risk_info[0]
                worst_driver = risk_info[-1]
                avg_risk = sum(d['risk_score'] for d in risk_info) / len(risk_info)
                
                answer = f"📊 **Live Driver Performance Analysis:**\n\n"
                answer += f"**Fleet Size:** {len(risk_info)} active drivers\n"
                answer += f"**Average Risk Score:** {avg_risk:.2f}\n\n"
                
                answer += f"🏆 **Best Performer:**\n"
                answer += f"• {best_driver['content']}\n\n"
                
                answer += f"⚠️ **Needs Attention:**\n"
                answer += f"• {worst_driver['content']}\n\n"
                
                performance_rating = "Excellent" if avg_risk < 0.3 else "Good" if avg_risk < 0.6 else "Needs Improvement"
                answer += f"**Overall Fleet Performance:** {performance_rating}"
            else:
                answer = "Driver performance data is being processed from the live stream..."
        else:
            answer = "No driver data available in the current real-time stream."
        
        return {
            "answer": answer,
            "sources": [f"live_driver_performance_{datetime.now().strftime('%Y%m%d_%H%M')}"],
            "confidence": 0.9 if driver_entries else 0.3
        }
    
    def _generate_shipment_answer(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate shipment-related answers"""
        shipment_entries = [c for c in context if c['type'] == 'shipment']
        
        if shipment_entries:
            # Analyze shipment statuses
            statuses = {}
            for entry in shipment_entries:
                content = entry['content'].lower()
                if 'in_transit' in content:
                    statuses['in_transit'] = statuses.get('in_transit', 0) + 1
                elif 'delivered' in content:
                    statuses['delivered'] = statuses.get('delivered', 0) + 1
                elif 'delayed' in content:
                    statuses['delayed'] = statuses.get('delayed', 0) + 1
                elif 'cancelled' in content:
                    statuses['cancelled'] = statuses.get('cancelled', 0) + 1
            
            answer = f"🚛 **Live Shipment Status:**\n\n"
            answer += f"**Total Shipments:** {len(shipment_entries)}\n\n"
            
            for status, count in statuses.items():
                status_icon = {"in_transit": "🚛", "delivered": "✅", "delayed": "⏰", "cancelled": "❌"}.get(status, "📦")
                answer += f"{status_icon} **{status.replace('_', ' ').title()}:** {count}\n"
            
            if statuses.get('delayed', 0) > 0:
                answer += f"\n⚠️ **Attention:** {statuses['delayed']} shipments are currently delayed."
        else:
            answer = "No shipment data available in the current real-time stream."
        
        return {
            "answer": answer,
            "sources": [f"live_shipment_tracking_{datetime.now().strftime('%Y%m%d_%H%M')}"],
            "confidence": 0.85 if shipment_entries else 0.3
        }
    
    def _generate_general_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate general answers from available context"""
        answer = f"📊 **Live System Status:**\n\n"
        answer += f"Based on real-time data stream analysis:\n\n"
        
        # Categorize context
        types = {}
        for entry in context:
            entry_type = entry.get('type', 'unknown')
            types[entry_type] = types.get(entry_type, 0) + 1
        
        for entry_type, count in types.items():
            type_icon = {"driver": "👥", "incident": "📋", "shipment": "🚛"}.get(entry_type, "📊")
            answer += f"{type_icon} **{entry_type.title()}s:** {count} entries\n"
        
        answer += f"\n**Recent Updates:**\n"
        for entry in context[:3]:
            answer += f"• {entry['content'][:100]}...\n"
        
        answer += f"\n💡 Try asking about 'high-risk drivers', 'recent incidents', or 'shipment status'"
        
        return {
            "answer": answer,
            "sources": [f"live_data_stream_{datetime.now().strftime('%Y%m%d_%H%M')}"],
            "confidence": 0.7
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """Main query method"""
        logger.info(f"Processing query: {question}")
        
        # Load latest knowledge base
        self.load_knowledge_base()
        
        # Search for relevant context
        context = self.search_knowledge(question)
        
        # Generate answer
        result = self.generate_answer(question, context)
        
        logger.info(f"Generated answer with confidence: {result.get('confidence', 0)}")
        return result

# Global RAG instance
rag_system = PathwayRAGSystem()

def query_rag(question: str) -> Dict[str, Any]:
    """Public interface for RAG queries"""
    return rag_system.query(question)