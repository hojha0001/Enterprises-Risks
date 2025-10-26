from datetime import datetime
import random
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from sqlmodel import Session, select

from . import models
from .database import init_db, get_session


app = FastAPI(
    title="Enterprise Risk Intelligence System API",
    version="0.1.0",
    description="API for assessing and monitoring enterprise risks",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/risk/score", response_model=models.RiskResponse)
def calculate_risk_score(
    risk_input: models.RiskScore,
    session: Session = Depends(get_session),
):
    """Calculate a dummy risk score and log the request to SQLite."""
    # Dummy risk calculation - replace with actual risk model
    score = random.uniform(0, 100)

    # Log the request to the RiskRequest table
    risk_request = models.RiskRequest(
        client_id=risk_input.client_id,
        risk_factors=risk_input.risk_factors,
        score=score,
    )
    session.add(risk_request)
    session.commit()

    # Also persist into RiskHistory for trend analysis
    history = models.RiskHistory(
        client_id=risk_input.client_id,
        score=score,
        risk_factors=risk_input.risk_factors,
    )
    session.add(history)
    session.commit()

    return models.RiskResponse(
        client_id=risk_input.client_id,
        score=score,
        timestamp=datetime.utcnow(),
    )


@app.post("/risk/history", response_model=models.RiskHistoryRead)
def create_history_entry(
    item: models.RiskHistoryCreate,
    session: Session = Depends(get_session),
):
    """Create a historical record (useful for importing or manual entries)."""
    timestamp = item.timestamp or datetime.utcnow()
    record = models.RiskHistory(
        client_id=item.client_id,
        score=item.score,
        timestamp=timestamp,
        risk_factors=item.risk_factors,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return models.RiskHistoryRead(
        id=record.id,
        client_id=record.client_id,
        timestamp=record.timestamp,
        score=record.score,
        risk_factors=record.risk_factors,
    )


@app.get("/risk/history", response_model=List[models.RiskHistoryRead])
def query_history(
    client_id: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Query historical risk scores. Optional filters: client_id, start, end, limit."""
    q = select(models.RiskHistory)
    if client_id:
        q = q.where(models.RiskHistory.client_id == client_id)
    if start:
        q = q.where(models.RiskHistory.timestamp >= start)
    if end:
        q = q.where(models.RiskHistory.timestamp <= end)
    q = q.limit(limit)
    results = session.exec(q).all()
    return [
        models.RiskHistoryRead(
            id=r.id,
            client_id=r.client_id,
            timestamp=r.timestamp,
            score=r.score,
            risk_factors=r.risk_factors,
        )
        for r in results
    ]
