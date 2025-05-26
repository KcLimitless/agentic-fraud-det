from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

@dataclass
class Transaction:
    """Core business entity representing a financial transaction."""
    transaction_id: str
    amount: Decimal
    location: str
    merchant: str
    timestamp: datetime
    currency: str = "USD"
    status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary format."""
        return {
            "transaction_id": self.transaction_id,
            "amount": float(self.amount),
            "location": self.location,
            "merchant": self.merchant,
            "timestamp": self.timestamp.isoformat(),
            "currency": self.currency,
            "status": self.status,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction instance from dictionary data."""
        return cls(
            transaction_id=data["transaction_id"],
            amount=Decimal(str(data["amount"])),
            location=data["location"],
            merchant=data["merchant"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"],
            currency=data.get("currency", "USD"),
            status=data.get("status", "pending"),
            metadata=data.get("metadata")
        )