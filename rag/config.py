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
STORE_DIR = Path("data/faiss_store")
DOC_DIR = Path("data/documents_refined")
TOP_K = 5
CHUNKS_SIZE = 500
CHUNK_OVERLAP = 100

EMB_MODEL_NAME = "text-embedding-3-large"
EMB_QUERY_PREFIX = ""
EMB_DOC_PREFIX = ""

# Per-model prefixes (override defaults above when present)
EMB_MODEL_PREFIXES = {
    "intfloat/multilingual-e5-large": ("query: ", "passage: "),
    "Qwen/Qwen3-Embedding-0.6B": ("", ""),
}
