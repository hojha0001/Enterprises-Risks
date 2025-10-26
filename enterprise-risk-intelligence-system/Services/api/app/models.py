from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class RiskRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True)
    request_time: datetime = Field(default_factory=datetime.utcnow)
    risk_factors: Dict[str, Any] = Field(sa_type=JSON)
    score: float


class RiskScore(SQLModel):
    client_id: str
    risk_factors: Dict[str, Any]


class RiskResponse(SQLModel):
    client_id: str
    score: float
    timestamp: datetime


# Historical scores stored as a separate table for querying trends
class RiskHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: float
    # optional payload to store the risk factors that produced the score
    risk_factors: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class RiskHistoryCreate(SQLModel):
    client_id: str
    score: float
    timestamp: Optional[datetime] = None
    risk_factors: Optional[Dict[str, Any]] = None


class RiskHistoryRead(SQLModel):
    id: int
    client_id: str
    timestamp: datetime
    score: float
    risk_factors: Optional[Dict[str, Any]] = None