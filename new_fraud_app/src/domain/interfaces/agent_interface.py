from abc import ABC, abstractmethod
from typing import Any, Dict
from semantic_kernel.contents.chat_message_content import ChatMessageContent

class AgentInterface(ABC):
    """Interface for all agents in the system."""
    
    @abstractmethod
    async def process(self, transaction: Dict[str, Any]) -> ChatMessageContent:
        """Process a transaction and return a response."""
        pass

    @abstractmethod
    def get_instructions(self) -> str:
        """Return the agent's instructions."""
        pass