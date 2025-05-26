from semantic_kernel.agents import AzureAIAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from typing import Any, Dict

from ...domain.interfaces.agent_interface import AgentInterface

class OrchestratorAgent(AgentInterface):
    """Implementation of the orchestrator agent."""

    def __init__(self, client: Any, definition: Any):
        self.agent = AzureAIAgent(client=client, definition=definition)

    def get_instructions(self) -> str:
        return """
        Role: Coordinate the fraud detection workflow.
        Responsibilities:
        - Receive incoming transaction data.
        - Forward data to the Verification Agent.
        - Route verification results to the Report Generation Agent.
        Strict Rules:
        1. Never perform fraud analysis directly.
        2. Always delegate transactions to the Verification Agent.
        3. Prefix all messages with: "ORCHESTRATOR_AGENT > {transaction_id} | "
        """

    async def process(self, transaction: Dict[str, Any]) -> ChatMessageContent:
        return await self.agent.process(transaction)