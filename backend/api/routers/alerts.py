from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class Alert(BaseModel):
    id: str
    type: str
    message: str
    priority: str


router = APIRouter()


@router.get("/", response_model=List[Alert])
def list_alerts() -> List[Alert]:
    return [
        Alert(id="A1", type="safety", message="Driver D002 risk increased", priority="high"),
    ]


