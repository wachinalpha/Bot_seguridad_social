"""
Retrieval metrics: Hit Rate, Precision@k, NDCG@k.

These are computed locally without calling the LLM.
Inputs come from the API response field `law_documents[].id`.
"""

import math
from typing import List


def hit_rate(retrieved_ids: List[str], expected_ids: List[str]) -> float:
    """
    1.0 if any expected document was retrieved, else 0.0.
    Also called Recall@k (binary version).
    """
    if not expected_ids:
        return 1.0  # out-of-scope cases: no docs expected
    return 1.0 if any(d in retrieved_ids for d in expected_ids) else 0.0


def precision_at_k(retrieved_ids: List[str], expected_ids: List[str]) -> float:
    """
    Fraction of retrieved documents that are relevant.
    Precision@k = |relevant ∩ retrieved| / |retrieved|
    """
    if not retrieved_ids:
        return 0.0
    if not expected_ids:
        return 1.0  # out-of-scope: no docs expected, none retrieved = perfect
    relevant = sum(1 for d in retrieved_ids if d in expected_ids)
    return relevant / len(retrieved_ids)


def ndcg_at_k(retrieved_ids: List[str], expected_ids: List[str]) -> float:
    """
    Normalized Discounted Cumulative Gain @k.
    Rewards finding the right doc in position 1 more than position 3.
    """
    if not expected_ids:
        return 1.0  # out-of-scope: correct if nothing expected

    def dcg(ids: List[str]) -> float:
        score = 0.0
        for i, doc_id in enumerate(ids):
            relevance = 1.0 if doc_id in expected_ids else 0.0
            score += relevance / math.log2(i + 2)  # log2(rank+1)
        return score

    actual_dcg = dcg(retrieved_ids)
    # Ideal: all relevant docs in top positions
    ideal_ids = [d for d in retrieved_ids if d in expected_ids] + \
                [d for d in retrieved_ids if d not in expected_ids]
    ideal_dcg = dcg(ideal_ids)

    if ideal_dcg == 0:
        return 0.0
    return actual_dcg / ideal_dcg
