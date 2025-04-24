# 注意llm_config的配置，默认配置是openai，需要自行更改。
# 此处使用的是azure的openai，使用时需要在环境变量中设置AZURE_OPENAI_API_KEY和AZURE_OPENAI_ENDPOINT

import os
from autogen import ConversableAgent
import pprint

# 获取 API 密钥，以及 Azure OpenAI 的 endpoint
api_key = os.getenv("4o_api")
base_url = os.getenv("4o_endpoint")
config_list = {
    "model": "gpt-4o",
    "api_key": api_key,
    "api_type": "azure",
    "base_url": base_url,
    "api_version": "2024-12-01-preview",
}

student_agent = ConversableAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    llm_config={"config_list":config_list},
)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config={"config_list":config_list},
)

chat_result = student_agent.initiate_chat(
    teacher_agent,
    message="What is triangle inequality?",
    summary_method="reflection_with_llm",
    max_turns=2,
)

print(ConversableAgent.DEFAULT_SUMMARY_PROMPT)
print(chat_result.summary)

pprint.pprint(chat_result.chat_history)
pprint.pprint(chat_result.cost)