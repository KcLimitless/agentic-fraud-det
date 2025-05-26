from typing import Dict, Any
from ...domain.interfaces.fraud_detector_interface import FraudDetectorInterface
from ...domain.value_objects.fraud_risk import FraudRisk

class DetectFraudUseCase:
    """Use case for fraud detection."""
    
    def __init__(self, fraud_detector: FraudDetectorInterface):
        self.fraud_detector = fraud_detector

    async def execute(self, transaction: Dict[str, Any]) -> FraudRisk:
        """Execute the fraud detection use case."""
        return await self.fraud_detector.detect_fraud(transaction)