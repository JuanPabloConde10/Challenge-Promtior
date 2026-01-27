import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_openai import OpenAIEmbeddings
from rag.config import EMB_DOC_PREFIX, EMB_QUERY_PREFIX, EMB_MODEL_PREFIXES


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.query_prefix, self.doc_prefix = EMB_MODEL_PREFIXES.get(
            model_name, (EMB_QUERY_PREFIX, EMB_DOC_PREFIX)
        )

        if model_name.startswith("text-embedding-"):
            self.backend = "openai"
            self.model = OpenAIEmbeddings(model=model_name)
            self.dim = None
        else:
            self.backend = "sentence_transformers"
            self.model = SentenceTransformer(model_name)
            self.dim = self.model.get_sentence_embedding_dimension()

    def _normalize(self, vecs: np.ndarray) -> np.ndarray:
        if vecs.ndim == 1:
            norm = np.linalg.norm(vecs)
            return vecs if norm == 0 else (vecs / norm)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms

    def embed_query(self, query: str) -> np.ndarray:
        text = f"{self.query_prefix}{query}"
        if self.backend == "openai":
            vec = self.model.embed_query(text)
            arr = np.asarray(vec, dtype="float32")
            if self.dim is None:
                self.dim = arr.shape[0]
            return self._normalize(arr)

        vec = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")[0]
        return vec

    def embed_documents(self, chunks: list[str]) -> np.ndarray:
        chunks_for_emb = [f"{self.doc_prefix}{c}" for c in chunks]
        if self.backend == "openai":
            vecs = self.model.embed_documents(chunks_for_emb)
            arr = np.asarray(vecs, dtype="float32")
            if self.dim is None and arr.ndim == 2:
                self.dim = arr.shape[1]
            return self._normalize(arr)

        vecs = self.model.encode(
            chunks_for_emb,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")
        return vecs
