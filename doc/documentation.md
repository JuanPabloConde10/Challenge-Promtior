# Promtier-Challenge

A continuación se describe en detalle la solución propuesta, el proceso de diseño y las principales dificultades encontradas.

## Data extraction

El primer paso consistió en recolectar la información del sitio de Promtior. Para ello se implementó el módulo `data_extraction.py`, que incluye tres funciones (`get_all_links`, `save_all_texts` y `refine_documents`) encargadas, en conjunto, de extraer y preparar el contenido de las páginas.

El workflow del módulo es el siguiente:

* A partir de la página de inicio (`https://www.promtior.ai`), se extraen todos los enlaces y se filtran aquellos que apuntan a redes sociales.
* Luego se descarga el contenido de cada página. Para convertir el HTML a texto plano se utiliza **BeautifulSoup**, lo que simplifica el scraping. Los documentos resultantes se guardan en la carpeta `documents_scrappy`.
* Finalmente, al revisar los archivos scrappeados se observa que el texto es poco estructurado y no favorece el retrieval. Por ese motivo se refina cada documento usando un **LLM**: se envía el contenido del `.txt` junto con un prompt que solicita una reescritura en un formato más legible y fácil de consultar. Los documentos refinados se almacenan en `documents_refined`.

## RAG

El sistema RAG sigue un enfoque clásico de **Bi-Encoder**. Ante una consulta, el flujo es el siguiente:

* Si la base vectorial aún no existe, se construye usando **FAISS**:

  * Se dividen los documentos en chunks de **500** caracteres con overlap de **100**.
  * Cada chunk se transforma a embeddings con el modelo seleccionado.
  * Los embeddings se almacenan en `index.faiss`.

  Además, se genera un `meta.json` para guardar metadata. En particular, se registra el *source* de cada chunk para poder mostrar en el frontend qué documentos se utilizaron como respaldo de la respuesta.

* Cuando llega una query, se calcula su embedding con el mismo modelo y se evalúa su similitud contra el índice. Se recuperan los **K** chunks más cercanos usando **similitud coseno**.

* Por último, se envían al LLM la pregunta y los **K** chunks recuperados, y se devuelve la respuesta al usuario.

En la configuración final se utiliza **K = 5**.

## Testing

Para evaluar el sistema se construye un dataset de **Q&A** basado en contenido real del sitio. Además, se incluyen preguntas para las cuales el sistema no debería tener información suficiente, con el objetivo de verificar que no invente respuestas.

Metodología de evaluación:

* Se prueban distintos valores de **K** (3, 5 y 10).
* Se varían tamaños de chunk (250, 500, 700).
* Se comparan distintos modelos de embeddings:

  * `text-embedding-3-large`
  * `text-embedding-3-small`
  * `intfloat/multilingual-e5-large`
  * `Qwen3-Embedding-0.6B`
* Método de retrieval:

  * Bi-Encoder
* Evaluación:

  * Se utiliza **LLM-as-a-Judge** para comparar la respuesta generada contra la respuesta esperada dada la pregunta. El juez clasifica en tres categorías: **Right**, **Middle** y **Wrong**.

Resultados:

| Idioma  | Modelo                         | Right | Middle | Wrong |
| ------- | ------------------------------ | ----: | -----: | ----: |
| Inglés  | text-embedding-3-large         |    13 |      6 |     0 |
| Inglés  | text-embedding-3-small         |    13 |      6 |     0 |
| Inglés  | intfloat/multilingual-e5-large |    12 |      7 |     0 |
| Inglés  | Qwen (Embedding-0.6B)          |    13 |      7 |     0 |
| Español | Qwen (Embedding-0.6B)          |    12 |      7 |     0 |
| Español | intfloat/multilingual-e5-large |    11 |      8 |     0 |
| Español | text-embedding-3-small         |    11 |      8 |     0 |
| Español | text-embedding-3-large         |    11 |      8 |     0 |

En general, los resultados indican que el rendimiento varía poco entre modelos de embeddings y que el sistema funciona levemente mejor en inglés que en español. En los casos clasificados como **Middle**, el análisis sugiere que la ambigüedad de la pregunta permite considerar válidas ambas respuestas (la esperada y la generada), aunque enfatizan aspectos distintos.

Cuando las preguntas tienen respuestas concretas y únicas, el sistema responde correctamente en todos los casos evaluados.

## Frontend

El frontend se mantiene intencionalmente simple y consta de dos vistas:

* Una vista principal para interactuar con el chatbot.
* Una vista de evaluación, donde se puede realizar una pregunta y ver qué chunks fueron recuperados. Desde ahí también se puede ejecutar la evaluación sobre el dataset y filtrar las preguntas respondidas correctamente e incorrectamente.

## Tecnologías utilizadas

Lista de tecnologías y su propósito:

* **LangChain + LangServe**: composición del pipeline RAG y exposición del chain como endpoint (`/rag/invoke`).
* **FastAPI**: servidor web ligero para montar el chain y servir el frontend.
* **FAISS**: base vectorial local para búsquedas rápidas mediante similitud coseno.
* **Modelos de embeddings**:

  * **OpenAI embeddings** (`text-embedding-3-large`, `text-embedding-3-small`) para variantes remotas.
  * **Sentence-Transformers** (`intfloat/multilingual-e5-large`, `Qwen/Qwen3-Embedding-0.6B`) para variantes locales.
* **OpenAI API**: modelo generativo (`gpt-5-mini`) para responder con contexto y para evaluación “LLM as a Judge”.
* **BeautifulSoup4**: scraping y parseo de HTML a texto plano.

## Dificultades

El principal problema aparece en el deploy. La librería **Sentence-Transformers** incrementa significativamente el tamaño de la imagen de Docker, lo que aumenta el consumo de recursos y puede agotar la memoria disponible en el plan gratuito de Railway.

## Cosas a mejorar

* **Dataset**: ampliar cobertura, reducir ambigüedades y balancear mejor preguntas en español/inglés.
* **Tiempos de respuesta**: optimizar el pipeline (caching, batch de embeddings, warmup, etc.).
* **Retrieval**: evaluar enfoques más avanzados, por ejemplo:

  * **Cross-Encoder** para re-rank de los chunks recuperados.
  * **Qdrant** para retrieval híbrido (combinando señal vectorial + keyword/BM25) y mejores capacidades de filtrado.
