import streamlit as st
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.adapters.contextualizers.gemini_manager import GeminiCacheManager
from rag_app.services.retrieval_service import RetrievalService

# Configure logging
configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize services (cached for Streamlit)
@st.cache_resource
def init_services():
    """Initialize all services with dependency injection."""
    try:
        embedder = GeminiEmbedder()
        vector_store = ChromaAdapter()
        contextualizer = GeminiCacheManager()
        
        retrieval_service = RetrievalService(
            embedder=embedder,
            vector_store=vector_store,
            contextualizer=contextualizer
        )
        
        return retrieval_service
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        st.error(f"Error al inicializar servicios: {e}")
        return None


def main():
    """Main Streamlit application."""
    
    # Page config
    st.set_page_config(
        page_title="Legal AI RAG - Seguridad Social Argentina",
        page_icon="⚖️",
        layout="wide"
    )
    
    # Title and description
    st.title("⚖️ Legal AI RAG - Seguridad Social Argentina")
    st.markdown("""
    Sistema de consultas sobre leyes de Seguridad Social usando **Gemini Context Caching** 
    (inspirado en NotebookLM).
    
    **Características:**
    - 🔍 Búsqueda semántica de leyes relevantes
    - 💾 Caché de contexto para respuestas rápidas
    - 📄 Respuestas basadas en el texto completo de las leyes
    """)
    
    # Check API key
    if not settings.gemini_api_key:
        st.error("⚠️ GEMINI_API_KEY no configurado. Por favor, configura tu API key.")
        st.stop()
    
    # Initialize services
    retrieval_service = init_services()
    
    if not retrieval_service:
        st.error("No se pudieron inicializar los servicios. Revisa los logs.")
        st.stop()
    
    # Sidebar with info
    with st.sidebar:
        st.header("📊 Información del Sistema")
        
        # Database stats
        try:
            vector_store = ChromaAdapter()
            doc_count = vector_store.count_documents()
            st.metric("Leyes indexadas", doc_count)
        except:
            st.metric("Leyes indexadas", "N/A")
        
        st.markdown("---")
        st.markdown("### 🔧 Configuración")
        st.markdown(f"**Modelo LLM:** `{settings.llm_model}`")
        st.markdown(f"**Modelo Embedding:** `{settings.embedding_model}`")
        st.markdown(f"**Cache TTL:** {settings.cache_ttl_minutes} min")
        
        st.markdown("---")
        st.markdown("### 💡 Sugerencias de consulta")
        st.markdown("""
        - ¿Cuáles son los requisitos para jubilarse?
        - ¿Qué cubre la Ley de Riesgos del Trabajo?
        - ¿Cuáles son las prestaciones de las obras sociales?
        """)
    
    # Main query interface
    st.markdown("---")
    st.header("💬 Hacer una consulta")
    
    # Query input
    user_query = st.text_area(
        "Escribe tu pregunta sobre las leyes de Seguridad Social:",
        height=100,
        placeholder="Ejemplo: ¿Cuáles son los requisitos para la jubilación ordinaria?"
    )
    
    # Query button
    if st.button("🔍 Consultar", type="primary"):
        if not user_query.strip():
            st.warning("Por favor, escribe una pregunta.")
        else:
            with st.spinner("Procesando tu consulta..."):
                try:
                    # Process query
                    result = retrieval_service.query(user_query)
                    
                    # Display results
                    st.markdown("---")
                    st.success("✅ Respuesta generada")
                    
                    # Answer
                    st.markdown("### 📝 Respuesta:")
                    st.markdown(result.answer)
                    
                    # Metadata in columns
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "⚡ Tiempo de respuesta",
                            f"{result.response_time_ms:.0f} ms"
                        )
                    
                    with col2:
                        cache_status = "✅ Reutilizado" if result.cache_used else "🆕 Nuevo"
                        st.metric("💾 Estado del caché", cache_status)
                    
                    with col3:
                        st.metric(
                            "🎯 Confianza",
                            f"{result.confidence_score:.0%}"
                        )
                    
                    # Law info
                    st.markdown("---")
                    st.markdown("### 📚 Ley consultada:")
                    st.info(f"""
                    **{result.law_document.titulo}**
                    
                    - **ID:** {result.law_document.id}
                    - **URL:** {result.law_document.url}
                    - **Categoría:** {result.law_document.metadata.get('categoria', 'N/A')}
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error al procesar la consulta: {e}")
                    logger.error(f"Query error: {e}", exc_info=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        Desarrollado con ❤️ usando Gemini API, Docling, y ChromaDB | Arquitectura Hexagonal
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
