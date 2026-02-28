"""
Refusal quality metrics.

Measures whether the system correctly refuses out-of-scope or 
unanswerable queries, and avoids over-refusing answerable ones.
"""

from tests.eval.metrics.citation import contains_refusal


def refusal_accuracy(answer: str, should_refuse: bool) -> bool:
    """
    Returns True if the system behaved correctly:
    - should_refuse=True  → system DID refuse (correct)
    - should_refuse=False → system did NOT refuse (correct)
    """
    refused = contains_refusal(answer)
    return refused == should_refuse


def is_over_refusal(answer: str, should_refuse: bool) -> bool:
    """
    True = the system refused when it should have answered.
    (False positive refusal → bot is too conservative)
    """
    return (not should_refuse) and contains_refusal(answer)


def is_under_refusal(answer: str, should_refuse: bool) -> bool:
    """
    True = the system answered when it should have refused.
    (False negative refusal → bot hallucinated or went off-scope)
    """
    return should_refuse and (not contains_refusal(answer))
