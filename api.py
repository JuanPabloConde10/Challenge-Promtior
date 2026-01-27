from pathlib import Path
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langserve import add_routes

from rag.chain import build_chain

load_dotenv()

app = FastAPI(title="Promtior RAG")

# LangServe RAG endpoint
rag_chain = build_chain()
add_routes(app, rag_chain, path="/rag")

# Static frontend
FRONTEND_DIR = Path(__file__).parent / "frontend"
DATA_DIR = Path(__file__).parent / "data"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")


@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/evaluation")
def evaluation_page():
    return FileResponse(FRONTEND_DIR / "evaluation.html")


@app.post("/api/evaluate")
def run_evaluation(payload: dict | None = None):
    from testing.evaluator import evaluate

    language = "English"
    if payload and isinstance(payload, dict):
        language = payload.get("language", language)

    return evaluate(language)


@app.post("/api/ask")
def ask_question(payload: dict | None = None):
    question = ""
    k = None
    embedding_model = None
    if payload and isinstance(payload, dict):
        question = (payload.get("question") or "").strip()
        k = payload.get("k")
        embedding_model = payload.get("embedding_model")
    if not question:
        return {"answer": "", "sources": [], "chunks": []}

    try:
        input_payload = {"question": question}
        if k is not None:
            input_payload["k"] = k
        if embedding_model:
            input_payload["embedding_model"] = embedding_model
        output = rag_chain.invoke(input_payload)
    except Exception as exc:
        return {"answer": "", "sources": [], "chunks": [], "error": str(exc)}

    if isinstance(output, dict):
        answer = (output.get("answer") or "").strip()
        sources = output.get("sources") or []
    else:
        answer = str(output).strip()
        sources = []

    from rag.config import EMB_MODEL_NAME, TOP_K
    from rag.embeddings import EmbeddingModel
    from rag.retriever import search
    from rag.store import load_store

    model_name = embedding_model or EMB_MODEL_NAME
    top_k = int(k) if k is not None else TOP_K
    index, meta = load_store(model_name=model_name)
    embedder = EmbeddingModel(model_name)
    chunks = search(index, meta, embedder, question, k=top_k)

    return {"answer": answer, "sources": sources, "chunks": chunks}
