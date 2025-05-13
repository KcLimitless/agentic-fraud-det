import asyncio
import os
import textwrap
from datetime import datetime
from pathlib import Path
import shutil

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function


# Clear the console
#os.system('cls' if os.name=='nt' else 'clear')

# Get the log files directory


# Agent Identifiers
ORCHESTRATOR_AGENT = "ORCHESTRATOR_AGENT"
VERIFICATION_AGENT = "VERIFICATION_AGENT"
REPORT_GENERATION_AGENT = "REPORT_GENERATION_AGENT"

# Orchestrator Agent Instructions
ORCHESTRATOR_AGENT_INSTRUCTIONS = """
Role: Coordinate the fraud detection workflow.

Responsibilities:
- Receive incoming transaction data.
- Forward data to the Verification Agent.
- Route verification results to the Report Generation Agent.
- Ensure smooth, structured communication between all agents.

Strict Rules:
1. Never perform fraud analysis directly.
2. Always delegate transactions to the Verification Agent.
3. If the transaction is already flagged as fraudulent, respond:
   "ORCHESTRATOR_AGENT > Fraud detected. Report generation in progress."
4. All responses must begin with:
   "ORCHESTRATOR_AGENT > {transaction_id} | "
"""

# Verification Agent Instructions
VERIFICATION_AGENT_INSTRUCTIONS = """
Role: Analyze transactions for potential fraud using advanced reasoning and historical comparison(if available).

Core Responsibilities:
- Assess transactions using Retrieval-Augmented Generation (RAG) combined with behavioral pattern analysis.
- Compare incoming transactions against historical data and user-specific norms.
- Return a structured fraud risk assessment to the Orchestrator Agent, including:
  • A fraud risk score (e.g., High, Low)
  • A clear rationale
  • Referenced behavioral anomalies or pattern matches

Key Fraud Patterns to Detect:
- **Unusual Spending Behavior**: Transactions that sharply deviate from historical amounts or categories.
- **Rapid Successive Transactions**: Multiple charges in a short period, especially across locations.
- **Location Anomalies**: Transactions from regions inconsistent with user history.
- **High-Risk Merchant Categories**: Purchases from flagged sectors (e.g., gambling, crypto).
- **Account Takeover Signs**: Sudden changes in device, login location, or account settings.
- **Split Transactions**: Sequential small charges designed to bypass detection thresholds.
- **Card Testing Attacks**: Micro-transactions indicative of stolen card validation attempts.

Rules:
1. Always compare each transaction against historical patterns before evaluating.
2. If the fraud risk is high, respond with:
   "VERIFICATION_AGENT > High fraud likelihood detected."
3. If the fraud risk is low, respond with:
   "VERIFICATION_AGENT > No fraud detected."
4. All responses must begin with:
   "VERIFICATION_AGENT > {transaction_id} | "
"""

# Report Generation Agent Instructions
REPORT_GENERATION_AGENT_INSTRUCTIONS = """
Role: Generate professional fraud detection reports based on verification results.

Responsibilities:
- Structure the analysis into a clear, concise report.
- Include the reasoning, supporting data, and actionable recommendations.

Strict Rules:
1. Never modify the verification output.
2. Tailor recommendations based on fraud classification.
3. All responses must begin with:
   "REPORT_GENERATION_AGENT > {transaction_id} | "
4. If fraud likelihood is high, include:
   "REPORT_GENERATION_AGENT > Fraud report generated."
"""

