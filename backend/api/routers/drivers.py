from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List


class Driver(BaseModel):
    id: str
    name: str
    license_number: str
    risk_score: float = 0.0
    status: str = "active"
    phone: str = ""
    location: str = ""


router = APIRouter()

# Database of 40 drivers with realistic Indian names and data
DRIVERS_DB = [
    Driver(id="D001", name="Aman Singh", license_number="PB12-3456", risk_score=0.12, status="active", phone="+91-98765-43210", location="Chandigarh"),
    Driver(id="D002", name="Priya Verma", license_number="PB09-7890", risk_score=0.45, status="active", phone="+91-98765-43211", location="Ludhiana"),
    Driver(id="D003", name="Rajesh Kumar", license_number="DL15-2468", risk_score=0.78, status="active", phone="+91-98765-43212", location="Delhi"),
    Driver(id="D004", name="Sunita Sharma", license_number="HR08-1357", risk_score=0.23, status="active", phone="+91-98765-43213", location="Gurugram"),
    Driver(id="D005", name="Vikram Patel", license_number="GJ01-9876", risk_score=0.67, status="active", phone="+91-98765-43214", location="Ahmedabad"),
    Driver(id="D006", name="Neha Gupta", license_number="UP32-5432", risk_score=0.19, status="active", phone="+91-98765-43215", location="Noida"),
    Driver(id="D007", name="Arjun Yadav", license_number="RJ14-8765", risk_score=0.82, status="active", phone="+91-98765-43216", location="Jaipur"),
    Driver(id="D008", name="Kavita Joshi", license_number="MH01-4321", risk_score=0.34, status="active", phone="+91-98765-43217", location="Mumbai"),
    Driver(id="D009", name="Deepak Choudhary", license_number="KA03-7654", risk_score=0.56, status="active", phone="+91-98765-43218", location="Bangalore"),
    Driver(id="D010", name="Anita Reddy", license_number="TN07-2109", risk_score=0.28, status="active", phone="+91-98765-43219", location="Chennai"),
    Driver(id="D011", name="Sanjay Mehta", license_number="GJ05-8642", risk_score=0.71, status="active", phone="+91-98765-43220", location="Surat"),
    Driver(id="D012", name="Pooja Agarwal", license_number="UP80-3579", risk_score=0.41, status="active", phone="+91-98765-43221", location="Lucknow"),
    Driver(id="D013", name="Rahul Bansal", license_number="DL08-9513", risk_score=0.15, status="active", phone="+91-98765-43222", location="New Delhi"),
    Driver(id="D014", name="Meera Shah", license_number="MH14-7531", risk_score=0.63, status="active", phone="+91-98765-43223", location="Pune"),
    Driver(id="D015", name="Ashok Tiwari", license_number="MP09-1593", risk_score=0.89, status="on_leave", phone="+91-98765-43224", location="Bhopal"),
    Driver(id="D016", name="Ritu Malhotra", license_number="PB13-7419", risk_score=0.32, status="active", phone="+91-98765-43225", location="Amritsar"),
    Driver(id="D017", name="Manoj Kumar", license_number="BR01-8520", risk_score=0.52, status="active", phone="+91-98765-43226", location="Patna"),
    Driver(id="D018", name="Sneha Kapoor", license_number="JK01-9630", risk_score=0.74, status="active", phone="+91-98765-43227", location="Jammu"),
    Driver(id="D019", name="Ajay Mishra", license_number="UP15-1472", risk_score=0.38, status="active", phone="+91-98765-43228", location="Kanpur"),
    Driver(id="D020", name="Divya Sinha", license_number="WB07-2583", risk_score=0.26, status="active", phone="+91-98765-43229", location="Kolkata"),
    Driver(id="D021", name="Rohit Sharma", license_number="HR12-4567", risk_score=0.47, status="active", phone="+91-98765-43230", location="Faridabad"),
    Driver(id="D022", name="Seema Jain", license_number="RJ09-8901", risk_score=0.61, status="active", phone="+91-98765-43231", location="Udaipur"),
    Driver(id="D023", name="Amit Chadha", license_number="PB16-2345", risk_score=0.29, status="active", phone="+91-98765-43232", location="Jalandhar"),
    Driver(id="D024", name="Nisha Rajan", license_number="KL14-6789", risk_score=0.84, status="active", phone="+91-98765-43233", location="Kochi"),
    Driver(id="D025", name="Sunil Rao", license_number="AP05-3456", risk_score=0.16, status="active", phone="+91-98765-43234", location="Hyderabad"),
    Driver(id="D026", name="Rashmi Singh", license_number="UP45-7890", risk_score=0.53, status="active", phone="+91-98765-43235", location="Agra"),
    Driver(id="D027", name="Kiran Yadav", license_number="MP14-1234", risk_score=0.72, status="active", phone="+91-98765-43236", location="Indore"),
    Driver(id="D028", name="Harish Gupta", license_number="DL22-5678", risk_score=0.31, status="active", phone="+91-98765-43237", location="Ghaziabad"),
    Driver(id="D029", name="Renu Kumari", license_number="BR09-9012", risk_score=0.48, status="active", phone="+91-98765-43238", location="Gaya"),
    Driver(id="D030", name="Varun Khanna", license_number="CH01-3456", risk_score=0.25, status="active", phone="+91-98765-43239", location="Chandigarh"),
    Driver(id="D031", name="Preeti Agarwal", license_number="UP67-7890", risk_score=0.66, status="active", phone="+91-98765-43240", location="Varanasi"),
    Driver(id="D032", name="Arun Nair", license_number="KL08-1234", risk_score=0.43, status="active", phone="+91-98765-43241", location="Thiruvananthapuram"),
    Driver(id="D033", name="Geeta Bhatia", license_number="GJ12-5678", risk_score=0.77, status="on_leave", phone="+91-98765-43242", location="Rajkot"),
    Driver(id="D034", name="Naveen Reddy", license_number="TG15-9012", risk_score=0.35, status="active", phone="+91-98765-43243", location="Warangal"),
    Driver(id="D035", name="Sonia Chopra", license_number="PB18-3456", risk_score=0.58, status="active", phone="+91-98765-43244", location="Bathinda"),
    Driver(id="D036", name="Dinesh Panchal", license_number="GJ20-7890", risk_score=0.91, status="active", phone="+91-98765-43245", location="Vadodara"),
    Driver(id="D037", name="Lalita Devi", license_number="RJ11-1234", risk_score=0.22, status="active", phone="+91-98765-43246", location="Jodhpur"),
    Driver(id="D038", name="Subhash Pal", license_number="UP89-5678", risk_score=0.64, status="active", phone="+91-98765-43247", location="Allahabad"),
    Driver(id="D039", name="Manju Thakur", license_number="HP07-9012", risk_score=0.39, status="active", phone="+91-98765-43248", location="Shimla"),
    Driver(id="D040", name="Santosh Kumar", license_number="JH03-3456", risk_score=0.81, status="active", phone="+91-98765-43249", location="Ranchi")
]


