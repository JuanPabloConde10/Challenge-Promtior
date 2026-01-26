from __future__ import annotations

import numpy as np
from langchain_core.documents import Document

from rag.config import TOP_K, EMB_MODEL_NAME
from rag.embeddings import EmbeddingModel
from rag.store import load_store


def search(index, meta, embedder: EmbeddingModel, query: str, k: int = TOP_K) -> list[dict]:
    # FAISS espera [1, dim]
    q_emb = embedder.embed_query(query)
    if q_emb.ndim == 1:
        q_emb = np.expand_dims(q_emb, axis=0)

    scores, ids = index.search(q_emb, k)
    results = []
    for score, cid in zip(scores[0].tolist(), ids[0].tolist()):
        if cid == -1:
            continue
        m = meta.get(cid, {})
        results.append(
            {
                "id": cid,
                "score": float(score),
                "source": m.get("source", "unknown"),
                "chunk_index": m.get("chunk_index"),
                "text": m.get("text", ""),
            }
        )
    return results


def to_documents(results: list[dict]) -> list[Document]:
    docs: list[Document] = []
    for r in results:
        docs.append(
            Document(
                page_content=r["text"],
                metadata={
                    "source": r["source"],
                    "score": r["score"],
                    "chunk_index": r["chunk_index"],
                    "id": r["id"],
                },
            )
        )
    return docs


def retrieve(query: str, k: int = TOP_K) -> list[Document]:
    index, meta = load_store()
    embedder = EmbeddingModel(EMB_MODEL_NAME)
    results = search(index, meta, embedder, query, k=k)
    return to_documents(results)
