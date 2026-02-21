#!/usr/bin/env python3
"""
RAG Evaluation Runner — Phase 1
================================
Runs the 5 golden test cases against the live API and reports:

  - Hit Rate
  - Precision@k
  - NDCG@k
  - Citation Presence Rate
  - Keyword Coverage
  - Refusal Accuracy
  - Over-refusal / Under-refusal
  - Latency (ms)

Usage (from repo root, with backend running):
    python tests/eval/run_eval.py
    python tests/eval/run_eval.py --api-url http://localhost:8000/api/v1
    python tests/eval/run_eval.py --save-report
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

# ── path setup (allows running from project root without installing)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.eval.metrics.citation import (
    citation_count,
    citation_presence,
    keyword_coverage,
)
from tests.eval.metrics.refusal import (
    is_over_refusal,
    is_under_refusal,
    refusal_accuracy,
)
from tests.eval.metrics.retrieval import hit_rate, ndcg_at_k, precision_at_k

# ── constants
GOLDEN_DATASET = Path(__file__).parent / "golden_dataset.json"
REPORTS_DIR = Path(__file__).parent / "reports"
API_CHAT_ENDPOINT = "/chat"

# ── ANSI colours for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def call_api(base_url: str, question: str) -> Dict[str, Any]:
    """Call the backend chat API and return the parsed JSON response."""
    url = base_url.rstrip("/") + API_CHAT_ENDPOINT
    payload = {"query": question}
    start = time.time()
    response = requests.post(url, json=payload, timeout=120)
    elapsed_ms = (time.time() - start) * 1000

    if not response.ok:
        raise RuntimeError(
            f"API error {response.status_code}: {response.text[:200]}"
        )

    data = response.json()
    data["_elapsed_ms"] = elapsed_ms  # inject measured latency
    return data


def evaluate_case(case: Dict, api_response: Dict) -> Dict[str, Any]:
    """Compute all metrics for a single test case."""
    answer: str = api_response.get("answer", "")
    retrieved_ids: List[str] = [
        doc["id"] for doc in api_response.get("law_documents", [])
    ]
    expected_ids: List[str] = case.get("expected_doc_ids", [])
    expected_kws: List[str] = case.get("expected_citations", [])
    should_refuse: bool = case.get("should_refuse", False)
    latency_ms: float = api_response.get("response_time_ms", api_response.get("_elapsed_ms", 0))

    return {
        "id": case["id"],
        "question": case["question"],
        # ── Retrieval
        "hit_rate": hit_rate(retrieved_ids, expected_ids),
        "precision_at_k": precision_at_k(retrieved_ids, expected_ids),
        "ndcg_at_k": ndcg_at_k(retrieved_ids, expected_ids),
        # ── Citation
        "citation_present": citation_presence(answer),
        "citation_count": citation_count(answer),
        "keyword_coverage": keyword_coverage(answer, expected_kws),
        # ── Refusal
        "refusal_accurate": refusal_accuracy(answer, should_refuse),
        "over_refusal": is_over_refusal(answer, should_refuse),
        "under_refusal": is_under_refusal(answer, should_refuse),
        # ── Latency
        "latency_ms": round(latency_ms, 1),
        # ── Raw answer (for inspection)
        "answer": answer,
        "retrieved_ids": retrieved_ids,
        "expected_ids": expected_ids,
        "should_refuse": should_refuse,
    }


def print_results(results: List[Dict]) -> None:
    """Pretty-print the per-case results and aggregate summary."""
    print(f"\n{BOLD}{'='*72}{RESET}")
    print(f"{BOLD}  RAG EVALUATION REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}{RESET}")
    print(f"{BOLD}{'='*72}{RESET}\n")

    for r in results:
        ok = lambda v: f"{GREEN}✓{RESET}" if v else f"{RED}✗{RESET}"
        pct = lambda v: f"{v*100:.0f}%"

        print(f"{CYAN}{BOLD}[{r['id']}]{RESET} {r['question']}")
        print(f"  Retrieved docs : {r['retrieved_ids']}")
        print(f"  Expected docs  : {r['expected_ids']}")
        print(f"  Hit Rate       : {ok(r['hit_rate'])}  {pct(r['hit_rate'])}")
        print(f"  Precision@k    : {pct(r['precision_at_k'])}")
        print(f"  NDCG@k         : {pct(r['ndcg_at_k'])}")
        print(f"  Citation present: {ok(r['citation_present'])}")
        print(f"  Keyword coverage: {pct(r['keyword_coverage'])}")
        print(f"  Refusal correct : {ok(r['refusal_accurate'])}  "
              f"{'(over-refusal!)' if r['over_refusal'] else ''}"
              f"{'(HALLUCINATION!)' if r['under_refusal'] else ''}")
        print(f"  Latency        : {YELLOW}{r['latency_ms']} ms{RESET}")
        print()

    # ── aggregate
    n = len(results)
    avg = lambda key: sum(r[key] for r in results) / n
    count = lambda key: sum(1 for r in results if r[key])

    print(f"{BOLD}{'─'*72}{RESET}")
    print(f"{BOLD}  AGGREGATE  (n={n}){RESET}")
    print(f"{'─'*72}")
    print(f"  Hit Rate (avg)          : {avg('hit_rate')*100:.1f}%")
    print(f"  Precision@k (avg)       : {avg('precision_at_k')*100:.1f}%")
    print(f"  NDCG@k (avg)            : {avg('ndcg_at_k')*100:.1f}%")
    print(f"  Citation Presence Rate  : {count('citation_present')}/{n} = {count('citation_present')/n*100:.0f}%")
    print(f"  Keyword Coverage (avg)  : {avg('keyword_coverage')*100:.1f}%")
    print(f"  Refusal Accuracy        : {count('refusal_accurate')}/{n} = {count('refusal_accurate')/n*100:.0f}%")
    print(f"  Over-refusal count      : {count('over_refusal')}")
    print(f"  Under-refusal count     : {count('under_refusal')}")
    print(f"  Avg Latency             : {avg('latency_ms'):.0f} ms")
    print(f"{'='*72}\n")


def save_report(results: List[Dict]) -> Path:
    """Save a JSON report to tests/eval/reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = REPORTS_DIR / f"{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": ts,
                "n_cases": len(results),
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG evaluation runner")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="Base URL of the backend API (default: http://localhost:8000/api/v1)",
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save JSON report to tests/eval/reports/",
    )
    parser.add_argument(
        "--case",
        help="Run a single case by ID (e.g. q1_trabajo_informal)",
    )
    args = parser.parse_args()

    # load dataset
    with open(GOLDEN_DATASET, encoding="utf-8") as f:
        dataset = json.load(f)

    if args.case:
        dataset = [c for c in dataset if c["id"] == args.case]
        if not dataset:
            print(f"Case '{args.case}' not found in golden dataset.")
            sys.exit(1)

    print(f"Running {len(dataset)} test case(s) against {args.api_url}...\n")

    results = []
    for case in dataset:
        print(f"  → {case['id']}: {case['question'][:60]}...")
        try:
            api_response = call_api(args.api_url, case["question"])
            result = evaluate_case(case, api_response)
        except Exception as e:
            print(f"     {RED}ERROR: {e}{RESET}")
            result = {
                "id": case["id"],
                "question": case["question"],
                "error": str(e),
                "hit_rate": 0,
                "precision_at_k": 0,
                "ndcg_at_k": 0,
                "citation_present": False,
                "citation_count": 0,
                "keyword_coverage": 0,
                "refusal_accurate": False,
                "over_refusal": False,
                "under_refusal": False,
                "latency_ms": 0,
                "answer": "",
                "retrieved_ids": [],
                "expected_ids": case.get("expected_doc_ids", []),
                "should_refuse": case.get("should_refuse", False),
            }
        results.append(result)

    print_results(results)

    if args.save_report:
        path = save_report(results)
        print(f"Report saved → {path}\n")


if __name__ == "__main__":
    main()
