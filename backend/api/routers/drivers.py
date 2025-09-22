from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class Driver(BaseModel):
    id: str
    name: str
    license_number: str
    risk_score: float = 0.0


router = APIRouter()


@router.get("/", response_model=List[Driver])
def list_drivers() -> List[Driver]:
    return [
        Driver(id="D001", name="Aman Singh", license_number="PB12-3456", risk_score=0.12),
        Driver(id="D002", name="Priya Verma", license_number="PB09-7890", risk_score=0.45),
    ]


@router.get("/{driver_id}", response_model=Driver)
def get_driver(driver_id: str) -> Driver:
    return Driver(id=driver_id, name="Demo Driver", license_number="PB00-0000", risk_score=0.25)


