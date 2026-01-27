from __future__ import annotations
from rag.config import LLM_MODEL_NAME

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from rag.retriever import retrieve
from rag.config import TOP_K, EMB_MODEL_NAME

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
    return ChatOpenAI(model=LLM_MODEL_NAME, temperature=0)


def build_chain():
    prompt = build_prompt()
    llm = build_llm()

    def build_inputs(input_data) -> dict:
        if isinstance(input_data, dict):
            question = (input_data.get("question") or "").strip()
            k = input_data.get("k", TOP_K)
            model_name = input_data.get("embedding_model", EMB_MODEL_NAME)
        else:
            question = str(input_data).strip()
            k = TOP_K
            model_name = EMB_MODEL_NAME

        docs = retrieve(question, k=int(k), model_name=model_name)
        return {
            "question": question,
            "context": format_docs(docs),
            "sources": extract_sources(docs),
            "embedding_model": model_name,
            "k": k,
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
