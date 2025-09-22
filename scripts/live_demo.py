import json
import time
import random
from datetime import datetime

def add_live_incident():
    """Add new incident to demonstrate real-time updates"""
    
    incidents = [
        {
            "id": f"INC{int(time.time())}",
            "driver_id": f"DRV-00{random.randint(1,5)}",
            "description": "Speed violation detected - exceeded limit by 30 km/h",
            "severity": "high",
            "date": datetime.now().isoformat()
        },
        {
            "id": f"INC{int(time.time())+1}",
            "driver_id": f"DRV-00{random.randint(1,5)}",
            "description": "Harsh braking event detected on highway",
            "severity": "medium", 
            "date": datetime.now().isoformat()
        },
        {
            "id": f"INC{int(time.time())+2}",
            "driver_id": f"DRV-00{random.randint(1,5)}",
            "description": "Route deviation without authorization",
            "severity": "low",
            "date": datetime.now().isoformat()
        }
    ]
    
    incident = random.choice(incidents)
    
    # Append to streaming file
    with open("data/streams/incidents/current_incidents.jsonl", "a") as f:
        f.write(json.dumps(incident) + "\n")
    
    print(f"✅ Added: {incident['description'][:50]}... (Driver: {incident['driver_id']})")
    return incident

def run_live_demo():
    """Demo real-time updates"""
    print("🚀 Starting live demo - adding incidents every 15 seconds")
    print("💡 Query your AI assistant to see real-time updates!")
    print("📊 Watch responses change as new data arrives")
    print("-" * 60)
    
    for i in range(3):
        incident = add_live_incident()
        print(f"📈 Incident {i+1}/3 added at {datetime.now().strftime('%H:%M:%S')}")
        
        if i < 2:
            print("⏰ Next incident in 15 seconds...")
            time.sleep(15)
    
    print("\n✅ Demo complete!")
    print("🔍 Query your AI: 'Which drivers are high-risk?' to see the updates")

if __name__ == "__main__":
    run_live_demo()
