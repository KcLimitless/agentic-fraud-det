from abc import ABC, abstractmethod
from typing import Any, Dict
from ..value_objects.fraud_risk import FraudRisk

class FraudDetectorInterface(ABC):
    """Interface for fraud detection services."""
    
    @abstractmethod
    async def detect_fraud(self, transaction: Dict[str, Any]) -> FraudRisk:
        """Detect fraud in a transaction."""
        pass