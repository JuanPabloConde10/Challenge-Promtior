import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

links = ['https://www.promtior.ai', 'https://www.promtior.ai/service', 'https://www.promtior.ai/use-cases', 'https://careers.promtior.ai/', 'https://www.promtior.ai/contacto', 'https://www.promtior.ai/blog', 'https://www.promtior.ai/politica-de-privacidad']

def unique(lst):
    return list(dict.fromkeys(lst))

def get_all_links(base_url: str) -> List[str]:
    response = requests.get(base_url)
    
    if response.status_code == 200:
        html_content = response.text
        print("Successfully fetched the page content.")
        soup = BeautifulSoup(html_content, 'html.parser')
        links = unique([l.get('href') for l in soup.find_all('a')])
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return unique(links)

def save_all_texts(all_links: List[str]):
    for id, l in enumerate(all_links):
        response = requests.get(l)
        if response.status_code == 200:
            html_content = response.text
            print("Successfully fetched the page content.")
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.body.get_text(separator="\n", strip=True)   
            path = f'data/documents_scrappy/documents{id}.txt'
            with open(path, "w") as text_file:
                text_file.write(text)
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def refine_documents():
    system_prompt = (
        "You are a very helpful assistant that is part of a RAG system.\n"
        "You receive plain-text content extracted from a web page.\n"
        "Your task is to rewrite it into multiple paragraphs in a format that is readable for a user, and that feels like copy written by someone at the company, WITHOUT losing any information and WITHOUT inventing anything.\n"
        "Write all in english\n"
        "Remove repeated menus, cookie notices, and navigation elements, but keep the real informational content."
    )

    user_prompt = (
        "Given the following content, return a text that contains all the information from that web page in a clear and well-organized way.\n\nCONTENT:\n{content}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
    chain = prompt | llm | StrOutputParser()

    in_path = Path("data/documents_scrappy")
    out_path = Path("data/documents_refined")

    out_path.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"No existe la carpeta de entrada: {in_path.resolve()}")

    txt_files = sorted(in_path.glob("*.txt"))
    if not txt_files:
        print(f"No encontré .txt en {in_path.resolve()}")
        return []
    
    for fp in txt_files:
        raw = fp.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            print(f"[SKIP] vacío: {fp.name}")
            continue
        try:
            refined = chain.invoke({"content": raw})
        except Exception as e:
            refined = "" 

        out_file = out_path / fp.name 
        out_file.write_text(refined, encoding="utf-8")
        print(f"[OK] {fp.name} -> {out_file}")
    
