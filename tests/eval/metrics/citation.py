"""
Citation quality metrics (deterministic, regex-based).

Checks whether the answer includes properly-formatted citations
as required by the system prompt: [Document title](URL)
"""

import re
from typing import List

# Matches citations like [Ley 24241](https://example.com/ley24241)
CITATION_PATTERN = re.compile(r'\[[^\]\n]+\]\(https?://[^\s)]+\)')

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
