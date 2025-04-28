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

# human can input after termination and the input message will be used as the user prompt for the agent. If the user input is "exit", the agent will be terminated.
user_proxy = ConversableAgent(
    name="UserProxy",
    system_message="You are a user proxy. You will be used to generate the user prompt for the agent. You will not be used to generate the agent's response. You will only be used to generate the user prompt for the agent. You will not be used to generate the agent's response.",
    llm_config={"config_list": config_list},
    human_input_mode="TERMINATE",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
)

assistant = ConversableAgent(
    name="Assistant",
    system_message="You are an assistant help to solve math problems. IF ALL PROBLEM ARE SOLVED, PLEASE SAY 'TERMINATE'.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

print("human input mode is set to 'TERMINATE'")
chat = user_proxy.initiate_chat(
    assistant,
    message="Figure the math problem below:\n\n1. What is the sum of 1 and 2?\n2. What is the product of 3 and 4?\n3. What is the difference between 5 and 6?\n4. What is the quotient of 7 and 8?\n5. What is the square root of 9?\n6. What is the cube root of 27?\n7. What is the factorial of 5?\n8. What is the sine of 30 degrees?\n9. What is the cosine of 60 degrees?\n10. What is the tangent of 45 degrees?",
)

# human input is always requested and the human can choose to skip, intercept , or terminate the conversation.
user_proxy.human_input_mode = "ALWAYS"

print("human input mode is set to 'ALWAYS'")
chat = user_proxy.initiate_chat(
    assistant,
    message="Figure the math problem below:\n\n1. What is the sum of 1 and 2?\n2. What is the product of 3 and 4?\n3. What is the difference between 5 and 6?\n4. What is the quotient of 7 and 8?\n5. What is the square root of 9?\n6. What is the cube root of 27?\n7. What is the factorial of 5?\n8. What is the sine of 30 degrees?\n9. What is the cosine of 60 degrees?\n10. What is the tangent of 45 degrees?",
)