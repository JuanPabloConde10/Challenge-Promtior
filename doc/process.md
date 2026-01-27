# Promtier-Challenge

A continuación explicamos en detalle la solución planteada, cómo fue que llegamos a ella y las dificultades que surgieron.

## Data extraction

Lo primero que hice fue ver cómo recolectar la información de la página de Promtier. Para eso definí el archivo `data_extraction.py`. Ahí definí tres funciones (`get_all_links`, `save_all_texts` y `refine_documents`) las cuales en su conjunto nos permiten extraer la información de las páginas de Promtier.

El workflow que se hace en este módulo es el siguiente:

- Primero, dada la página de inicio de Promtier (`https://www.promtior.ai`), obtenemos todos los links que se encuentran en esta y descartamos los links que eran de redes sociales.
- Lo siguiente que hicimos fue descargar el contenido de estas páginas web. Para esto usamos la biblioteca **BeautifulSoup**, que nos facilitó un montón el trabajo de pasar a texto plano el contenido de la página. Los documentos scrappeados se encuentran en la carpeta `documents_scrappy`.
- Después de hacer esto, analizamos el contenido que tenían los archivos guardados y vimos que no tenían una estructura que facilitara el retrieval. Por esto decidimos, mediante el uso de un **LLM**, hacer un refinamiento de los documentos con el fin de mejorar el retrieval. Este proceso de refinamiento consistió simplemente en pasarle al LLM el contenido del `.txt` más un prompt que le pedía que nos creara un documento legible y que sea fácil de extraer información de él. Esto se hizo para cada documento y quedó guardado en la carpeta `documents_refined`.

## RAG

Para el RAG tomamos un enfoque clásico de **Bi-Encoder**. Cuando se hace una consulta, los pasos que se siguen son los siguientes:

- Si la base de datos vectorial no está creada, la creamos. Para esto utilizamos **FAISS**.  
  El proceso de cargar el índice consiste en:
  - Partir los documentos en chunks de tamaño **500** caracteres y overlap **100**.
  - Pasar estos chunks por nuestro modelo de embeddings, el cual los codifica en un vector de alta dimensionalidad.
  - Almacenar estos vectores en `index.faiss`.

  Importante también resaltar que creamos un `meta.json` para almacenar metadata. En particular, lo que nos interesa guardar es a qué *source* pertenecen los chunks que se usaron para la respuesta del cliente, de esta forma poder mostrar en el frontend las fuentes usadas para dar una respuesta.

- Cuando viene una query, la pasamos a un embedding utilizando el mismo modelo que usamos para la codificación de los chunks. Este nuevo embedding lo comparamos con los embeddings existentes y nos quedamos con los **K** vectores (chunks) más similares. La medida de similitud es la **similitud coseno**.
- Luego al LLM le pasamos estos **K** chunks más la pregunta y le devolvemos al usuario la respuesta.

## Testing

Para testear el sistema decidimos crear un dataset de **Q&A** con información de cosas que estaban en la página web. También agregamos preguntas que el modelo no tiene información para responder, para evaluar que no responda cosas que no puede.

A continuación presentamos la metodología de evaluación realizada:

- Variamos el tamaño de **K** (3, 5 y 10).
- Variamos el tamaño de chunk (250, 500, 700).
- Modelos de embeddings:
  - `text-embedding-3-large`
  - `text-embedding-3-small`
  - `intfloat/multilingual-e5-large`
  - `Qwen3-Embedding-0.6B`
- Método de retrieval:
  - Bi-Encoder
  - Cross-Encoder

Los resultados fueron los siguientes:

> (Agregar tabla/gráfica o resumen de métricas acá)

## Frontend

Para el frontend hicimos algo bien sencillo: dos ventanas.

- La principal, donde se puede interactuar con el chatbot.
- La segunda (mi favorita), que es de evaluación: se puede hacer una pregunta y ver qué chunks devuelve. Acá también se puede correr la evaluación del dataset y filtrar cuáles fueron respondidas bien y mal.

## Tecnologías utilizadas

> (Completar)

## Dificultades

> (Completar)

## Cosas a mejorar

- El dataset
- Los tiempos de respuesta
