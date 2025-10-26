from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, col, text

from ..database import get_session
from ..models import RiskRecord

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/timeseries", response_model=List[RiskRecord])
def timeseries(
    entity_id: Optional[str] = None,
    label: Optional[str] = None,
    model: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(500, le=5000),
    offset: int = 0,
    session: Session = Depends(get_session),
):
    stmt = select(RiskRecord)
    if entity_id:
        stmt = stmt.where(RiskRecord.entity_id == entity_id)
    if label:
        stmt = stmt.where(RiskRecord.label == label)
    if model:
        stmt = stmt.where(RiskRecord.model == model)
    if min_score is not None:
        stmt = stmt.where(RiskRecord.score >= min_score)
    if max_score is not None:
        stmt = stmt.where(RiskRecord.score <= max_score)
    if start:
        stmt = stmt.where(RiskRecord.created_at >= start)
    if end:
        stmt = stmt.where(RiskRecord.created_at <= end)
    stmt = stmt.order_by(col(RiskRecord.created_at).asc()).limit(limit).offset(offset)
    return session.exec(stmt).all()


@router.get("/aggregate/day")
def aggregate_day(
    entity_id: Optional[str] = None,
    session: Session = Depends(get_session),
):
    # SQLite daily buckets via strftime
    q = """
      SELECT strftime('%Y-%m-%d', created_at) as day, AVG(score) as avg_score, COUNT(*) as n
      FROM riskrecord
      {where}
      GROUP BY day
      ORDER BY day ASC
    """
    where = "WHERE entity_id = :eid" if entity_id else ""
    rows = session.exec(text(q.format(where=where)), {"eid": entity_id} if entity_id else {}).all()
    return [{"day": d, "avg_score": a, "n": n} for d, a, n in rows]
