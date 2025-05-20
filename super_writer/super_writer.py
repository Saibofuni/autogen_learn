from autogen import ConversableAgent
import super_writer_support as support
import os

# You need to set the environment variables for 4o_api and 4o_endpoint before running this script.
api_key = os.environ.get("4o_api")
base_url = os.environ.get("4o_endpoint")
config_list = {
    "model": "gpt-4o",
    "api_key": api_key,
    "api_type": "azure",
    "base_url": base_url,
    "api_version": "2024-12-01-preview",
}

user_proxy = ConversableAgent(
    name="user_proxy",
    llm_config={"config_list": config_list},
    system_message="You are a user proxy for a content generation system. Your task is to assist in generating and enriching content based on user requests.",
)

format_writer = ConversableAgent(
    name="format_writer",
    llm_config={"config_list": config_list},
    system_message=(
        "You are a format writer. Your task is to generate a format (markdown format) according to the title and request."
        "REMEMBER THE TITLE USE '#', SUBTITLE USE '##'. Example:\n\n"
        "# Title\n\n"
        "## Overview\n"
        "Provide a concise and complete summary of the key content of the entry, including the full Chinese name, the most common complete definition, "
        "key contributors, earliest research time, theory maturity time, main research works, and brief impact.\n\n"
        "## Basic Information\n"
        "Fill in according to the theorem/law template, including Chinese name, English name, alias, applied discipline, expression, key contributors, "
        "earliest research time, theory maturity time, main research works, applicable field range, etc.\n"
        "......\n"
    ),
)

writer = ConversableAgent(
    name="writer",
    llm_config={"config_list": config_list},
    system_message="You are a content writer. Your task is to generate and enrich content based on user requests. You need to follow the format strictly. DO NOT ADD IRRELEVANT CONTENT.",
)

writer_details = ConversableAgent(
    name="writer_details",
    llm_config={"config_list": config_list},
    system_message="You are a content writer. Your task is to generate and enrich content based on user requests and it will be added to the markdown file, so use markdown format. You need to follow the format strictly. Do not add anything else.",
)

# Function to generate the format
def format_generate(title: str, request: str) -> str:
    format_chat = user_proxy.initiate_chat(
        format_writer,
        message=f"Please generate a detailed format based on the title '{title}' and the request '{request}'.",
        summary_method="last_msg",
        max_turns=1,
    )
    format_ = format_chat.summary
    with open("./format.md", "w", encoding="utf-8") as file:
        file.write(format_)
    print(f"Format generated and saved to format.md")
    return f"Generated format for title: {title} with request: {request}"

# Function to enrich the content
def enrich_content(content: str) -> str:
    enrich_chat = user_proxy.initiate_chat(
        writer_details,
        message=f"DO NOT ADD '---'. Super enrich the content(add 1000-1500) provided below logically(eg: using '1. 2. 3. ' and indentation) while strictly follow the format. Content: {content}",
        summary_method="last_msg",
        max_turns=1,
    )
    return enrich_chat.summary

if __name__ == "__main__":

    title = input("Please enter the title of the article: ")
    request = input("Please enter the request of the article(eg: language, abundence): ")
    final_path = input("Please enter the final path of the article(docx): ")
    final_path = final_path.replace("\\", "/")

    format_path = "./format.md"

    format_generate(title, request)

    text_path = f"./{title}.txt"
    path = f"./{title}.md"
    path = path

    with open(path, "w", encoding="utf-8") as file:
        file.write(f"## {title}\n\n")

    format_ = support.get_format("./format.md")

    chat = user_proxy.initiate_chat(
        writer,
        message=f"Please generate a detailed article based on the title '{title}' and the format provided below. Format: {format_}. YOU NEED TO FOLLOW THE FORMAT STRICTLY. DO NOT ADD ANYTHING ELSE. REPLACE '标题' WITH '{title}'.",
        summary_method="last_msg",
        max_turns=1,
    )

    content = chat.summary
    support.write_article(text_path, content)

    # fetch the content from the text file and enrich it
    empty = False
    while not empty:
        content = support.get_contents(text_path)
        if content == "":
            empty = True
        else:
            enriched_content = enrich_content(content)
            support.write_to_markdown(path, enriched_content)

    # Check if the file exists before attempting to remove it
    if os.path.exists("./format.md"):
        os.remove("./format.md")
        print(f"File ./format.md removed.")
    else:
        print(f"File ./format.md does not exist.")

    # Check if the file exists before attempting to remove it
    if os.path.exists(text_path):
        os.remove(text_path)
        print(f"File {text_path} removed.")
    else:
        print(f"File {text_path} does not exist.")

    support.markdown_to_docx(path, final_path)
    
    if os.path.exists(path):
        os.remove(path)
        print(f"File {path} removed.")
    else:
        print(f"File {path} does not exist.")