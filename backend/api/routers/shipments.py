from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random


class Shipment(BaseModel):
    id: str
    driver_id: str
    status: str
    origin: str
    destination: str
    cargo_type: str
    cargo_weight: float = 0.0
    departure_time: str = ""
    estimated_arrival: str = ""
    actual_arrival: Optional[str] = None
    distance: float = 0.0
    fuel_consumption: float = 0.0
    priority: str = "medium"
    customer: str = ""
    vehicle_id: str = ""


router = APIRouter()

# Generate realistic shipment data for 40 drivers
def generate_shipments_data():
    shipments = []
    
    # Indian cities and routes
    origins = [
        "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
        "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur",
        "Nagpur", "Indore", "Bhopal", "Chandigarh", "Ludhiana", "Agra",
        "Noida", "Gurugram", "Faridabad", "Ghaziabad", "Amritsar", "Patna"
    ]
    
    destinations = [
        "Kochi", "Thiruvananthapuram", "Coimbatore", "Madurai", "Vijayawada",
        "Visakhapatnam", "Ranchi", "Jamshedpur", "Raipur", "Jodhpur",
        "Udaipur", "Vadodara", "Rajkot", "Nashik", "Aurangabad", "Solapur",
        "Hubli", "Mysore", "Mangalore", "Calicut", "Thrissur", "Ernakulam"
    ]
    
    cargo_types = [
        "Electronics", "Food Items", "Chemicals", "Construction Materials",
        "Textiles", "Automotive Parts", "Pharmaceuticals", "Consumer Goods",
        "Raw Materials", "Machinery", "Agricultural Products", "Furniture",
        "Steel Products", "Plastic Items", "Medical Equipment"
    ]
    
    statuses = ["in_transit", "delivered", "delayed", "cancelled", "pending"]
    priorities = ["low", "medium", "high", "critical"]
    
    customers = [
        "Reliance Industries", "Tata Group", "Wipro Ltd", "Infosys Ltd",
        "HCL Technologies", "Tech Mahindra", "Bajaj Auto", "Mahindra Group",
        "Godrej Group", "Larsen & Toubro", "Asian Paints", "UltraTech Cement",
        "Britannia Industries", "Nestle India", "Hindustan Unilever",
        "ITC Limited", "Maruti Suzuki", "Hero MotoCorp", "TVS Motors"
    ]
    
    # Driver and vehicle IDs for 40 drivers
    driver_ids = [f"D{str(i).zfill(3)}" for i in range(1, 41)]
    vehicle_ids = [f"V{str(i).zfill(3)}" for i in range(1, 41)]
    
    # Generate shipments for last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(1, 101):  # 100 shipments
        # Random dates and times
        departure_date = base_date + timedelta(days=random.randint(0, 30))
        departure_time = departure_date + timedelta(
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59)
        )
        
        # Estimated arrival (1-3 days later)
        estimated_arrival = departure_time + timedelta(
            days=random.randint(1, 3),
            hours=random.randint(1, 8)
        )
        
        # Actual arrival (for completed shipments)
        status = random.choice(statuses)
        actual_arrival = None
        if status == "delivered":
            # Delivered shipments have actual arrival
            variation = random.randint(-4, 8)  # Can be early or late
            actual_arrival = (estimated_arrival + timedelta(hours=variation)).isoformat()
        elif status == "delayed":
            # Delayed shipments are overdue
            estimated_arrival = departure_time + timedelta(days=random.randint(1, 2))
        
        origin = random.choice(origins)
        destination = random.choice([d for d in destinations if d != origin])
        
        shipment = Shipment(
            id=f"SHP{str(3000 + i).zfill(4)}",
            driver_id=random.choice(driver_ids),
            status=status,
            origin=origin,
            destination=destination,
            cargo_type=random.choice(cargo_types),
            cargo_weight=round(random.uniform(500, 15000), 1),  # 0.5 to 15 tons
            departure_time=departure_time.isoformat(),
            estimated_arrival=estimated_arrival.isoformat(),
            actual_arrival=actual_arrival,
            distance=round(random.uniform(200, 2500), 1),  # 200km to 2500km
            fuel_consumption=round(random.uniform(50, 400), 1),  # 50L to 400L
            priority=random.choice(priorities),
            customer=random.choice(customers),
            vehicle_id=random.choice(vehicle_ids)
        )
        shipments.append(shipment)
    
    # Sort by departure time (most recent first)
    shipments.sort(key=lambda x: x.departure_time, reverse=True)
    return shipments


