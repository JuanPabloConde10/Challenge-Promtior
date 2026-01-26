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
