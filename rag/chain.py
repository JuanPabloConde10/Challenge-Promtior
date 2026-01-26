from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from rag.retriever import retrieve

def format_docs(docs) -> str:
    parts = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        parts.append(f"[source] {src}\n{d.page_content}")
    return "\n\n".join(parts)

def extract_sources(docs) -> list[str]:
    sources: list[str] = []
    seen = set()
    for d in docs:
        src = d.metadata.get("source")
        if not src:
            continue
        if src == "Presentación Challenge":
            src = "/data/AI Engineer.pdf"
        if src in seen:
            continue
        seen.add(src)
        sources.append(src)
    return sources


def build_prompt():
    system = (
        "You are a helpful assistant answering questions about the company Promtior.\n"
        "Use only the provided context. If the answer is not in the context, respond I don't have enough information to responde this.\n"
        "Keep the answer concise and factual."
    )
    human = "Question: {question}\n\nContext:\n{context}"
    return ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])


def build_llm():
    return ChatOpenAI(model="gpt-5-mini", temperature=0)


def build_chain():
    prompt = build_prompt()
    llm = build_llm()

    def build_inputs(question: str) -> dict:
        docs = retrieve(question)
        return {
            "question": question,
            "context": format_docs(docs),
            "sources": extract_sources(docs),
        }

    def only_prompt_inputs(data: dict) -> dict:
        return {
            "question": data["question"],
            "context": data["context"],
        }

    inputs = RunnableLambda(build_inputs)
    answer_chain = RunnableLambda(only_prompt_inputs) | prompt | llm | StrOutputParser()

    return (
        inputs
        | RunnablePassthrough.assign(answer=answer_chain)
        | RunnableLambda(lambda data: {"answer": data["answer"], "sources": data["sources"]})
    )