# Generate the shipments data
SHIPMENTS_DB = generate_shipments_data()


@router.get("/", response_model=List[Shipment])
def list_shipments() -> List[Shipment]:
    """Get all shipments"""
    return SHIPMENTS_DB


@router.get("/active", response_model=List[Shipment])
def get_active_shipments() -> List[Shipment]:
    """Get shipments currently in transit"""
    return [shipment for shipment in SHIPMENTS_DB if shipment.status == "in_transit"]


@router.get("/delayed", response_model=List[Shipment])
def get_delayed_shipments() -> List[Shipment]:
    """Get delayed shipments"""
    return [shipment for shipment in SHIPMENTS_DB if shipment.status == "delayed"]


@router.get("/delivered", response_model=List[Shipment])
def get_delivered_shipments() -> List[Shipment]:
    """Get completed shipments"""
    return [shipment for shipment in SHIPMENTS_DB if shipment.status == "delivered"]


@router.get("/high-priority", response_model=List[Shipment])
def get_high_priority_shipments() -> List[Shipment]:
    """Get high priority shipments"""
    return [shipment for shipment in SHIPMENTS_DB if shipment.priority in ["high", "critical"]]


@router.get("/driver/{driver_id}", response_model=List[Shipment])
def get_driver_shipments(driver_id: str) -> List[Shipment]:
    """Get shipments for specific driver"""
    driver_shipments = [shipment for shipment in SHIPMENTS_DB if shipment.driver_id == driver_id]
    if not driver_shipments:
        raise HTTPException(status_code=404, detail=f"No shipments found for driver {driver_id}")
    return driver_shipments


@router.get("/origin/{city}", response_model=List[Shipment])
def get_shipments_from_origin(city: str) -> List[Shipment]:
    """Get shipments from specific origin city"""
    origin_shipments = [shipment for shipment in SHIPMENTS_DB if shipment.origin.lower() == city.lower()]
    if not origin_shipments:
        raise HTTPException(status_code=404, detail=f"No shipments found from {city}")
    return origin_shipments


@router.get("/destination/{city}", response_model=List[Shipment])
def get_shipments_to_destination(city: str) -> List[Shipment]:
    """Get shipments to specific destination city"""
    dest_shipments = [shipment for shipment in SHIPMENTS_DB if shipment.destination.lower() == city.lower()]
    if not dest_shipments:
        raise HTTPException(status_code=404, detail=f"No shipments found to {city}")
    return dest_shipments


@router.get("/cargo/{cargo_type}", response_model=List[Shipment])
def get_shipments_by_cargo(cargo_type: str) -> List[Shipment]:
    """Get shipments by cargo type"""
    cargo_shipments = [shipment for shipment in SHIPMENTS_DB if cargo_type.lower() in shipment.cargo_type.lower()]
    if not cargo_shipments:
        raise HTTPException(status_code=404, detail=f"No shipments found for cargo type: {cargo_type}")
    return cargo_shipments


@router.get("/{shipment_id}", response_model=Shipment)
def get_shipment(shipment_id: str) -> Shipment:
    """Get specific shipment by ID"""
    for shipment in SHIPMENTS_DB:
        if shipment.id == shipment_id:
            return shipment
    raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")


