from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class FraudRisk:
    """Value object representing fraud risk assessment."""
    level: RiskLevel
    score: float
    reasons: List[str]
    confidence: float
    metadata: Optional[dict] = None

    def is_high_risk(self) -> bool:
        return self.level == RiskLevel.HIGH

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "score": self.score,
            "reasons": self.reasons,
            "confidence": self.confidence,
            "metadata": self.metadata
        }