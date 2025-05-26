from semantic_kernel.agents import AzureAIAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from typing import Any, Dict

from ...domain.interfaces.agent_interface import AgentInterface

class ReportAgent(AgentInterface):
    """Implementation of the report generation agent."""

    def __init__(self, client: Any, definition: Any):
        self.agent = AzureAIAgent(client=client, definition=definition)

    def get_instructions(self) -> str:
        return """
        Role: Compile a structured fraud report.
        Rules:
        1. Never modify verification output.
        2. Provide recommendations based on findings.
        3. Prefix all messages with: "REPORT_GENERATION_AGENT > {transaction_id} | "
        4. If high risk: Include "Fraud report generated."
        """

    async def process(self, transaction: Dict[str, Any]) -> ChatMessageContent:
        return await self.agent.process(transaction)