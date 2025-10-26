from fastapi import FastAPI, Depends
from sqlmodel import Session
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from .database import get_session, create_db_and_tables
from .models import RiskAssessment

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

class RiskRequest(BaseModel):
    entity_name: str
    risk_factors: List[str]
    context: str | None = None

class RiskResponse(BaseModel):
    id: int
    risk_score: float
    confidence: float
    factors: List[str]
    entity_name: str
    context: str | None = None
    created_at: str
    updated_at: str

app = FastAPI(
    title="Enterprise Risk Intelligence System",
    lifespan=lifespan
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/risk/score", response_model=RiskResponse)
async def calculate_risk_score(request: RiskRequest, session: Session = Depends(get_session)):
    # TODO: Implement actual risk scoring logic
    risk_assessment = RiskAssessment(
        entity_name=request.entity_name,
        risk_score=0.5,  # Placeholder
        confidence=0.8,  # Placeholder
        factors=",".join(request.risk_factors),
        context=request.context
    )
    
    session.add(risk_assessment)
    session.commit()
    session.refresh(risk_assessment)
    
    return risk_assessment.to_dict()