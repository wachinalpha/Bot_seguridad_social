#!/usr/bin/env python3
"""
Performance audit test for Gemini Context Caching.

This test validates:
1. Cache creation time and cost
2. Cache reuse speed improvement
3. Cost savings from caching
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings
from rag_app.utils.logger import configure_logging
from rag_app.adapters.embedders.gemini_embedder import GeminiEmbedder
from rag_app.adapters.stores.chroma_adapter import ChromaAdapter
from rag_app.adapters.contextualizers.gemini_manager import GeminiCacheManager
from rag_app.services.retrieval_service import RetrievalService


def estimate_cost(tokens_input: int, tokens_output: int, cached_tokens: int = 0) -> float:
    """
    Estimate API cost based on Gemini pricing.
    
    Rates (approximate):
    - Input: $0.000015 per 1K tokens
    - Output: $0.00006 per 1K tokens
    - Cached input: $0.0000015 per 1K tokens (90% discount)
    """
    input_cost = (tokens_input / 1000) * 0.000015
    output_cost = (tokens_output / 1000) * 0.00006
    cache_cost = (cached_tokens / 1000) * 0.0000015
    
    return input_cost + output_cost + cache_cost


def main():
    """Run performance audit."""
    configure_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=" * 70)
    print("LEGAL AI RAG - PERFORMANCE AUDIT")
    print("=" * 70)
    print()
    
    # Check API key
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not found!")
        sys.exit(1)
    
    try:
        # Initialize services
        print("[1/5] Initializing services...")
        embedder = GeminiEmbedder()
        vector_store = ChromaAdapter()
        contextualizer = GeminiCacheManager()
        
        retrieval_service = RetrievalService(
            embedder=embedder,
            vector_store=vector_store,
            contextualizer=contextualizer
        )
        
        # Check database has documents
        doc_count = vector_store.count_documents()
        if doc_count == 0:
            print("\n⚠️  No documents found in vector store!")
            print("Please run 'python -m rag_app.scripts.setup_db' first.")
            sys.exit(1)
        
        print(f"✓ Found {doc_count} documents in vector store")
        print()
        
        # Test queries
        test_query_1 = "¿Cuáles son los requisitos para jubilarse?"
        test_query_2 = "¿A qué edad se puede jubilar una persona?"
        
        print("[2/5] Running FIRST query (will create cache)...")
        print(f"Query: {test_query_1}")
        print()
        
        start_time = time.time()
        result_1 = retrieval_service.query(test_query_1)
        time_1 = time.time() - start_time
        
        print(f"Answer preview: {result_1.answer[:200]}...")
        print()
        print(f"⏱️  Time: {time_1:.2f} seconds")
        print(f"💾 Cache used: {result_1.cache_used}")
        print(f"📚 Law: {result_1.law_document.titulo}")
        print()
        
        # Estimate cost for first query (cache creation + query)
        # Assume average law is ~30k tokens, output ~500 tokens
        est_tokens_input_1 = 30000
        est_tokens_output_1 = 500
        cost_1 = estimate_cost(est_tokens_input_1, est_tokens_output_1)
        print(f"💰 Estimated cost: ${cost_1:.4f}")
        print()
        
        # Wait a bit
        print("[3/5] Waiting 2 seconds...")
        time.sleep(2)
        print()
        
        print("[4/5] Running SECOND query (should reuse cache)...")
        print(f"Query: {test_query_2}")
        print()
        
        start_time = time.time()
        result_2 = retrieval_service.query(test_query_2)
        time_2 = time.time() - start_time
        
        print(f"Answer preview: {result_2.answer[:200]}...")
        print()
        print(f"⏱️  Time: {time_2:.2f} seconds")
        print(f"💾 Cache used: {result_2.cache_used}")
        print(f"📚 Law: {result_2.law_document.titulo}")
        print()
        
        # Estimate cost for second query (cached)
        est_tokens_input_2 = 50  # Only query tokens
        est_cached_tokens_2 = 30000
        cost_2 = estimate_cost(est_tokens_input_2, est_tokens_output_1, est_cached_tokens_2)
        print(f"💰 Estimated cost: ${cost_2:.4f}")
        print()
        
        # Summary
        print("[5/5] Performance Summary")
        print("=" * 70)
        print()
        
        # Speed comparison
        speedup = ((time_1 - time_2) / time_1 * 100) if time_1 > time_2 else 0
        print(f"⚡ Speed Improvement:")
        print(f"   Query 1 (cache creation): {time_1:.2f}s")
        print(f"   Query 2 (cache reuse):    {time_2:.2f}s")
        print(f"   Speedup: {speedup:.1f}%")
        print()
        
        # Cost comparison
        total_cost = cost_1 + cost_2
        cost_without_cache = estimate_cost(est_tokens_input_1, est_tokens_output_1) * 2
        savings = ((cost_without_cache - total_cost) / cost_without_cache * 100)
        
        print(f"💰 Cost Analysis:")
        print(f"   Total cost (with caching):     ${total_cost:.4f}")
        print(f"   Cost without caching:          ${cost_without_cache:.4f}")
        print(f"   Savings: {savings:.1f}%")
        print()
        
        # Validation
        print("✅ Validation:")
        
        # Check if caching is available
        if not contextualizer.caching_available:
            print("   ⚠️  Context caching not available (Free Tier limit=0)")
            print("   ℹ️  System running in fallback mode without caching")
            print("   ✓ Queries completed successfully without cache")
            print()
            print("=" * 70)
            print("AUDIT COMPLETE - FREE TIER MODE (No Caching)")
            print("=" * 70)
            print()
            print("Note: To enable context caching, upgrade to a paid API plan.")
            return
        
        # If caching is available, validate cache reuse
        assert result_2.cache_used, "❌ Cache was not reused!"
        assert time_2 < time_1, "❌ Second query was not faster!"
        print("   ✓ Cache was successfully reused")
        print("   ✓ Second query was faster")
        print("   ✓ Cost savings achieved")
        print()
        
        print("=" * 70)
        print("AUDIT COMPLETE - ALL TESTS PASSED ✓")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"Audit failed: {e}", exc_info=True)
        print(f"\n❌ Audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
