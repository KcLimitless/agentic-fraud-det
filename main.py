import asyncio
import os
import textwrap
from datetime import datetime
from pathlib import Path

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

# Agent Identifiers
ORCHESTRATOR_AGENT = "ORCHESTRATOR_AGENT"
VERIFICATION_AGENT = "VERIFICATION_AGENT"
REPORT_GENERATION_AGENT = "REPORT_GENERATION_AGENT"

# Instructions
ORCHESTRATOR_AGENT_INSTRUCTIONS = """
Role: Coordinate the fraud detection workflow.
Responsibilities:
- Receive incoming transaction data.
- Forward data to the Verification Agent.
- Route verification results to the Report Generation Agent.
- Ensure structured communication.
Strict Rules:
1. Never perform fraud analysis directly.
2. Always delegate transactions to the Verification Agent.
3. If already flagged: "ORCHESTRATOR_AGENT > Fraud detected. Report generation in progress."
4. Prefix all messages with: "ORCHESTRATOR_AGENT > {transaction_id} | "
"""

VERIFICATION_AGENT_INSTRUCTIONS = """
Role: Analyze transactions using RAG and historical patterns.
Key Patterns:
- Unusual Spending, Rapid Transactions, Location Anomalies, High-Risk Merchants,
  Account Takeovers, Split Transactions, Card Testing.
Rules:
1. Compare with historical data before assessing.
2. High risk: "VERIFICATION_AGENT > High fraud likelihood detected."
3. Low risk: "VERIFICATION_AGENT > No fraud detected."
4. Prefix all messages with: "VERIFICATION_AGENT > {transaction_id} | "
"""

REPORT_GENERATION_AGENT_INSTRUCTIONS = """
Role: Compile a structured fraud report.
Rules:
1. Never modify verification output.
2. Provide recommendations based on findings.
3. Prefix all messages with: "REPORT_GENERATION_AGENT > {transaction_id} | "
4. If high risk: Include "Fraud report generated."
"""

# Selection Strategy
class SelectionStrategy(SequentialSelectionStrategy):
    def __init__(self, transaction):
        self.transaction = transaction

    async def select_next_agent(self, conversation_history):
        transaction = self.transaction

        if transaction.get("already_flagged"):
            if not any(msg["agent"] == ORCHESTRATOR_AGENT for msg in conversation_history):
                return ORCHESTRATOR_AGENT
            return None

        if not conversation_history:
            return ORCHESTRATOR_AGENT

        last_agent = conversation_history[-1]["agent"]

        if last_agent == ORCHESTRATOR_AGENT:
            for msg in reversed(conversation_history):
                if msg["agent"] == VERIFICATION_AGENT:
                    if "High fraud likelihood" in msg["content"] or "No fraud detected" in msg["content"]:
                        return REPORT_GENERATION_AGENT
            return VERIFICATION_AGENT

        if last_agent == VERIFICATION_AGENT:
            return ORCHESTRATOR_AGENT

        if last_agent == REPORT_GENERATION_AGENT:
            return None

        return None

# Termination Strategy
class ApprovalTerminationStrategy(TerminationStrategy):
    def __init__(self, transaction):
        self.transaction = transaction

    async def should_terminate(self, conversation_history):
        transaction = self.transaction

        if transaction.get("already_flagged"):
            return any(
                msg["agent"] == ORCHESTRATOR_AGENT and
                "Fraud detected. Report generation in progress." in msg["content"]
                for msg in conversation_history
            )

        return any(
            msg["agent"] == REPORT_GENERATION_AGENT and
            "Fraud report generated." in msg["content"]
            for msg in conversation_history
        )

# Main async function
async def main():
    transaction_id = "TXN12345"
    transaction_data = {
        "transaction_id": transaction_id,
        "amount": 500,
        "location": "New York",
        "merchant": "Electronics Store",
        # "already_flagged": True  # Uncomment to simulate pre-flagged fraud
    }

    ai_agent_settings = AzureAIAgentSettings()

    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        ) as creds,
        AzureAIAgent.create_client(credential=creds) as client
    ):
        orchestrator_def = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=ORCHESTRATOR_AGENT,
            instructions=ORCHESTRATOR_AGENT_INSTRUCTIONS
        )
        verification_def = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=VERIFICATION_AGENT,
            instructions=VERIFICATION_AGENT_INSTRUCTIONS
        )
        report_def = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=REPORT_GENERATION_AGENT,
            instructions=REPORT_GENERATION_AGENT_INSTRUCTIONS
        )

        orchestrator_agent = AzureAIAgent(client=client, agent_definition=orchestrator_def)
        verification_agent = AzureAIAgent(client=client, agent_definition=verification_def)
        report_agent = AzureAIAgent(client=client, agent_definition=report_def)

        selection = SelectionStrategy(transaction_data)
        termination = ApprovalTerminationStrategy(transaction_data)

        group_chat = AgentGroupChat(
            agents=[orchestrator_agent, verification_agent, report_agent],
            selection_strategy=selection,
            termination_strategy=termination
        )

        conversation_history = []

        initial_message = ChatMessageContent(
            role=AuthorRole.USER,
            content=f"Transaction ID: {transaction_id}\nData: {transaction_data}"
        )
        conversation_history.append({"agent": "USER", "content": initial_message.content})

        while not await group_chat.should_terminate(conversation_history):
            next_agent = await group_chat.select_next_agent(conversation_history)

            if not next_agent:
                break

            response = await next_agent.chat(conversation_history, transaction_data)

            print(f"{next_agent.name} Response:\n{textwrap.indent(response.content, '    ')}\n")

            conversation_history.append({
                "agent": next_agent.name,
                "content": response.content
            })

        print("\nFull Conversation History:\n" + "-" * 50)
        for msg in conversation_history:
            print(f"{msg['agent']}:")
            print(textwrap.indent(msg['content'], '    '))
            print("-")

if __name__ == "__main__":
    asyncio.run(main())
