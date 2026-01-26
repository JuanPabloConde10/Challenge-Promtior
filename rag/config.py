from pathlib import Path

LINKS = [
    "https://www.promtior.ai",
    "https://www.promtior.ai/service",
    "https://www.promtior.ai/use-cases",
    "https://careers.promtior.ai/",
    "https://www.promtior.ai/contacto",
    "https://www.promtior.ai/blog",
    "https://www.promtior.ai/politica-de-privacidad",
    "Presentación Challenge",
]
LLM_MODEL_NAME = "gpt-5-mini"
EMB_MODEL_NAME = "intfloat/multilingual-e5-large"
STORE_DIR = Path("data/faiss_store")
DOC_DIR = Path("data/documents_refined")
TOP_K = 5
CHUNKS_SIZE = 500
CHUNK_OVERLAP = 100
EMB_QUERY_PREFIX = "query: "
EMB_DOC_PREFIX = "passage: "