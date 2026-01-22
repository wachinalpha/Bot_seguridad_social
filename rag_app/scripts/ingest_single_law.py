#!/usr/bin/env python3
"""
Script para ingestar una ley específica desde leyes_config.json

Uso:
    python -m rag_app.scripts.ingest_single_law 24714
    python -m rag_app.scripts.ingest_single_law --list
    
Con Docker:
    docker compose run --rm ingest python -m rag_app.scripts.ingest_single_law 24714
"""
import json
import sys
import argparse
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.services.ingestion_service import IngestionService


def load_leyes_config(config_path=None):
    """Load leyes configuration file."""
    if config_path is None:
        config_path = Path(settings.base_dir) / "rag_app" / "config" / "leyes_config.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config.get('leyes', [])


def find_law_by_number(leyes, numero):
    """Find a law in the config by its number."""
    for ley in leyes:
        if str(ley.get('numero')) == str(numero):
            return ley
    return None


def list_available_laws(leyes):
    """Print all available laws."""
    print("\n📚 Leyes disponibles en leyes_config.json:\n")
    print(f"{'Número':<15} {'Año':<6} {'Categoría':<25} {'Nombre'}")
    print("-" * 100)
    
    for ley in leyes:
        numero = ley.get('numero', 'N/A')
        año = ley.get('año', 'N/A')
        categoria = ley.get('categoria', 'N/A')
        nombre = ley.get('nombre', 'Sin nombre')
        # Truncate name if too long
        if len(nombre) > 50:
            nombre = nombre[:47] + "..."
        print(f"{numero:<15} {año:<6} {categoria:<25} {nombre}")
    
    print(f"\nTotal: {len(leyes)} leyes configuradas")
    print("\nUso: python -m rag_app.scripts.ingest_single_law [NUMERO]")


def main():
    parser = argparse.ArgumentParser(
        description='Ingestar una ley específica desde leyes_config.json'
    )
    parser.add_argument(
        'numero',
        nargs='?',
        help='Número de la ley a ingestar (ej: 24714, 593-2016)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Listar todas las leyes disponibles'
    )
    parser.add_argument(
        '--config',
        help='Ruta al archivo leyes_config.json (opcional)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        leyes = load_leyes_config(args.config)
    except FileNotFoundError:
        print("❌ Error: No se encontró leyes_config.json")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Error: leyes_config.json tiene formato inválido")
        sys.exit(1)
    
    # List mode
    if args.list:
        list_available_laws(leyes)
        sys.exit(0)
    
    # Check if number provided
    if not args.numero:
        print("❌ Error: Debes especificar el número de ley")
        print("   Uso: python -m rag_app.scripts.ingest_single_law 24714")
        print("   O ejecutá con --list para ver leyes disponibles")
        sys.exit(1)
    
    # Find the law
    ley = find_law_by_number(leyes, args.numero)
    if not ley:
        print(f"❌ Error: Ley '{args.numero}' no encontrada en leyes_config.json")
        print(f"   Ejecutá con --list para ver leyes disponibles")
        sys.exit(1)
    
    # Print law info
    print(f"\n📋 Ingesta de ley seleccionada:")
    print(f"   Número: {ley.get('numero')}")
    print(f"   Nombre: {ley.get('nombre')}")
    print(f"   URL: {ley.get('url')}")
    print(f"   Categoría: {ley.get('categoria', 'N/A')}")
    print(f"   Corpus version: {settings.corpus_version}")
    print()
    
    # Initialize services
    print("🔧 Inicializando servicios...")
    try:
        embedder = GeminiEmbedder()
        vector_store = ChromaAdapter()
        
        # Document processor (DoclingAdapter)
        from rag_app.adapters.chunkers.docling_adapter import DoclingAdapter
        document_processor = DoclingAdapter()
        
        ingestion_service = IngestionService(
            document_processor=document_processor,
            embedder=embedder,
            vector_store=vector_store
        )
        
        print("✅ Servicios inicializados\n")
        
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Ingest the law
    print(f"📚 Procesando ley {ley.get('numero')}...")
    try:
        law_doc = ingestion_service.ingest_law(ley)
        print(f"\n✅ Ley {law_doc.id} ingresada exitosamente")
        print(f"   Título: {law_doc.titulo}")
        print(f"   File: {law_doc.file_path}")
        print(f"   Collection: {settings.chroma_collection_name_versioned}")
        
    except Exception as e:
        print(f"\n❌ Error ingresando ley {ley.get('numero')}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Summary
    print(f"\n📊 Resumen:")
    print(f"   Total documentos en ChromaDB: {vector_store.count_documents()}")
    print(f"   Versión del corpus: {settings.corpus_version}")
    print()


if __name__ == "__main__":
    main()
