import numpy as np
from sentence_transformers import SentenceTransformer
from rag.config import EMB_DOC_PREFIX, EMB_QUERY_PREFIX

class EmbeddingModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
    
    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode(
            EMB_QUERY_PREFIX + query,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")
    
    def embed_documents(self, chunks: list[str]) -> list[np.ndarray]:
        chunks_for_emb = [EMB_DOC_PREFIX+c for c in chunks]
        return self.model.encode(
            chunks_for_emb,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")