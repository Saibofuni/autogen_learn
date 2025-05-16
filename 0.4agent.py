from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
import os
import asyncio
from io import BytesIO
import PIL
import requests
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image

# ATTENTION: deepseek DO NOT support mutilmodal message yet.
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

# --------------------AssistantAgent-------------------------------------
# Define a tool that searches the web for information.
# For simplicity, we will use a mock function here that returns a static string.
async def web_search(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."
web_search_function_tool = FunctionTool(web_search, description="Find information on the web")

# Create an agent that uses the Azure OpenAI GPT-4o-mini model.
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o-mini",
    azure_endpoint=os.environ.get("4omini_endpoint"),
    model="gpt-4o-mini",
    api_version="2024-12-01-preview",
    api_key=os.environ.get("4omini_api"),
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    # model_client=custom_model_client,
    tools=[web_search],
    system_message="Use tools to solve tasks.",
)

# Use asyncio.run(agent.run(...)) when running in a script.
result = asyncio.run(agent.run(task="Find information on AutoGen"))
print(result.messages[-1].content)
# --------------------------------------------------------------------------

# -------------------- MutilmodalMessage -----------------------------------
# Create a multi-modal message with random image and text.
pil_image = PIL.Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
img = Image(pil_image)
multi_modal_message = MultiModalMessage(content=["Can you describe the content of this image?", img], source="user")

# Use asyncio.run(...) when running in a script.
result = asyncio.run(agent.run(task=multi_modal_message))
print(result.messages[-1].content)  # type: ignore
# --------------------------------------------------------------------------

#---------------------------- StreamMessage ------------------------------
async def assistant_run_stream() -> None:
    # Option 1: read each message from the stream (as shown in the previous example).
    # async for message in agent.run_stream(task="Find information on AutoGen"):
    #     print(message)

    # Option 2: use Console to print all messages as they appear.
    await Console(
        agent.run_stream(task="Find information on AutoGen"),
        output_stats=True,  # Enable stats printing.
    )


# Use asyncio.run(assistant_run_stream()) when running in a script.
asyncio.run(assistant_run_stream())
# ---------------------------------------------------------------------------

# ---------------------------- StructuredOutput ------------------------------
from typing import Literal
from pydantic import BaseModel

# The response format for the agent as a Pydantic base model.
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]


# Create an agent that uses the OpenAI GPT-4o model.
agent = AssistantAgent(
    "assistant",
    model_client=model_client,
    system_message="Categorize the input as happy, sad, or neutral following the JSON format.",
    # Define the output content type of the agent.
    output_content_type=AgentResponse,
)

result = asyncio.run(Console(agent.run_stream(task="I am happy.")))

# Check the last message in the result, validate its type, and print the thoughts and response.
assert isinstance(result.messages[-1], StructuredMessage)
assert isinstance(result.messages[-1].content, AgentResponse)
print("Thought: ", result.messages[-1].content.thoughts)
print("Response: ", result.messages[-1].content.response)
asyncio.run(model_client.close())
# ---------------------------------------------------------------------------

# ---------------------------- Use McpWorkbench ------------------------------
# Get the fetch tool from mcp-server-fetch.
# fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])

# # Create an async function to use the MCP workbench and agent.
# async def run_fetch_agent():
#     # Create an MCP workbench which provides a session to the mcp server.
#     async with McpWorkbench(fetch_mcp_server) as workbench:  # type: ignore
#         # Create an agent that can use the fetch tool.
#         fetch_agent = AssistantAgent(
#             name="fetcher", model_client=model_client, workbench=workbench, reflect_on_tool_use=True
#         )

#         # Let the agent fetch the content of a URL and summarize it.
#         result = await fetch_agent.run(task="Summarize the content of https://en.wikipedia.org/wiki/Seattle")
#         assert isinstance(result.messages[-1], TextMessage)
#         print(result.messages[-1].content)

#         # Close the connection to the model client.
#         await model_client.close()

# # Run the async function.
# asyncio.run(run_fetch_agent())
# ---------------------------------------------------------------------------