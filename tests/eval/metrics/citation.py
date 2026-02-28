"""
Citation quality metrics (deterministic, regex-based).

Checks whether the answer includes properly-formatted citations
as required by the system prompt: [DOC_ID:Lx-Ly]
"""

import re
from typing import List

# Matches citations like [ley_24714:L10-L25] or [ley_1602-2009:L7]
CITATION_PATTERN = re.compile(r'\[[\w_\-]+:L\d+(?:-L\d+)?\]')

# Refusal phrases defined in the system prompt
REFUSAL_PHRASES = [
    "no surge de los documentos provistos",
    "solo puedo responder consultas de seguridad social",
]


def citation_presence(answer: str) -> bool:
    """True if the answer contains at least one properly-formatted citation."""
    return bool(CITATION_PATTERN.search(answer))


def citation_count(answer: str) -> int:
    """Number of formatted citations found in the answer."""
    return len(CITATION_PATTERN.findall(answer))


def keyword_coverage(answer: str, expected_keywords: List[str]) -> float:
    """
    Fraction of expected citation keywords that appear in the answer.
    Case-insensitive substring match.
    """
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return found / len(expected_keywords)


def contains_refusal(answer: str) -> bool:
    """True if the answer contains a standard refusal phrase."""
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)