@router.get("/", response_model=List[Driver])
def list_drivers() -> List[Driver]:
    """Get all drivers"""
    return DRIVERS_DB


@router.get("/high-risk", response_model=List[Driver])
def get_high_risk_drivers() -> List[Driver]:
    """Get drivers with risk score > 0.6"""
    return [driver for driver in DRIVERS_DB if driver.risk_score > 0.6]


@router.get("/active", response_model=List[Driver])
def get_active_drivers() -> List[Driver]:
    """Get only active drivers"""
    return [driver for driver in DRIVERS_DB if driver.status == "active"]


@router.get("/{driver_id}", response_model=Driver)
def get_driver(driver_id: str) -> Driver:
    """Get specific driver by ID"""
    for driver in DRIVERS_DB:
        if driver.id == driver_id:
            return driver
    raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")


@router.get("/stats/summary")
def get_driver_stats():
    """Get driver statistics summary"""
    total_drivers = len(DRIVERS_DB)
    active_drivers = len([d for d in DRIVERS_DB if d.status == "active"])
    high_risk_drivers = len([d for d in DRIVERS_DB if d.risk_score > 0.6])
    critical_risk_drivers = len([d for d in DRIVERS_DB if d.risk_score > 0.8])
    
    avg_risk_score = sum(d.risk_score for d in DRIVERS_DB) / total_drivers if total_drivers > 0 else 0
    
    return {
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "on_leave_drivers": total_drivers - active_drivers,
        "high_risk_drivers": high_risk_drivers,
        "critical_risk_drivers": critical_risk_drivers,
        "average_risk_score": round(avg_risk_score, 3),
        "risk_distribution": {
            "low_risk": len([d for d in DRIVERS_DB if d.risk_score <= 0.3]),
            "medium_risk": len([d for d in DRIVERS_DB if 0.3 < d.risk_score <= 0.6]),
            "high_risk": len([d for d in DRIVERS_DB if 0.6 < d.risk_score <= 0.8]),
            "critical_risk": len([d for d in DRIVERS_DB if d.risk_score > 0.8])
        }
    }