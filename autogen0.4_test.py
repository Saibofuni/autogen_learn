from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import asyncio
import os
import json

# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
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

# use the following line if you want to use OpenAI API instead of Azure OpenAI
'''
from autogen_ext.models.openai import OpenAIChatCompletionClient
model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-xxx")
'''
# use the following line if you want to use other API
'''
from autogen_ext.models.openai import OpenAIChatCompletionClient
custom_model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("deepseek_api"),
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True,
    },
)
'''

# Define a simple function tool that the agent can use.
# For this example, we use a fake weather tool for demonstration purposes.
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."


# Define an AssistantAgent with the model, tool, system message, and reflection enabled.
# The system message instructs the agent via natural language.
agent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    # model_client=custom_model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # Enable streaming tokens from the model client.
)


# Run the agent and stream the messages to the console.
async def main() -> None:
    await Console(agent.run_stream(task="What is the weather in New York?"))
    # Close the connection to the model client.
    await model_client.close()


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
