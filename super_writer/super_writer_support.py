import os
import markdown2
import re
from docx import Document
import subprocess
import requests
from bs4 import BeautifulSoup




def write_article(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Article written to {path} successfully.")
    return "Article written successfully."



def get_format(format_path: str) -> str:
    with open(format_path, "r", encoding="utf-8") as file:
        return file.read()



def get_contents(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    content = []
    remove_lines = []
    capture = False
    remaining_lines = []
    for line in lines:
        if "###" in line and "####" not in line:
            if capture:  # Stop capturing when the next "###" is found
                remaining_lines.append(line)  # Keep the current "###" for the next read
                break
            capture = True
            content.append(line)
        elif capture:
            content.append(line)
        remove_lines.append(line)
    updated_lines = [line for line in lines if line not in remove_lines]
    with open(path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)
    return "".join(content)



def write_to_markdown(path: str, content: str) -> str:
    with open(path, "a", encoding="utf-8") as file:
        file.write(content+"\n\n")
    return "Content written to markdown file successfully."



def check_pandoc_installed():
    try:
        subprocess.run(["pandoc", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False



def markdown_to_docx(input_file, output_folder):
    if not input_file.lower().endswith(('.md', '.markdown')):
        print("Please provide a valid Markdown file (ending with .md or .markdown)")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Output folder '{output_folder}' has been created.")
    output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + ".docx")
    doc = Document()
    try:
        with open(input_file, 'r', encoding='utf-8') as md_file:
            md_text = md_file.read()
    except FileNotFoundError:
        print("File not found, please check if the file path is correct.")
        return
    html = markdown2.markdown(md_text, extras=["tables", "fenced-code-blocks", "footnotes"])
    inline_formula = re.findall(r'\$(.*?)\$', html)
    block_formula = re.findall(r'\$\$(.*?)\$\$', html)
    # 替换公式为 Pandoc 可识别的格式
    for formula in inline_formula:
        html = html.replace(f"${formula}$", f"\\({formula}\\)")
    for formula in block_formula:
        html = html.replace(f"$${formula}$$", f"\\[{formula}\\]")
    if not check_pandoc_installed():
        print("Pandoc is not installed or not added to the system PATH, please install Pandoc and ensure it is in the system PATH.")
        return
    with open("temp.html", "w", encoding="utf-8") as temp_html:
        temp_html.write(html)
    try:
        subprocess.run(["pandoc", "temp.html", "-o", output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")
        return
    os.remove("temp.html")
    print(f"Markdown file '{input_file}' has been successfully converted to Word file '{output_file}'")