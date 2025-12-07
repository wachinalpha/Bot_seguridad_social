# Legal AI RAG System - Architecture Documentation

## Overview

This system implements a **NotebookLM-inspired Legal AI RAG** for Argentine Social Security Laws using **Hexagonal Architecture** (Ports & Adapters pattern).

**Key Innovation:** Document-level retrieval with Gemini Context Caching instead of traditional chunk-based RAG.

## Architecture Diagram

```mermaid
graph TB
    subgraph "External World"
        USER[👤 User]
        WEB[🌐 Law Websites]
        GEMINI[🤖 Gemini API]
    end
    
    subgraph "Entry Points"
        UI[🖥️ Streamlit UI<br/>main.py]
        SETUP[⚙️ Setup Script<br/>setup_db.py]
    end
    
    subgraph "Services Layer (Orchestration)"
        INGEST[📥 IngestionService<br/>Web → MD → Vector]
        RETRIEVE[📤 RetrievalService<br/>Query → Cache → Answer]
    end
    
    subgraph "Ports (Interfaces)"
        PORT_DOC[📄 DocumentProcessorPort]
        PORT_EMB[🔢 EmbedderPort]
        PORT_VEC[🗄️ VectorStorePort]
        PORT_CTX[💾 ContextualizerPort]
    end
    
    subgraph "Adapters (Implementations)"
        ADAPT_DOC[📑 DoclingAdapter<br/>Docling]
        ADAPT_EMB[🔢 GeminiEmbedder<br/>text-embedding-004]
        ADAPT_VEC[🗄️ ChromaAdapter<br/>ChromaDB]
        ADAPT_CTX[💾 GeminiCacheManager<br/>Context Caching API]
    end
    
    subgraph "Domain Layer"
        MODEL_LAW[⚖️ LawDocument]
        MODEL_CACHE[💾 CacheSession]
        MODEL_RESULT[📊 QueryResult]
    end
    
    subgraph "External Storage"
        FILES[📁 Markdown Files<br/>data/processed/]
        CHROMA[(ChromaDB<br/>data/chroma_db/)]
    end
    
    %% User interactions
    USER --> UI
    USER -.setup.-> SETUP
    
    %% UI flow
    UI --> RETRIEVE
    SETUP --> INGEST
    
    %% Service dependencies
    INGEST --> PORT_DOC
    INGEST --> PORT_EMB
    INGEST --> PORT_VEC
    
    RETRIEVE --> PORT_EMB
    RETRIEVE --> PORT_VEC
    RETRIEVE --> PORT_CTX
    
    %% Port -> Adapter bindings
    PORT_DOC -.implements.- ADAPT_DOC
    PORT_EMB -.implements.- ADAPT_EMB
    PORT_VEC -.implements.- ADAPT_VEC
    PORT_CTX -.implements.- ADAPT_CTX
    
    %% Adapter interactions
    ADAPT_DOC --> WEB
    ADAPT_DOC --> FILES
    ADAPT_EMB --> GEMINI
    ADAPT_VEC --> CHROMA
    ADAPT_CTX --> FILES
    ADAPT_CTX --> GEMINI
    
    %% Domain usage
    INGEST -.uses.- MODEL_LAW
    RETRIEVE -.uses.- MODEL_CACHE
    RETRIEVE -.creates.- MODEL_RESULT
    
    classDef serviceClass fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef portClass fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef adapterClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef domainClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class INGEST,RETRIEVE serviceClass
    class PORT_DOC,PORT_EMB,PORT_VEC,PORT_CTX portClass
    class ADAPT_DOC,ADAPT_EMB,ADAPT_VEC,ADAPT_CTX adapterClass
    class MODEL_LAW,MODEL_CACHE,MODEL_RESULT domainClass
```

## Data Flow Diagrams

### Ingestion Flow (One-time Setup)

```mermaid
sequenceDiagram
    actor Admin
    participant Script as setup_db.py
    participant Ingest as IngestionService
    participant DocProc as DoclingAdapter
    participant Embed as GeminiEmbedder
    participant Vector as ChromaAdapter
    participant Files as MD Files
    participant DB as ChromaDB
    
    Admin->>Script: Run setup
    Script->>Ingest: ingest_from_config()
    
    loop For each law in config
        Ingest->>DocProc: process_url(url, law_id)
        DocProc->>DocProc: Convert with Docling
        DocProc->>Files: Save as .md
        DocProc-->>Ingest: (file_path, content)
        
        Ingest->>Ingest: Extract summary
        Ingest->>Embed: embed_text(title + summary)
        Embed-->>Ingest: embedding vector
        
        Ingest->>Vector: save_document(law_doc, embedding)
        Vector->>DB: Store metadata + embedding
    end
    
    Ingest-->>Script: List of processed docs
    Script-->>Admin: ✓ Setup complete
```

