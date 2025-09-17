# 注意llm_config的配置，默认配置是openai，需要自行更改。
# 此处使用的是azure的openai，使用时需要在环境变量中设置AZURE_OPENAI_API_KEY和AZURE_OPENAI_ENDPOINT

import os
from autogen import ConversableAgent
import pprint
import json

# 获取 API 密钥，以及 Azure OpenAI 的 endpoint
api_config_path = os.environ.get("api_configs")
with open(api_config_path, "r", encoding="utf-8") as f:
    api_configs = json.load(f)
    api_key = api_configs['azure-4o']['api_key']
    endpoint = api_configs['azure-4o']['base_url']
    version = api_configs['azure-4o']['api_version']


api_key = os.getenv("4o_api")
base_url = os.getenv("4o_endpoint")
config_list = {
    "model": "gpt-4o",
    "api_key": api_key,
    "api_type": "azure",
    "base_url": endpoint,
    "api_version": version,
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
# attention: the summary_method is reflection_with_llm, which means the agent will use LLM to summarize the conversation. You can also use "last_msg" to get the last message as summary.
print(ConversableAgent.DEFAULT_SUMMARY_PROMPT)
print(chat_result.summary)

pprint.pprint(chat_result.chat_history)
pprint.pprint(chat_result.cost)