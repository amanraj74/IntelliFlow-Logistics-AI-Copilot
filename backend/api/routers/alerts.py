from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random


class Alert(BaseModel):
    id: str
    type: str
    message: str
    priority: str
    driver_id: str = ""
    timestamp: str
    status: str = "active"
    location: str = ""


router = APIRouter()

# Generate realistic alerts for the system
def generate_alerts_data():
    alerts = []
    alert_types = [
        "safety", "compliance", "performance", "maintenance", 
        "route", "fuel", "weather", "security"
    ]
    
    priorities = ["low", "medium", "high", "critical"]
    
    alert_templates = {
        "safety": [
            "Driver {driver_id} risk score increased to {risk}",
            "Harsh braking detected for driver {driver_id}",
            "Speed violation recorded - driver {driver_id}",
            "Driver fatigue detected - {driver_id}",
            "Unsafe driving behavior - driver {driver_id}"
        ],
        "compliance": [
            "License expiry reminder - driver {driver_id}",
            "Vehicle inspection overdue - {driver_id}",
            "Load weight exceeded - driver {driver_id}",
            "Route deviation detected - {driver_id}",
            "Unauthorized stop - driver {driver_id}"
        ],
        "performance": [
            "Late delivery reported - driver {driver_id}",
            "Fuel efficiency below threshold - {driver_id}",
            "Customer complaint received - {driver_id}",
            "Multiple violations - driver {driver_id}",
            "Performance review required - {driver_id}"
        ],
        "maintenance": [
            "Engine temperature warning - driver {driver_id}",
            "Tire pressure alert - {driver_id}",
            "Brake system check required - {driver_id}",
            "GPS malfunction - driver {driver_id}",
            "Vehicle diagnostics alert - {driver_id}"
        ],
        "route": [
            "Traffic congestion on route - {driver_id}",
            "Road closure ahead - driver {driver_id}",
            "Weather alert for route - {driver_id}",
            "Construction zone detected - {driver_id}",
            "Optimal route suggestion - {driver_id}"
        ],
        "fuel": [
            "Fuel level critical - driver {driver_id}",
            "Fuel station recommendation - {driver_id}",
            "Fuel efficiency monitoring - {driver_id}",
            "Fuel cost optimization alert - {driver_id}",
            "Fuel theft suspected - {driver_id}"
        ],
        "weather": [
            "Heavy rain warning - route {location}",
            "Fog conditions ahead - driver {driver_id}",
            "High wind alert - {location}",
            "Temperature extreme warning - {driver_id}",
            "Weather delay expected - {driver_id}"
        ],
        "security": [
            "Unauthorized access attempt - {driver_id}",
            "Vehicle left unsecured - driver {driver_id}",
            "Cargo seal broken - {driver_id}",
            "Emergency button pressed - driver {driver_id}",
            "Vehicle tracking lost - {driver_id}"
        ]
    }
    
    locations = [
        "NH-1 Delhi-Chandigarh", "Mumbai-Pune Highway", "Bangalore-Chennai Route",
        "GT Road Ludhiana", "Eastern Freeway Mumbai", "DND Flyway Delhi",
        "Yamuna Expressway", "Noida-Greater Noida", "Ahmedabad-Surat Highway",
        "Faridabad-Gurgaon", "Udaipur-Jodhpur Highway", "Kochi-Thiruvananthapuram",
        "Hyderabad-Warangal", "Indore-Bhopal Highway", "Vadodara-Ahmedabad",
        "Shimla-Chandigarh", "Ranchi-Jamshedpur", "Agra-Mathura Highway"
    ]
    
    # Updated driver IDs for 40 drivers
    driver_ids = [f"D{str(i).zfill(3)}" for i in range(1, 41)]
    
    # Generate alerts for last 7 days
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(1, 51):  # 50 alerts
        alert_type = random.choice(alert_types)
        priority = random.choice(priorities)
        driver_id = random.choice(driver_ids)
        location = random.choice(locations)
        
        # Select random template for the alert type
        template = random.choice(alert_templates[alert_type])
        
        # Fill template with data
        if "{risk}" in template:
            risk_score = round(random.uniform(0.7, 0.9), 2)
            message = template.format(driver_id=driver_id, risk=risk_score)
        else:
            message = template.format(driver_id=driver_id, location=location)
        
        # Generate timestamp
        alert_time = base_time + timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Set status based on priority and age
        if priority == "critical":
            status = "active"
        elif alert_time < datetime.now() - timedelta(days=2):
            status = random.choice(["resolved", "acknowledged"])
        else:
            status = random.choice(["active", "acknowledged"])
        
        alert = Alert(
            id=f"A{str(2000 + i)}",
            type=alert_type,
            message=message,
            priority=priority,
            driver_id=driver_id if "{driver_id}" in template else "",
            timestamp=alert_time.isoformat(),
            status=status,
            location=location if "{location}" in template else ""
        )
        alerts.append(alert)
    
    # Sort by timestamp (most recent first)
    alerts.sort(key=lambda x: x.timestamp, reverse=True)
    return alerts


