from fastapi import APIRouter
from pydantic import BaseModel


class AIQuery(BaseModel):
    question: str


class AIAnswer(BaseModel):
    answer: str
    sources: list[str]


router = APIRouter()


@router.post("/query", response_model=AIAnswer)
def query_ai(payload: AIQuery) -> AIAnswer:
    return AIAnswer(
        answer=f"Live answer stub: {payload.question}",
        sources=["pathway:index:drivers", "pathway:index:incidents"],
    )