@router.get("/stats/summary")
def get_shipment_stats():
    """Get shipment statistics summary"""
    total_shipments = len(SHIPMENTS_DB)
    
    # Count by status
    status_count = {"in_transit": 0, "delivered": 0, "delayed": 0, "cancelled": 0, "pending": 0}
    for shipment in SHIPMENTS_DB:
        status_count[shipment.status] += 1
    
    # Count by priority
    priority_count = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for shipment in SHIPMENTS_DB:
        priority_count[shipment.priority] += 1
    
    # Calculate on-time delivery rate
    delivered_shipments = [s for s in SHIPMENTS_DB if s.status == "delivered" and s.actual_arrival]
    on_time_deliveries = 0
    
    for shipment in delivered_shipments:
        if shipment.actual_arrival:
            actual = datetime.fromisoformat(shipment.actual_arrival.replace('Z', '+00:00').replace('+00:00', ''))
            estimated = datetime.fromisoformat(shipment.estimated_arrival.replace('Z', '+00:00').replace('+00:00', ''))
            if actual <= estimated:
                on_time_deliveries += 1
    
    on_time_rate = (on_time_deliveries / len(delivered_shipments) * 100) if delivered_shipments else 0
    
    # Top routes
    routes = {}
    for shipment in SHIPMENTS_DB:
        route = f"{shipment.origin} → {shipment.destination}"
        routes[route] = routes.get(route, 0) + 1
    
    top_routes = sorted(routes.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Driver performance
    driver_shipments = {}
    for shipment in SHIPMENTS_DB:
        driver_id = shipment.driver_id
        if driver_id not in driver_shipments:
            driver_shipments[driver_id] = {"total": 0, "delivered": 0, "delayed": 0}
        driver_shipments[driver_id]["total"] += 1
        driver_shipments[driver_id][shipment.status] = driver_shipments[driver_id].get(shipment.status, 0) + 1
    
    # Top performing drivers (by delivery success rate)
    top_drivers = []
    for driver_id, stats in driver_shipments.items():
        if stats["total"] >= 3:  # Only drivers with 3+ shipments
            success_rate = (stats.get("delivered", 0) / stats["total"]) * 100
            top_drivers.append({"driver_id": driver_id, "success_rate": round(success_rate, 1), "total_shipments": stats["total"]})
    
    top_drivers = sorted(top_drivers, key=lambda x: x["success_rate"], reverse=True)[:5]
    
    # Recent activity (last 7 days)
    recent_date = datetime.now() - timedelta(days=7)
    recent_shipments = [
        s for s in SHIPMENTS_DB 
        if datetime.fromisoformat(s.departure_time.replace('Z', '+00:00').replace('+00:00', '')) >= recent_date
    ]
    
    # Total cargo weight and fuel consumption
    total_weight = sum(s.cargo_weight for s in SHIPMENTS_DB)
    total_fuel = sum(s.fuel_consumption for s in SHIPMENTS_DB)
    
    return {
        "total_shipments": total_shipments,
        "active_shipments": status_count["in_transit"],
        "delivered_shipments": status_count["delivered"],
        "delayed_shipments": status_count["delayed"],
        "pending_shipments": status_count["pending"],
        "cancelled_shipments": status_count["cancelled"],
        "status_breakdown": status_count,
        "priority_breakdown": priority_count,
        "on_time_delivery_rate": round(on_time_rate, 1),
        "recent_shipments_7_days": len(recent_shipments),
        "top_routes": [{"route": route, "count": count} for route, count in top_routes],
        "top_performing_drivers": top_drivers,
        "total_cargo_weight": round(total_weight, 1),
        "total_fuel_consumption": round(total_fuel, 1),
        "avg_distance": round(sum(s.distance for s in SHIPMENTS_DB) / total_shipments, 1) if total_shipments > 0 else 0,
        "cargo_types": len(set(s.cargo_type for s in SHIPMENTS_DB))
    }