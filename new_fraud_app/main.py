import asyncio
import logging
from datetime import datetime
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings

from src.domain.entities.transaction import Transaction
from src.infrastructure.agents.orchestrator_agent import OrchestratorAgent
from src.infrastructure.agents.verification_agent import VerificationAgent
from src.infrastructure.agents.report_agent import ReportAgent
from src.application.services.fraud_detection_service import FraudDetectionService
from src.infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

async def initialize_agents(client):
    """Initialize all agents with their respective configurations."""
    agents = []
    
    for agent_class in [OrchestratorAgent, VerificationAgent, ReportAgent]:
        agent_def = await client.agents.create_agent(
            model=settings.MODEL_DEPLOYMENT_NAME,
            name=agent_class.__name__,
            instructions=agent_class().get_instructions()
        )
        agents.append(agent_class(client=client, definition=agent_def))
    
    return agents

async def main():
    """Main entry point for the fraud detection system."""
    # Example transaction
    transaction = Transaction(
        transaction_id="TXN12345",
        amount=500.00,
        location="New York",
        merchant="Electronics Store",
        timestamp=datetime.utcnow()  # Add the required timestamp
    )
    
    try:
        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(credential=creds) as client
        ):
            # Initialize agents
            agents = await initialize_agents(client)
            
            # Create fraud detection service
            fraud_service = FraudDetectionService(agents)
            
            # Process transaction
            fraud_risk = await fraud_service.process_transaction(transaction)
            
            logger.info(f"Fraud risk assessment: {fraud_risk.to_dict()}")
            
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())