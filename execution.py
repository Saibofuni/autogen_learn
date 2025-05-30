from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor
import tempfile
import os

api_key = os.environ.get("4o_api")
base_url = os.environ.get("4o_endpoint")
config_list = {
    "model": "gpt-4o",
    "api_key": api_key,
    "api_type": "azure",
    "base_url": base_url,
    "api_version": "2024-12-01-preview",
}

temp_dir = tempfile.TemporaryDirectory()

# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

user_agent = ConversableAgent(
    "User_Agent",
    llm_config=False,
    code_execution_config={"executor":executor},
    human_input_mode="NEVER",
)

code_writer_system_message = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.
"""

assistant = ConversableAgent(
    "Assistant_Agent",
    system_message=code_writer_system_message,
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
)

chat = user_agent.initiate_chat(
    assistant,
    message="write python code 'Hello World'.",
)

temp_dir.cleanup() # clean up the tempfile

# use docker to execute code
# strongly suggest to use this way. YOU NEED TO INSTALL DOCKER FIRST




# a simple way to execute code
# autogen has already provided you with a simple way to execute code using docker.
from autogen import AssistantAgent
from autogen import UserProxyAgent

executor_agent = UserProxyAgent(
    "Executor_Agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="ALWAYS",
)

code_agent = AssistantAgent(
    "code_agent",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

chat_message = executor_agent.initiate_chat(
    code_agent,
    message="write python code 'Hello World'.",
)