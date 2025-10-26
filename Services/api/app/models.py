from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class RiskAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entity_name: str
    risk_score: float
    confidence: float
    factors: str  # Stored as comma-separated values
    context: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "entity_name": self.entity_name,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "factors": self.factors.split(",") if self.factors else [],
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }