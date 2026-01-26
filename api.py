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
    if payload and isinstance(payload, dict):
        question = (payload.get("question") or "").strip()
    if not question:
        return {"answer": "", "sources": [], "chunks": []}

    try:
        output = rag_chain.invoke(question)
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

    index, meta = load_store()
    embedder = EmbeddingModel(EMB_MODEL_NAME)
    chunks = search(index, meta, embedder, question, k=TOP_K)

    return {"answer": answer, "sources": sources, "chunks": chunks}