async def main():
    # Initialize Azure AI Agent settings
    ai_agent_settings = AzureAIAgentSettings()

    # Authenticate and create Azure AI client
    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True, 
            exclude_managed_identity_credential=True
        ) as creds,
        AzureAIAgent.create_client(credential=creds) as client
    ):
        # Create the agents on the Azure AI agent service
        # This code creates the agent definitions on your Azure AI Project client
        orchestrator_agent_defination = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=ORCHESTRATOR_AGENT,
            instructions=ORCHESTRATOR_AGENT_INSTRUCTIONS
        )
        verification_agent_defination = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=VERIFICATION_AGENT,
            instructions=VERIFICATION_AGENT_INSTRUCTIONS
        )
        report_generation_agent_defination = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=REPORT_GENERATION_AGENT,
            instructions=REPORT_GENERATION_AGENT_INSTRUCTIONS
        )

        # Create a Semantic Kernel agents for the Azure AI agents above
        orchestrator_agent = AzureAIAgent(
            client=client,
            agent_definition=orchestrator_agent_defination
            #plugins=[LogFilePlugin()]
        )
        verification_agent = AzureAIAgent(
            client=client,
            agent_definition=verification_agent_defination
            #plugins=[LogFilePlugin()]
        )
        report_generation_agent = AzureAIAgent(
            client=client,
            agent_definition=report_generation_agent_defination
            #plugins=[LogFilePlugin()]
        )

        # Create and add the agents to an AgentGroupChat to facilitate communication
        # 2. Create the group chat
        group_chat = AgentGroupChat(
            agents=[
                orchestrator_agent,
                verification_agent,
                report_generation_agent
            ],
            selection_strategy=SelectionStrategy(),
            termination_strategy=ApprovalTerminationStrategy(
                #agents=[report_generation_agent]
            )
        )

        # Example transaction data
        transaction_id = "TXN12345"
        transaction_data = {
            "amount": 500,
            "location": "New York",
            "merchant": "Electronics Store"
        }

        # Process the transaction
        response = await group_chat.send_message(
            ORCHESTRATOR_AGENT,
            ChatMessageContent(
                role=AuthorRole.USER,
                content=f"Transaction ID: {transaction_id}\nData: {transaction_data}"
            )
        )

        # Print the response
        print(response)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())


# class for selection strategy
class SelectionStrategy(SequentialSelectionStrategy):
    """A strategy for determining which agent should take the next turn in the chat."""

    async def select_next_agent(self, conversation_history, transaction):
        """
        Determines the next agent to act based on the current conversation state and transaction metadata.

        Args:
            conversation_history (list): A list of dicts, each with keys like 'agent' and 'content'.
            transaction (dict): Transaction metadata, may include keys like 'already_flagged'.

        Returns:
            str | None: The name of the agent to take the next turn, or None to end the conversation.
        """

        # Handle pre-flagged transactions: Orchestrator sends one message, then conversation ends
        if transaction.get("already_flagged"):
            if not any(msg["agent"] == "ORCHESTRATOR_AGENT" for msg in conversation_history):
                return "ORCHESTRATOR_AGENT"
            return None  # Already acknowledged, end conversation

        if not conversation_history:
            return "ORCHESTRATOR_AGENT"

        last_agent = conversation_history[-1]["agent"]

        if last_agent == "ORCHESTRATOR_AGENT":
            return "VERIFICATION_AGENT"

        if last_agent == "VERIFICATION_AGENT":
            return "ORCHESTRATOR_AGENT"

        if last_agent == "ORCHESTRATOR_AGENT":
            # Check if Verification Agent has given a verdict
            for msg in reversed(conversation_history):
                if msg["agent"] == "VERIFICATION_AGENT":
                    if ("High fraud likelihood" in msg["content"] or
                        "No fraud detected" in msg["content"]):
                        return "REPORT_GENERATION_AGENT"

        if last_agent == "REPORT_GENERATION_AGENT":
            return None  # End of conversation

        return None  # Fallback: no agent needed

# class for termination strategy
class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate the conversation."""

    async def should_terminate(self, conversation_history, transaction):
        """
        Determines whether the multi-agent conversation should end.

        Args:
            conversation_history (list): List of dicts with 'agent' and 'content'.
            transaction (dict): Metadata associated with the current transaction.

        Returns:
            bool: True if the chat should terminate, False otherwise.
        """

        # Terminate immediately if pre-flagged fraud has been acknowledged
        if transaction.get("already_flagged"):
            orchestrator_ack = any(
                msg["agent"] == "ORCHESTRATOR_AGENT" and
                "Fraud detected. Report generation in progress." in msg["content"]
                for msg in conversation_history
            )
            return orchestrator_ack

        # Terminate if a final report has been generated
        report_generated = any(
            msg["agent"] == "REPORT_GENERATION_AGENT" and
            "Fraud report generated." in msg["content"]
            for msg in conversation_history
        )

        # Or optionally, if the REPORT_GENERATION_AGENT has responded at all
        report_finalized = any(
            msg["agent"] == "REPORT_GENERATION_AGENT"
            for msg in conversation_history
        )

        return report_generated or report_finalized    



