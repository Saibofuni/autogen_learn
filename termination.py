from autogen import ConversableAgent
import os

api_key = os.getenv("4o_api")
base_url = os.getenv("4o_endpoint")
config_list = {
    "model": "gpt-4o",
    "api_key": api_key,
    "api_type": "azure",
    "base_url": base_url,
    "api_version": "2024-12-01-preview",
}

# use message to end the conversation
user_proxy = ConversableAgent(
    name="User_Proxy",
    system_message="You are a user proxy. You will ask the agents to do some math operations.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATION" in msg["content"],
)

assistant = ConversableAgent(
    name="Assistant",
    system_message="You are an assistant. You will do some math operations. If the tast is done, you need to return 'TERMINATION' to the user proxy.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

print("use message to end the conversation")

chat_message = user_proxy.initiate_chat(
    assistant,
    message="Please add 1 to 2 and return the result.",
)
#---------------------------------------------------------------------

# set the max turn to end the conversation

print("set the max turn to end the conversation")
chat_message = user_proxy.initiate_chat(
    assistant,
    message="Please add 1 to 2 and return the result.",
    max_turn=3,
)
#---------------------------------------------------------------------

# set the max_consecutive_auto_reply inside the agent
user_proxy2 = ConversableAgent(
    name="User_Proxy",
    system_message="You are a user proxy. You will ask the agents to do some math operations.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)

assistant2 = ConversableAgent(
    name="Assistant",
    system_message="You are an assistant. You will do some math operations. If the tast is done, you need to return 'TERMINATION' to the user proxy.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

print("set the max_consecutive_auto_reply inside the agent")

chat_message = user_proxy2.initiate_chat(
    assistant2,
    message="Please add 1 to 2 and return the result.",
)#---------------------------------------------------------------------