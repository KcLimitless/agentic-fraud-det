from typing import Dict, Any, List
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

from ...domain.interfaces.agent_interface import AgentInterface
from ...domain.entities.transaction import Transaction
from ...domain.value_objects.fraud_risk import FraudRisk, RiskLevel

class FraudDetectionService:
    """Service coordinating fraud detection workflow."""

    def __init__(self, agents: List[AgentInterface]):
        self.agents = agents
        self.group_chat = AgentGroupChat()

    async def process_transaction(self, transaction: Transaction) -> FraudRisk:
        """Process a transaction through the fraud detection workflow."""
        # Initialize conversation
        initial_message = ChatMessageContent(
            role=AuthorRole.USER,
            content=f"Transaction ID: {transaction.transaction_id}\nData: {transaction.to_dict()}"
        )
        await self.group_chat.add_chat_message(initial_message)

        # Process through agents
        async for message in self.group_chat.invoke(transaction.to_dict()):
            if "High fraud likelihood detected" in message.content:
                return FraudRisk(
                    level=RiskLevel.HIGH,
                    score=0.9,
                    reasons=["High risk transaction detected"],
                    confidence=0.95
                )

        return FraudRisk(
            level=RiskLevel.LOW,
            score=0.1,
            reasons=["No suspicious patterns detected"],
            confidence=0.95
        )