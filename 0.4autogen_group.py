import asyncio
import json
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
import json

# Create an OpenAI model client.
api_config_path = os.environ.get("api_configs")
with open(api_config_path, "r", encoding="utf-8") as f:
    api_configs = json.load(f)
    api_key = api_configs['azure-4o']['api_key']
    endpoint = api_configs['azure-4o']['base_url']
    version = api_configs['azure-4o']['api_version']


model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o",
    azure_endpoint=endpoint,
    model="gpt-4o",
    api_version=version,
    api_key=api_key,
)

# Create the primary agent.
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# Create the critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the primary and critic agents.
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)

async def main():
    # Run the team task
    result = await team.run(task="write a poem.")
    print(result.messages[-1].content)

# Run the main coroutine
asyncio.run(main())