from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class Incident(BaseModel):
    id: str
    driver_id: str
    date: str
    severity: str
    description: str


router = APIRouter()


@router.get("/", response_model=List[Incident])
def list_incidents() -> List[Incident]:
    return [
        Incident(
            id="I1001",
            driver_id="D001",
            date="2025-09-15",
            severity="high",
            description="Harsh braking detected",
        )
    ]


