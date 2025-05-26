from semantic_kernel.agents import AzureAIAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from typing import Any, Dict

from ...domain.interfaces.agent_interface import AgentInterface

class VerificationAgent(AgentInterface):
    """Implementation of the verification agent."""

    def __init__(self, client: Any, definition: Any):
        self.agent = AzureAIAgent(client=client, definition=definition)

    def get_instructions(self) -> str:
        return """
        Role: Analyze transactions using RAG and historical patterns.
        Key Fraud Patterns:
        - Unusual Spending, Rapid Transactions, Location Anomalies, High-Risk Merchants, Account Takeovers, Split Transactions, Card Testing.
        Rules:
        1. Compare with historical data before assessing.
        2. High risk: "VERIFICATION_AGENT > High fraud likelihood detected."
        3. Low risk: "VERIFICATION_AGENT > No fraud detected."
        4. Prefix all messages with: "VERIFICATION_AGENT > {transaction_id} | "
        """

    async def process(self, transaction: Dict[str, Any]) -> ChatMessageContent:
        return await self.agent.process(transaction)