# Generate the alerts data
ALERTS_DB = generate_alerts_data()


@router.get("/", response_model=List[Alert])
def list_alerts() -> List[Alert]:
    """Get all alerts"""
    return ALERTS_DB


@router.get("/active", response_model=List[Alert])
def get_active_alerts() -> List[Alert]:
    """Get only active alerts"""
    return [alert for alert in ALERTS_DB if alert.status == "active"]


@router.get("/critical", response_model=List[Alert])
def get_critical_alerts() -> List[Alert]:
    """Get critical priority alerts"""
    return [alert for alert in ALERTS_DB if alert.priority == "critical"]


@router.get("/high-priority", response_model=List[Alert])
def get_high_priority_alerts() -> List[Alert]:
    """Get high and critical priority alerts"""
    return [alert for alert in ALERTS_DB if alert.priority in ["high", "critical"]]


@router.get("/type/{alert_type}", response_model=List[Alert])
def get_alerts_by_type(alert_type: str) -> List[Alert]:
    """Get alerts by specific type"""
    filtered_alerts = [alert for alert in ALERTS_DB if alert.type == alert_type]
    if not filtered_alerts:
        raise HTTPException(status_code=404, detail=f"No alerts found for type: {alert_type}")
    return filtered_alerts


@router.get("/driver/{driver_id}", response_model=List[Alert])
def get_driver_alerts(driver_id: str) -> List[Alert]:
    """Get alerts for specific driver"""
    driver_alerts = [alert for alert in ALERTS_DB if alert.driver_id == driver_id]
    if not driver_alerts:
        raise HTTPException(status_code=404, detail=f"No alerts found for driver {driver_id}")
    return driver_alerts


@router.get("/recent/{hours}", response_model=List[Alert])
def get_recent_alerts(hours: int = 24) -> List[Alert]:
    """Get alerts from last N hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_alerts = [
        alert for alert in ALERTS_DB 
        if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00').replace('+00:00', '')) >= cutoff_time
    ]
    return recent_alerts


@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: str) -> Alert:
    """Get specific alert by ID"""
    for alert in ALERTS_DB:
        if alert.id == alert_id:
            return alert
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str):
    """Mark alert as acknowledged"""
    for alert in ALERTS_DB:
        if alert.id == alert_id:
            alert.status = "acknowledged"
            return {"message": f"Alert {alert_id} acknowledged", "status": "success"}
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    for alert in ALERTS_DB:
        if alert.id == alert_id:
            alert.status = "resolved"
            return {"message": f"Alert {alert_id} resolved", "status": "success"}
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.get("/stats/summary")
def get_alert_stats():
    """Get alert statistics summary"""
    total_alerts = len(ALERTS_DB)
    
    # Count by status
    status_count = {"active": 0, "acknowledged": 0, "resolved": 0}
    for alert in ALERTS_DB:
        status_count[alert.status] += 1
    
    # Count by priority
    priority_count = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for alert in ALERTS_DB:
        priority_count[alert.priority] += 1
    
    # Count by type
    type_count = {}
    for alert in ALERTS_DB:
        alert_type = alert.type
        type_count[alert_type] = type_count.get(alert_type, 0) + 1
    
    # Recent alerts (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_alerts = [
        alert for alert in ALERTS_DB 
        if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00').replace('+00:00', '')) >= recent_cutoff
    ]
    
    # Driver with most alerts
    driver_alert_count = {}
    for alert in ALERTS_DB:
        if alert.driver_id:
            driver_id = alert.driver_id
            driver_alert_count[driver_id] = driver_alert_count.get(driver_id, 0) + 1
    
    top_alert_driver = max(driver_alert_count.items(), key=lambda x: x[1]) if driver_alert_count else ("None", 0)
    
    return {
        "total_alerts": total_alerts,
        "active_alerts": status_count["active"],
        "critical_alerts": priority_count["critical"],
        "recent_alerts_24h": len(recent_alerts),
        "status_breakdown": status_count,
        "priority_breakdown": priority_count,
        "type_breakdown": type_count,
        "resolution_rate": round(
            (status_count["resolved"] / total_alerts * 100) if total_alerts > 0 else 0, 1
        ),
        "most_alerts_driver": {
            "driver_id": top_alert_driver[0],
            "alert_count": top_alert_driver[1]
        }
    }