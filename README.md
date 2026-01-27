# Promtior RAG Assistant

Chatbot RAG (LangChain + LangServe + FastAPI) sobre el contenido del sitio de Promtior. Incluye UI web, modo evaluacion, y endpoints API.

En este link se encuentra la documentación de la solución propuesta: [Ver documentación](docs/documentation.md)

El link a la pagina desplegada en Railways es el siguiente: [Pagina](https://challenge-promtior-production.up.railway.app/)

## Requisitos
- Python 3.11+
- OPENAI_API_KEY configurada

## Setup local (uv)
```bash
uv sync
uvicorn api:app --reload
```
Abrir: http://localhost:8000

## Docker Compose (local)
```bash
docker compose up --build
```

## Variables de entorno
- OPENAI_API_KEY

## Datos / index
El RAG usa `data/faiss_store` (index.faiss + meta.json).
Si cambias el modelo de embeddings, borra y reindexa:
```bash
rm -rf data/faiss_store
python -c "from rag.store import create_faiss_index; from rag.config import DOC_DIR, STORE_DIR; create_faiss_index(DOC_DIR, STORE_DIR)"
```

## Endpoints
- `/` UI chatbot
- `/evaluation` UI evaluacion
- `/rag/invoke` LangServe (RAG)
- `/api/evaluate` Ejecuta evaluacion con dataset
- `/api/ask` Pregunta rapida (respuesta + chunks)

## Evaluacion
Los datasets viven en:
- `testing/questions.csv` (English)
- `testing/preguntas.csv` (Spanish)

Desde la UI `/evaluation` puedes:
- correr tests
- filtrar Right/Middle/Wrong
- hacer una pregunta rapida y ver chunks

## Notas
- El archivo PDF se sirve en `/data/AI Engineer.pdf` y se usa como fuente cuando el documento es "Presentacion Challenge".