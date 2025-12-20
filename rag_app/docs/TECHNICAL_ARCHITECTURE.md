# Legal AI RAG - Technical Architecture Documentation

> **For Developers & AI Language Models**

This document provides a comprehensive technical overview of the Legal AI RAG system architecture, module responsibilities, and data flow.

---

## 🏗️ Architecture Pattern: Hexagonal Architecture (Ports & Adapters)

The system implements **Hexagonal Architecture** (also known as Ports and Adapters) to achieve:

- **Technology agnostic core**: Domain logic independent of external frameworks
- **Testability**: Easy to mock dependencies via interfaces
- **Flexibility**: Swap implementations without changing business logic (e.g., ChromaDB → Pinecone)
- **Clear boundaries**: Explicit separation between domain, application, and infrastructure layers

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                    (main.py - Streamlit)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   APPLICATION LAYER                          │
│          (Services - Business Orchestration)                 │
│  • IngestionService                                          │
│  • RetrievalService                                          │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
      ┌────────▼────────┐         ┌───────▼──────────┐
      │  DOMAIN LAYER   │         │  PORTS (Interfaces)│
      │  (Models)       │         │  • DocumentProcessor │
      │  • LawDocument  │         │  • EmbedderPort    │
      │  • CacheSession │         │  • VectorStorePort │
      │  • QueryResult  │         │  • ContextualizerPort│
      └─────────────────┘         └───────┬──────────┘
                                          │
                           ┌──────────────▼──────────────┐
                           │   ADAPTERS (Implementations) │
                           │   • DoclingAdapter           │
                           │   • GeminiEmbedder          │
                           │   • ChromaAdapter           │
                           │   • GeminiCacheManager      │
                           └─────────────────────────────┘
                                          │
                           ┌──────────────▼──────────────┐
                           │   EXTERNAL SERVICES         │
                           │   • Google Gemini API       │
                           │   • ChromaDB (local)        │
                           │   • Docling Library         │
                           └─────────────────────────────┘
```

---

## 📦 Module Responsibilities

### **1. Domain Layer** (`domain/models.py`)

**Purpose**: Pure business entities with zero dependencies on external libraries.

**Components**:

- **`LawDocument`**: Core entity representing a legal document
  ```python
  @dataclass
  class LawDocument:
      id: str                    # Unique identifier
      titulo: str                # Document title
      url: str                   # Source URL (or file://)
      file_path: str            # Path to processed .md file
      summary: str              # Brief summary for embedding
      metadata: dict            # Additional metadata (año, categoria, etc.)
  ```

- **`CacheSession`**: Tracks Gemini context cache lifecycle
  ```python
  @dataclass
  class CacheSession:
      cache_id: str             # Google cache identifier
      law_id: str               # Associated law
      content_hash: str         # SHA256 of content
      expiration_time: datetime # Cache TTL
      model_name: str           # Gemini model used
  ```

- **`QueryResult`**: Query response with metadata
  ```python
  @dataclass
  class QueryResult:
      answer: str               # LLM-generated answer
      law_document: LawDocument # Source law
      confidence_score: float   # Relevance score
      cache_used: bool          # Was cache reused?
      cache_id: Optional[str]   # Cache identifier
      response_time_ms: float   # Response time
  ```

**Key Principle**: No imports from `google.generativeai`, `chromadb`, etc. Only standard library.

---

### **2. Ports Layer** (`ports/`)

**Purpose**: Define contracts (interfaces) that adapters must implement. Enables dependency inversion.

#### `ports/chunker.py` → **DocumentProcessorPort**

```python
class DocumentProcessorPort(Protocol):
    def process_url(self, url: str, law_id: str) -> Tuple[str, str]:
        """Convert URL/file to markdown.
        
        Returns: (file_path, markdown_content)
        """