### Retrieval Flow (User Query)

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant Retrieval as RetrievalService
    participant Embed as GeminiEmbedder
    participant Vector as ChromaAdapter
    participant Cache as GeminiCacheManager
    participant Gemini as Gemini API
    participant Files as MD Files
    
    User->>UI: Ask question
    UI->>Retrieval: query(user_query)
    
    Retrieval->>Embed: embed_text(query)
    Embed-->>Retrieval: query_embedding
    
    Retrieval->>Vector: search(query_embedding, top_k=1)
    Vector-->>Retrieval: [most_relevant_law]
    
    Retrieval->>Cache: get_or_create_cache(law_doc)
    Cache->>Files: Read law MD file
    Cache->>Cache: Compute content hash
    
    alt Cache exists
        Cache->>Gemini: Check caching.CachedContent.list()
        Gemini-->>Cache: Existing cache found
        Cache-->>Retrieval: CacheSession (reused)
    else No cache
        Cache->>Gemini: caching.CachedContent.create()
        Gemini-->>Cache: New cache created
        Cache-->>Retrieval: CacheSession (new)
    end
    
    Retrieval->>Cache: generate_answer(cache, query)
    Cache->>Gemini: model.generate_content(query)
    Gemini-->>Cache: Generated answer
    Cache-->>Retrieval: answer
    
    Retrieval-->>UI: QueryResult
    UI-->>User: Display answer + metadata
```

## Design Decisions

### 1. Document-Level vs. Chunk-Level RAG

**Decision:** Store entire laws in Gemini Cache instead of chunking.

**Rationale:**
- Laws need complete context to answer correctly
- Gemini 1.5 Pro supports 2M token context window
- Context Caching reduces cost by ~90% for repeated queries
- Simpler architecture (no chunk merging logic needed)

**Trade-offs:**
- ✅ Higher answer quality (full context)
- ✅ 90% cost reduction after cache creation
- ✅ Faster responses on cache hit (<1s)
- ❌ Higher initial cost to create cache
- ❌ Only works for documents that fit in context window

### 2. Hexagonal Architecture

**Decision:** Strict separation of Ports (interfaces) and Adapters (implementations).

**Rationale:**
- Easy to swap implementations (e.g., different vector DB)
- Testable with mocks
- Clear dependency flow (Domain ← Services ← Ports → Adapters)

**Example:** If we want to switch from ChromaDB to Pinecone, we only change `ChromaAdapter` without touching services.

### 3. Vector Store Strategy

**Decision:** Index only title + summary, store file path in metadata.

**Rationale:**
- Vector DB becomes a lightweight "table of contents"
- Full content loaded from files when needed
- Faster indexing and cheaper storage

### 4. Cache Management

**Decision:** 1-hour TTL with content hash validation.

**Rationale:**
- Laws rarely change (1 hour is reasonable)
- Content hash prevents stale caches on updates
- Automatic cache reuse across sessions

## Cost Analysis

### Traditional RAG (No Caching)

For a medium law (~50k tokens):

| Query # | Input Tokens | Output Tokens | Cost (USD) |
|---------|--------------|---------------|------------|
| Query 1 | 50,000       | 500           | $0.75      |
| Query 2 | 50,000       | 500           | $0.75      |
| Query 3 | 50,000       | 500           | $0.75      |
| **Total (3 queries)** | **150,000** | **1,500** | **$2.25** |

### With Context Caching

| Query # | Input Tokens | Cached Tokens | Output Tokens | Cost (USD) |
|---------|--------------|---------------|---------------|------------|
| Cache creation | 50,000 | - | - | $0.50 |
| Query 1 | 100 | 50,000 | 500 | $0.05 |
| Query 2 | 100 | 50,000 | 500 | $0.05 |
| Query 3 | 100 | 50,000 | 500 | $0.05 |
| **Total (3 queries)** | **50,300** | **150,000** | **1,500** | **$0.65** |

**Savings:** ~71% cost reduction for 3 queries, ~90% per query after cache creation.

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Gemini 1.5 Pro | Answer generation with context caching |
| Embeddings | text-embedding-004 | Semantic search |
| Document Processing | Docling (IBM) | Web → Markdown conversion |
| Vector DB | ChromaDB | Local vector storage |
| Web UI | Streamlit | User interface |
| Configuration | Pydantic Settings | Environment management |

## File Structure

```
rag_app/
├── config/              # Configuration
│   ├── leyes_config.json
│   └── settings.py
├── domain/              # Domain models
│   └── models.py
├── ports/               # Interface definitions
│   ├── chunker.py      (DocumentProcessorPort)
│   ├── embedder.py
│   ├── vector_store.py
│   └── contextualizer.py
├── adapters/            # Implementations
│   ├── chunkers/
│   │   └── docling_adapter.py
│   ├── embedders/
│   │   └── gemini_embedder.py
│   ├── stores/
│   │   └── chroma_adapter.py
│   └── contextualizers/
│       └── gemini_manager.py
├── services/            # Business logic orchestration
│   ├── ingestion_service.py
│   └── retrieval_service.py
├── scripts/             # Utility scripts
│   └── setup_db.py
├── utils/               # Cross-cutting concerns
│   └── logger.py
├── main.py             # Streamlit UI entry point
└── tests/              # Tests
    └── audit_performance.py
```

## Future Enhancements

1. **Multi-Law Queries:** Combine multiple laws in one cache
2. **Incremental Updates:** Update individual laws without re-ingesting all
3. **Advanced Routing:** LLM-based query routing to select relevant laws
4. **Cost Tracker:** Real-time cost monitoring dashboard
5. **Export Functionality:** Save Q&A sessions as PDF reports
6. **Authentication:** Multi-user support with usage tracking

## References

- [Gemini Context Caching Documentation](https://ai.google.dev/gemini-api/docs/caching)
- [Docling Documentation](https://github.com/DS4SD/docling)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Hexagonal Architecture Pattern](https://alistair.cockburn.us/hexagonal-architecture/)
