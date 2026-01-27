import numpy as np
# from sentence_transformers import SentenceTransformer
from langchain_openai import OpenAIEmbeddings
from rag.config import EMB_DOC_PREFIX, EMB_QUERY_PREFIX

class EmbeddingModel:
    def __init__(self, model_name):
        self.model_name = model_name
        # self.model = SentenceTransformer(model_name)
        # self.dim = self.model.get_sentence_embedding_dimension()
        self.model = OpenAIEmbeddings(model=model_name)
        test_vec = self.embed_query("dimension check")
        self.dim = len(test_vec)
        print(self.dim)
    
    def embed_query(self, query: str) -> np.ndarray:
        text = f"{EMB_QUERY_PREFIX}{query}"
        vec = self.model.embed_query(text)
        return np.asarray(vec, dtype="float32")
    
    def embed_documents(self, chunks: list[str]) -> list[np.ndarray]:
        chunks_for_emb = [f"{EMB_DOC_PREFIX}{c}" for c in chunks]
        vecs = self.model.embed_documents(chunks_for_emb)
        return np.asarray(vecs, dtype="float32")