```

**Contract**: Any document processor must take a URL/file and return markdown.

#### `ports/embedder.py` → **EmbedderPort**

```python
class EmbedderPort(Protocol):
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation."""
```

**Contract**: Any embedder must convert text → vector representation.

#### `ports/vector_store.py` → **VectorStorePort**

```python
class VectorStorePort(Protocol):
    def save_document(self, law_doc: LawDocument, embedding: List[float]) -> None:
        """Index document with its embedding."""
    
    def search(self, query_embedding: List[float], top_k: int) -> List[LawDocument]:
        """Semantic search by vector similarity."""
    
    def get_by_id(self, law_id: str) -> Optional[LawDocument]:
        """Retrieve document by ID."""
```

**Contract**: Any vector store must support index, search, retrieve operations.

#### `ports/contextualizer.py` → **ContextualizerPort**

```python
class ContextualizerPort(Protocol):
    def get_or_create_cache(self, law_doc: LawDocument) -> Optional[CacheSession]:
        """Create or reuse context cache."""
    
    def generate_answer(self, cache_session: Optional[CacheSession], 
                       query: str, law_doc: LawDocument) -> str:
        """Generate answer with or without cache."""
```

**Contract**: Any contextualizer must handle caching lifecycle and answer generation.

---

### **3. Adapters Layer** (`adapters/`)

**Purpose**: Concrete implementations of ports using specific technologies.

#### `adapters/chunkers/docling_adapter.py` → **DoclingAdapter**

**Technology**: IBM Docling library

**Responsibilities**:
- Download/read documents from URLs or files
- Convert to structured markdown
- Save to `data/processed/`

**Key Implementation**:
```python
def process_url(self, url: str, law_id: str) -> Tuple[str, str]:
    # Use Docling to convert web/file → markdown
    result = self.converter.convert(url)
    md_content = result.document.export_to_markdown()
    
    # Save locally
    file_path = settings.processed_docs_path / f"{law_id}.md"
    file_path.write_text(md_content)
    
    return (str(file_path), md_content)
```

#### `adapters/embedders/gemini_embedder.py` → **GeminiEmbedder**

**Technology**: Google Gemini `text-embedding-004`

**Responsibilities**:
- Generate 768-dimensional embeddings
- Batch processing for efficiency

**Key Implementation**:
```python
def embed_text(self, text: str) -> List[float]:
    result = genai.embed_content(
        model=self.model_name,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']
```

#### `adapters/stores/chroma_adapter.py` → **ChromaAdapter**

**Technology**: ChromaDB (local persistence)

**Responsibilities**:
- Store embeddings with metadata
- Cosine similarity search
- **Critical**: Only indexes `title + summary`, NOT full text
- Stores `file_path` pointer to full markdown

**Key Design Decision**:
```python
# LIGHTWEIGHT INDEX
searchable_text = f"{law_doc.titulo}\n\n{law_doc.summary}"
embedding = <embed searchable_text>

# Store pointer to full content
metadata = {
    "law_id": law_doc.id,
    "titulo": law_doc.titulo,
    "file_path": law_doc.file_path,  # ← Full text location
    "url": law_doc.url,
    ...
}
```

**Why?** Full laws are 20k-50k tokens. Embedding only title+summary keeps vector DB small and fast.

#### `adapters/contextualizers/gemini_manager.py` → **GeminiCacheManager**

**Technology**: Google Gemini 2.5-flash with Context Caching API

**Responsibilities**:
1. **Cache Management**: Create, reuse, list, delete caches
2. **Content Hashing**: SHA256 to detect content changes
3. **Free Tier Detection**: Graceful degradation when caching unavailable
4. **Dual Mode**:
   - **Mode 1 (Paid Tier)**: Use `caching.CachedContent.create()` + cache reuse
   - **Mode 2 (Free Tier)**: Direct model calls with full context

**Key Implementation (Free Tier Handling)**:
```python
def _create_cache(self, law_doc, content, content_hash):
    if not self.caching_available:
        return None  # Skip cache creation
    
    try:
        cache = caching.CachedContent.create(
            model="gemini-2.5-flash",
            contents=[content],
            ttl=timedelta(minutes=60)
        )
        return CacheSession(...)
    
    except Exception as e:
        if "429" in str(e) and "TotalCachedContentStorageTokensPerModelFreeTier" in str(e):
            logger.warning("Free Tier detected. Disabling caching.")
            self.caching_available = False
            return None
        raise

def generate_answer(self, cache_session, query, law_doc):
    if cache_session is not None:
        # MODE 1: Use cached content
        model = genai.GenerativeModel.from_cached_content(cache_session.cache_id)
        return model.generate_content(query).text
    else:
        # MODE 2: Fallback - direct call with full context
        content = Path(law_doc.file_path).read_text()
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=...)
        return model.generate_content([content, query]).text
```

**Critical Feature**: System remains fully functional even when caching is unavailable.

---

### **4. Services Layer** (`services/`)

**Purpose**: Orchestrate workflows using ports (dependency injection). Business logic resides here.

#### `services/ingestion_service.py` → **IngestionService**

**Workflow**: `URLs → Markdown → Embeddings → Vector DB`

**Dependencies (injected)**:
- `DocumentProcessorPort` (e.g., DoclingAdapter)
- `EmbedderPort` (e.g., GeminiEmbedder)
- `VectorStorePort` (e.g., ChromaAdapter)

**Process**:
```python
def ingest_all_laws(self):
    laws = load_from_config("leyes_config.json")
    
    for law in laws:
        # Step 1: Process URL → markdown
        file_path, md_content = self.processor.process_url(law['url'], law['id'])
        
        # Step 2: Extract summary (first 500 chars)
        summary = md_content[:500]
        
        # Step 3: Create LawDocument
        law_doc = LawDocument(id=law['id'], titulo=law['nombre'], 
                             file_path=file_path, summary=summary, ...)
        
        # Step 4: Generate embedding
        searchable_text = f"{law_doc.titulo}\n\n{law_doc.summary}"
        embedding = self.embedder.embed_text(searchable_text)
        
        # Step 5: Save to vector store
        self.vector_store.save_document(law_doc, embedding)
```

**Key Principle**: Service knows the *workflow*, not the *implementation details*.

#### `services/retrieval_service.py` → **RetrievalService**

**Workflow**: `Query → Embedding → Search → Cache → Answer`

**Dependencies (injected)**:
- `EmbedderPort`
- `VectorStorePort`
- `ContextualizerPort`

**Process**:
```python
def query(self, user_query: str) -> QueryResult:
    # Step 1: Embed query
    query_embedding = self.embedder.embed_text(user_query)
    
    # Step 2: Semantic search
    similar_docs = self.vector_store.search(query_embedding, top_k=1)
    law_doc = similar_docs[0]  # Most relevant law
    
    # Step 3: Get or create cache (may return None on Free Tier)
    cache_session = self.contextualizer.get_or_create_cache(law_doc)
    
    # Step 4: Generate answer (with or without cache)
    answer = self.contextualizer.generate_answer(cache_session, user_query, law_doc)
    
    # Step 5: Return result
    return QueryResult(
        answer=answer,
        law_document=law_doc,
        cache_used=(cache_session is not None and not cache_session.is_expired),
        ...
    )
```

---

### **5. Configuration Layer** (`config/`)

#### `config/settings.py` → **Settings**

**Technology**: Pydantic Settings (`.env` loader)

**Responsibilities**:
- Load environment variables
- Provide defaults
- Auto-create directories

**Critical Settings**:
```python
gemini_api_key: str                        # Required
llm_model: str = "gemini-2.5-flash"       # Model for generation
embedding_model: str = "models/text-embedding-004"
cache_ttl_minutes: int = 60                # Cache lifetime
processed_docs_path: Path                  # data/processed/
chroma_db_path: Path                       # data/chroma_db/
```

#### `config/leyes_config.json` → Law Database

**Structure**:
```json
{
  "leyes": [
    {
      "numero": "24714",
      "nombre": "Sistema Integrado de Jubilaciones",
      "url": "https://...",
      "año": 1996,
      "categoria": "Jubilaciones",
      "descripcion_breve": "..."
    }
  ]
}
```

---

### **6. Entry Points**

#### `scripts/setup_from_md.py` → **Offline Ingestion Script**

**Purpose**: Initialize system using local `.md` files (bypassing URL downloads).

**When to use**: Government URLs are down, or testing with existing markdown.

**Process**:
1. Read `Anses1.md`
2. Copy to `data/processed/`
3. Generate embedding
4. Save to ChromaDB

#### `scripts/setup_db.py` → **Online Ingestion Script**

**Purpose**: Initialize system from URLs in `leyes_config.json`.

**When to use**: When URLs are accessible and you want fresh data.

#### `main.py` → **Streamlit UI**

**Purpose**: User-facing web interface.

**Features**:
- Query input
- Answer display
- Metadata (time, cache status, law info)
- System stats sidebar

---

## 🔄 Data Flow Diagrams

### Ingestion Flow

```
┌─────────────┐
│ leyes_config│
│   .json     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ IngestionService │
└────────┬─────────┘
         │
         ├─────► DocumentProcessor ──► URL/File ──► Markdown (.md)
         │                                              │
         │                                              ▼
         │                                    ┌─────────────────┐
         │                                    │ data/processed/ │
         │                                    │  ley_xxx.md     │
         │                                    └─────────────────┘
         │
         ├─────► Extract summary (first 500 chars)
         │
         ├─────► GeminiEmbedder ──► embedding vector [768 dims]
         │
         └─────► ChromaAdapter ──► Save (embedding + metadata)
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ ChromaDB         │
                                    │ {id, embedding,  │
                                    │  file_path, ...} │
                                    └──────────────────┘
```

### Query Flow

```
┌──────────────┐
│ User Query   │
│ "¿Requisitos?│
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│RetrievalService │
└────────┬────────┘
         │
         ├─────► GeminiEmbedder ──► query_embedding [768]
         │
         ├─────► ChromaAdapter.search(query_embedding)
         │            │
         │            ▼
         │       ┌────────────────┐
         │       │ Most similar:  │
         │       │ ley_anses_001  │
         │       │ file_path: ... │
         │       └────────┬───────┘
         │                │
         ├────────────────┘
         │
         ├─────► GeminiCacheManager.get_or_create_cache(law_doc)
         │            │
         │            ├──► Read file_path → full markdown content
         │            └──► Check if cache exists (by content hash)
         │                 │
         │                 ├─► Cache exists? → Reuse (CacheSession)
         │                 └─► No cache? 
         │                      ├─► Free Tier? → Return None
         │                      └─► Paid? → Create cache (CacheSession)
         │
         └─────► GeminiCacheManager.generate_answer(cache, query, law_doc)
                  │
                  ├─► cache != None? → Use cached_content
                  └─► cache == None? → Direct call with full content
                       │
                       ▼
                  ┌────────────────┐
                  │ Gemini 2.5     │
                  │ LLM Response   │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  QueryResult   │
                  │  - answer      │
                  │  - law_doc     │
                  │  - cache_used  │
                  │  - time_ms     │
                  └────────────────┘
```

---

## 🎯 Key Design Decisions

### 1. **Document-Level RAG vs Chunk-Level RAG**

**Choice**: Document-Level

**Rationale**:
- Legal documents require full context for accurate interpretation
- Gemini 2.5 supports 2M token context (can fit entire laws)
- Eliminates chunk boundary issues
- Better citation accuracy

**Trade-off**: Slower for very large corpora (10,000+ laws). Mitigated by:
- Indexing only title+summary (fast retrieval)
- Caching full context (amortizes cost)

### 2. **Lightweight Vector Store**

**Choice**: Index title+summary, NOT full text

**Rationale**:
- Vector DB storage cost
- Faster similarity search
- Full text stored cheaply as `.md` files

**Pointer Pattern**:
```
ChromaDB: [embedding, {file_path: "/data/processed/ley_123.md"}]
                                        ↓
Full Content: Read from file_path when needed
```

### 3. **Graceful Degradation (Free Tier)**

**Choice**: Detect API limits, fallback to direct calls

**Rationale**:
- System must work with free API keys
- Caching is optimization, not requirement
- Transparent to user (slower but functional)

**Implementation**:
```python
if error_429 and "FreeTier" in error:
    self.caching_available = False
    # Continue with direct model calls
```

### 4. **Content Hashing for Cache Invalidation**

**Choice**: SHA256 of markdown content

**Rationale**:
- Detect when law text changes
- Avoid serving stale cached answers
- Automatic cache refresh

```python
content_hash = hashlib.sha256(md_content.encode()).hexdigest()
cache_name = f"{law_id}_{content_hash[:8]}"
```

### 5. **Hexagonal Architecture**

**Choice**: Strict separation of concerns

**Benefits**:
- **Testability**: Mock `GeminiEmbedder` with `FakeEmbedder` for tests
- **Flexibility**: Swap ChromaDB → Pinecone by implementing `VectorStorePort`
- **Clarity**: Dependencies flow inward (Adapters → Ports → Domain)

**Example of swapping**:
```python
# Original
vector_store = ChromaAdapter()

# Swap to Pinecone (just implement VectorStorePort)
vector_store = PineconeAdapter()

# Services don't change!
ingestion_service = IngestionService(..., vector_store=vector_store)
```

---

## 🧪 Testing Strategy

### Unit Tests (Recommended)

```python
# Test service with mocks
def test_retrieval_service():
    fake_embedder = FakeEmbedder()
    fake_store = FakeVectorStore()
    fake_contextualizer = FakeCacheManager()
    
    service = RetrievalService(fake_embedder, fake_store, fake_contextualizer)
    result = service.query("test question")
    
    assert result.answer is not None
```

### Integration Test

See `tests/audit_performance.py` for real API integration test.

---

## 📊 Performance Characteristics

### With Caching (Paid Tier)

| Metric | First Query | Subsequent Queries |
|--------|-------------|-------------------|
| Time | ~15 seconds | ~2 seconds |
| Cost | ~$0.50 | ~$0.05 |
| Tokens Input | 30,000 (full law) | 50 (query only) |
| Tokens Cached | 0 | 30,000 |

**Savings**: ~90% cost reduction, ~86% time reduction

### Without Caching (Free Tier)

| Metric | Every Query |
|--------|-------------|
| Time | ~15 seconds |
| Cost | ~$0.00 (free) |
| Tokens Input | 30,000 |

**Trade-off**: Slower, but functional and free.

---

## 🔧 Extension Points

### Want to add a new model provider (e.g., OpenAI)?

1. Create `adapters/embedders/openai_embedder.py` implementing `EmbedderPort`
2. Create `adapters/contextualizers/openai_manager.py` implementing `ContextualizerPort`
3. Inject in `main.py`:
   ```python
   embedder = OpenAIEmbedder()
   contextualizer = OpenAICacheManager()
   ```

No changes to domain, ports, or services required!

### Want to add multi-law queries?

Modify `retrieval_service.py`:
```python
def query_multi_law(self, user_query: str, top_k: int = 3):
    similar_docs = self.vector_store.search(query_embedding, top_k=3)
    
    # Combine contexts
    combined_context = "\n\n".join([
        Path(doc.file_path).read_text() for doc in similar_docs
    ])
    
    # Generate answer with combined context
    ...
```

### Want to add authentication?

Add `adapters/auth/` with `AuthPort`, implement with Firebase/Auth0/etc. Inject into `main.py`.

---

## 📝 Summary for AI Models

**If you're an AI model maintaining/extending this codebase:**

1. **Respect the hexagonal architecture**: Changes to external APIs go in `adapters/`, not `services/`
2. **Use dependency injection**: Services receive ports, not concrete classes
3. **Free Tier is a first-class citizen**: Always handle `caching_available = False`
4. **File paths are absolute**: All paths use `settings.processed_docs_path` / `chroma_db_path`
5. **Content hashing is critical**: Don't bypass it or cache invalidation breaks
6. **Document-level is the strategy**: Don't chunk without understanding the trade-offs

**Common modification patterns**:
- Adding a feature → Update `services/`
- Swapping technology → Replace `adapters/`, keep same port
- New data model → Add to `domain/models.py`
- Configuration change → Edit `settings.py` and `.env`

---

## 📚 References

- **Hexagonal Architecture**: Alistair Cockburn (2005)
- **Gemini Context Caching**: https://ai.google.dev/gemini-api/docs/caching
- **ChromaDB**: https://docs.trychroma.com/
- **Docling**: https://github.com/DS4SD/docling

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-07  
**Maintainer**: System Architect
