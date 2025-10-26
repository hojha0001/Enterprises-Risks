from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import random

from ..database import get_session
from ..models import RiskRecord

router = APIRouter(tags=["risk"])


@router.post("/risk/score")
def score(payload: dict, session: Session = Depends(get_session)):
    """Compute a score and persist a RiskRecord for dashboarding."""
    # basic validation
    eid = payload.get("entity_id") or payload.get("client_id")
    if not eid:
        raise HTTPException(status_code=400, detail="entity_id or client_id is required")

    # compute dummy score (replace with real model)
    sc = float(random.uniform(0, 100))

    rec = RiskRecord(
        entity_id=eid,
        score=sc,
        model=payload.get("model", "v1"),
        label=payload.get("label"),
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    resp = {"entity_id": rec.entity_id, "score": rec.score, "created_at": rec.created_at.isoformat()}
    # keep backward-compatible key for tests / clients that use client_id
    if payload.get("client_id"):
        resp["client_id"] = payload.get("client_id")
    return resp
