from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random


class Incident(BaseModel):
    id: str
    driver_id: str
    date: str
    time: str
    severity: str
    description: str
    location: str
    status: str = "resolved"


router = APIRouter()

# Generate realistic incidents for the 40 drivers
def generate_incidents_data():
    incidents = []
    incident_types = [
        "Harsh braking detected",
        "Speed limit violation",
        "Route deviation detected", 
        "Late delivery reported",
        "Vehicle maintenance alert",
        "Fuel efficiency concern",
        "Traffic violation recorded",
        "Customer complaint received",
        "GPS signal lost",
        "Unauthorized stop detected",
        "Engine temperature warning",
        "Tire pressure alert",
        "Accident reported - minor",
        "Parking violation",
        "Load weight exceeded",
        "Driver fatigue detected",
        "Mobile phone usage while driving",
        "Seatbelt violation",
        "Aggressive driving behavior",
        "Vehicle inspection overdue",
        "Brake system warning",
        "Overheating incident",
        "Emergency brake activation",
        "Lane departure detected",
        "Following distance violation"
    ]
    
    locations = [
        "NH-1 Chandigarh-Delhi", "GT Road Ludhiana", "DND Flyway Delhi", 
        "Yamuna Expressway", "Mumbai-Pune Highway", "Bangalore-Chennai Highway",
        "Ahmedabad-Mumbai Highway", "Jaipur-Delhi Highway", "Noida Expressway",
        "Eastern Freeway Mumbai", "ORR Hyderabad", "NICE Road Bangalore",
        "Lucknow-Kanpur Highway", "Kolkata Bypass", "Amritsar-Jalandhar Road",
        "Patna-Gaya Highway", "Jammu-Srinagar Highway", "Chennai-Bangalore Highway",
        "Pune-Kolhapur Highway", "Surat-Vadodara Highway", "Faridabad-Delhi",
        "Udaipur-Jodhpur Highway", "Kochi-Thiruvananthapuram", "Hyderabad-Warangal",
        "Indore-Bhopal Highway", "Vadodara-Ahmedabad", "Shimla-Chandigarh",
        "Ranchi-Jamshedpur", "Agra-Mathura Highway"
    ]
    
    severities = ["low", "medium", "high"]
    # Updated driver IDs for 40 drivers
    driver_ids = [f"D{str(i).zfill(3)}" for i in range(1, 41)]
    
    # Generate incidents for last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(1, 76):  # 75 incidents for 40 drivers
        incident_date = base_date + timedelta(days=random.randint(0, 30))
        incident_time = f"{random.randint(6, 23):02d}:{random.randint(0, 59):02d}"
        
        incident = Incident(
            id=f"I{str(1000 + i)}",
            driver_id=random.choice(driver_ids),
            date=incident_date.strftime("%Y-%m-%d"),
            time=incident_time,
            severity=random.choice(severities),
            description=random.choice(incident_types),
            location=random.choice(locations),
            status=random.choice(["resolved", "pending", "investigating"])
        )
        incidents.append(incident)
    
    # Sort by date (most recent first)
    incidents.sort(key=lambda x: x.date, reverse=True)
    return incidents


# Generate the incidents data
INCIDENTS_DB = generate_incidents_data()


@router.get("/", response_model=List[Incident])
def list_incidents() -> List[Incident]:
    """Get all incidents"""
    return INCIDENTS_DB


@router.get("/recent", response_model=List[Incident])
def get_recent_incidents(limit: int = 10) -> List[Incident]:
    """Get recent incidents (default 10)"""
    return INCIDENTS_DB[:limit]


@router.get("/high-severity", response_model=List[Incident])
def get_high_severity_incidents() -> List[Incident]:
    """Get high severity incidents only"""
    return [incident for incident in INCIDENTS_DB if incident.severity == "high"]


@router.get("/pending", response_model=List[Incident])
def get_pending_incidents() -> List[Incident]:
    """Get pending incidents"""
    return [incident for incident in INCIDENTS_DB if incident.status == "pending"]


@router.get("/driver/{driver_id}", response_model=List[Incident])
def get_driver_incidents(driver_id: str) -> List[Incident]:
    """Get incidents for specific driver"""
    driver_incidents = [incident for incident in INCIDENTS_DB if incident.driver_id == driver_id]
    if not driver_incidents:
        raise HTTPException(status_code=404, detail=f"No incidents found for driver {driver_id}")
    return driver_incidents


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: str) -> Incident:
    """Get specific incident by ID"""
    for incident in INCIDENTS_DB:
        if incident.id == incident_id:
            return incident
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@router.get("/stats/summary")
def get_incident_stats():
    """Get incident statistics summary"""
    total_incidents = len(INCIDENTS_DB)
    
    severity_count = {"low": 0, "medium": 0, "high": 0}
    status_count = {"resolved": 0, "pending": 0, "investigating": 0}
    
    for incident in INCIDENTS_DB:
        severity_count[incident.severity] += 1
        status_count[incident.status] += 1
    
    # Recent incidents (last 7 days)
    recent_date = datetime.now() - timedelta(days=7)
    recent_incidents = [
        i for i in INCIDENTS_DB 
        if datetime.strptime(i.date, "%Y-%m-%d") >= recent_date
    ]
    
    # Driver incident count
    driver_incidents = {}
    for incident in INCIDENTS_DB:
        driver_id = incident.driver_id
        driver_incidents[driver_id] = driver_incidents.get(driver_id, 0) + 1
    
    # Top 5 drivers with most incidents
    top_incident_drivers = sorted(driver_incidents.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_incidents": total_incidents,
        "recent_incidents_7_days": len(recent_incidents),
        "severity_breakdown": severity_count,
        "status_breakdown": status_count,
        "pending_incidents": status_count["pending"],
        "high_severity_count": severity_count["high"],
        "top_incident_drivers": [
            {"driver_id": driver_id, "incident_count": count} 
            for driver_id, count in top_incident_drivers
        ],
        "resolution_rate": round(
            (status_count["resolved"] / total_incidents * 100) if total_incidents > 0 else 0, 1
        )
    }