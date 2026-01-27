import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from rag.chain import build_chain
from rag.retriever import retrieve

def build_prompt():
    system = (
        "You are a very smart comparator\n"
        "You are going to recive one question, the right answer of the question and a possible answer."
        "You have to classify the question in three categories:"
        "- Right: only if the possible answer contains the exact information as the right question"
        "- Middle: contains part of the information"
        "- Wrong: there is no possibility to considere this as a right answer"
        "\n\nRespond only one of this 3 words"
    )
    human = "Question: {question}\n\nRight Answer:\n{Right}\n\n Possible Answer:\n{Possible}"
    return ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])

def evaluate(lenguage = "English"):
    right = 0
    middle = 0
    wrong = 0
    total = 0
    results = []

    df = pd.read_csv(
        "testing/questions.csv",
        engine="python",
        quotechar="\"",
        escapechar="\\",
        skipinitialspace=True,
    )
    if lenguage == "Spanish":
        df = pd.read_csv(
            "testing/preguntas.csv",
            engine="python",
            quotechar="\"",
            escapechar="\\",
            skipinitialspace=True,
        )

    rag_chain = build_chain()
    comparator_prompt = build_prompt()
    comparator_llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
    comparator_chain = comparator_prompt | comparator_llm | StrOutputParser()

    for question, right_a in zip(df["question"], df["answer"]):
        question = str(question).strip()
        right_a = str(right_a).strip()
        if not question:
            continue

        total += 1
        print(total)
        
        docs = retrieve(question)
        chunks = [
            {
                "text": d.page_content,
                "source": d.metadata.get("source"),
                "score": d.metadata.get("score"),
                "chunk_index": d.metadata.get("chunk_index"),
                "id": d.metadata.get("id"),
            }
            for d in docs
        ]

        try:
            rag_output = rag_chain.invoke(question)
        except Exception as exc:
            rag_output = {"answer": "", "sources": [], "error": str(exc)}

        if isinstance(rag_output, dict):
            answer = str(rag_output.get("answer", "")).strip()
            sources = rag_output.get("sources", [])
            error = rag_output.get("error")
        else:
            answer = str(rag_output).strip()
            sources = []
            error = None

        try:
            verdict = comparator_chain.invoke(
                {"question": question, "Right": right_a, "Possible": answer}
            ).strip()
        except Exception as exc:
            verdict = f"error: {exc}"

        verdict_norm = verdict.lower()
        if verdict_norm.startswith("right"):
            right += 1
        elif verdict_norm.startswith("middle"):
            middle += 1
        elif verdict_norm.startswith("wrong"):
            wrong += 1

        results.append(
            {
                "question": question,
                "expected": right_a,
                "answer": answer,
                "sources": sources,
                "verdict": verdict,
                "error": error,
                "chunks": chunks,
            }
        )

    summary = {
        "total": total,
        "right": right,
        "middle": middle,
        "wrong": wrong,
        "accuracy": (right / total) if total else 0.0,
    }

    return {"summary": summary, "results": results}

    
