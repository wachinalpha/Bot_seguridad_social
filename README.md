# Bot_seguridad_social
Repositorio destinado al desarrollo de un bot que responda dudas y reclamos de la seguridad social Argentina. Aclaraciones:
Abajo puse la estructura deseada aproximada del proyecto. Por ahora, si miran no está todo lo que aparece en este readme, sino algunos scripts. Esta arquitectura tiene que funcionar como guía ordenadora y no como un axioma.
#Arquitectura del proyecto
📂 Estructura de Carpetas
rag_app/
  config/
    leyes_config.json
    settings.py
  domain/
    models.py
  ports/
    chunker.py
    embedder.py
    vector_store.py
    contextualizer.py
  adapters/
    chunkers/
    embedders/
    stores/
    contextualizers/
  services/
    ingestion_service.py
    retrieval_service.py
  pipelines/
  scripts/
  utils/
  main.py
  tests/

Descripción de cada módulo

config/
| Archivo             | Función                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `settings.py`       | Configuración central del proyecto. Carga variables desde `.env` (API keys, rutas, configuración de embeddings, base vectorial, etc.). |
| `leyes_config.json` | Metadata declarativa de las leyes a ingestar: fuente, URL, versión, tipo de documento, jurisdicción, etc.                              |

domain/
| Archivo     | Función                                                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `models.py` | Define clases como: `Law` (documento legal completo), `Chunk` (fragmento indexable), `QueryResult`, etc. Sin lógica especifica; solo estructura. Para los
que codean en C es similar a un struct|


ports/ (Interfaces / Abstracciones)
| Archivo             | Función                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `chunker.py`        | Interface para dividir documentos (`Law → list[Chunk]`).                                                           |
| `embedder.py`       | Interface para generar embeddings a partir de texto.                                                               |
| `vector_store.py`   | Interface para almacenar/buscar chunks en bases vectoriales.                                                       |
| `contextualizer.py` | Interface para armar el "contexto final" que verá el LLM (prompt builder, re-ranker, formateo de citas). |

** Este es el módulo menos útil por ahora, va a servir mas adelante si queremos empezar a modificar el retrival. Tal ves cambie o lo saquemos en un futuro no se.
adapters/
| Carpeta            | Contenido                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `chunkers/`        | Ej: `HybridMarkdownChunker`, `ArticleChunker`, etc.                                      |
| `embedders/`       | Ej: `MiniLMEmbedder`, `E5Embedder`, `InstructorXLEmbedder`.                              |
| `stores/`          | Ej: `ChromaVectorStore`, `PgVectorStore`, `FAISSAdapter`.                                |
| `contextualizers/` | Lógica para construir prompts, citar artículos, aplicar templates de contexto para LLMs. |

services/
| Archivo                | Función                                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `ingestion_service.py` | Toma una ley → chunk → embedding → guarda en base vectorial. Incluye versionado e idempotencia.                               |
| `retrieval_service.py` | Dada una consulta → busca los chunks relevantes → opcionalmente pasa por un contextualizer para devolver respuesta + fuentes. |


pipelines/
Flujos de orquestación de alto nivel (pueden combinar varios servicios).
Ejemplo:

IngestPipeline: carga JSON, crea Law, llama al ingestion_service.

QueryPipeline: recibe pregunta → retrieval_service → contextualizer → LLM.

tests/
Tests unitarios y de integración. Mínimo esperado:

test_chunker.py

test_embedder.py

test_ingestion_service.py

test_retrieval_service.py

Fixtures para JSON de ejemplo y pequeña base de Chroma en modo :memory:.

scripts/

Scripts CLI para uso manual o batch. Ejemplos:

ingest_laws.py → ingestión masiva desde leyes_config.json.

test_query.py → probar preguntas sin front-end.

main.py

Punto de entrada opcional del proyecto (CLI general). Puede manejar:
python main.py ingest --file data/ley_24714.json
python main.py query --ask "¿Qué dice el artículo 2 sobre asignaciones?"

utils/
| Archivo             | Función                                                      |
| ------------------- | ------------------------------------------------------------ |
| `logger.py`         | Configuración personalizada del logging.                     |
| `hashing.py`        | Funciones para generar `content_hash` de los chunks.         |
| `markdown_utils.py` | Limpieza, normalización y extracción de títulos/encabezados. |



