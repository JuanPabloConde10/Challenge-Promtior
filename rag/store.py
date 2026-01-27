import faiss
import json
import numpy as np

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from rag.embeddings import EmbeddingModel
from rag.config import STORE_DIR, DOC_DIR, EMB_MODEL_NAME, CHUNKS_SIZE, CHUNK_OVERLAP, LINKS


def _model_slug(model_name: str) -> str:
    return (
        model_name.replace("/", "__")
        .replace(":", "_")
        .replace(" ", "_")
        .lower()
    )


def _model_store_dir(store_dir: Path, model_name: str) -> Path:
    return store_dir / _model_slug(model_name)


def create_faiss_index(doc_dir: Path, store_dir: Path, model_name: str = EMB_MODEL_NAME):
    """Crea FAISS + metadatos para el modelo indicado."""

    model_emb = EmbeddingModel(model_name)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNKS_SIZE, chunk_overlap=CHUNK_OVERLAP
    )

    index = None
    meta = {}
    next_id = 1

    txt_files = sorted(doc_dir.glob("*.txt"))
    if not txt_files:
        print(f"No encontré .txt en {doc_dir.resolve()}")

    for i, fp in enumerate(txt_files):
        raw = fp.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            print(f"[SKIP] vacío: {fp.name}")
            continue

        chunks = [c.strip() for c in text_splitter.split_text(raw) if c.strip()]
        if not chunks:
            print(f"[SKIP] sin chunks: {fp.name}")
            continue

        embeddings = model_emb.embed_documents(chunks)
        if index is None:
            dim = embeddings.shape[1]
            base = faiss.IndexFlatIP(dim)
            index = faiss.IndexIDMap2(base)

        ids = np.arange(next_id, next_id + len(chunks), dtype="int64")
        index.add_with_ids(embeddings, ids)

        source = LINKS[i] if i < len(LINKS) else fp.name
        for cid, chunk_text, chunk_index in zip(ids.tolist(), chunks, range(len(chunks))):
            meta[cid] = {
                "source": source,
                "local_file": fp.name,
                "doc_index": i,
                "chunk_index": chunk_index,
                "text": chunk_text,
            }

        next_id += len(chunks)
        print(f"[OK] {fp.name}: {len(chunks)} chunks")

    if index is None:
        raise ValueError("No se pudieron generar embeddings para crear el indice.")

    store_dir = _model_store_dir(store_dir, model_name)
    store_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(store_dir / "index.faiss"))
    with open(store_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\nListo. Index: {(store_dir / 'index.faiss').resolve()}")
    print(f"Meta:  {(store_dir / 'meta.json').resolve()}")
    print(f"Total vectors: {index.ntotal}")

    return index, meta


def load_store(model_name: str = EMB_MODEL_NAME) -> tuple[faiss.Index, dict[int, dict]]:
    """Loads faiss index; if missing, creates a new one for the model."""
    store_dir = _model_store_dir(STORE_DIR, model_name)
    index_path = store_dir / "index.faiss"
    meta_path = store_dir / "meta.json"

    if (not index_path.exists()) or (not meta_path.exists()):
        return create_faiss_index(DOC_DIR, STORE_DIR, model_name=model_name)

    index = faiss.read_index(str(index_path))
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_raw = json.load(f)

    meta = {int(k): v for k, v in meta_raw.items()}
    return index, meta
