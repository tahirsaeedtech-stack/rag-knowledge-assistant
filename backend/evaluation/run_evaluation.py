"""Evaluate indexed-document retrieval with human-labeled relevant chunk IDs.

Run from backend directory:
    python -m evaluation.run_evaluation --dataset evaluation/datasets/questions.json --k 3
"""
import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from evaluation.retrieval_metrics import evaluate_ranking


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=Path("evaluation/reports/latest.json"))
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be >= 1")
    if not 0 <= args.min_score <= 1:
        parser.error("--min-score must be between 0 and 1")

    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        parser.error("Dataset must be a nonempty JSON array")
    for i, case in enumerate(cases, 1):
        if not isinstance(case, dict) or not all(case.get(key) for key in ("question", "document_id", "relevant_chunk_ids")):
            parser.error(f"Case {i} needs question, document_id and nonempty relevant_chunk_ids")
        if not isinstance(case["relevant_chunk_ids"], list) or not all(isinstance(v, (str, int)) for v in case["relevant_chunk_ids"]):
            parser.error(f"Case {i} has invalid relevant_chunk_ids")

    # Import only after validating dataset: avoids unnecessary Qdrant connection on malformed input.
    from app.services.retrieval_service import retrieval_service

    rows = []
    for i, case in enumerate(cases, 1):
        start = time.perf_counter()
        matches = retrieval_service.search(
            query=case["question"],
            document_id=case["document_id"],
            limit=args.k,
            min_score=args.min_score,
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        retrieved_ids = [str(match["chunk_id"]) for match in matches if match.get("chunk_id") is not None]
        metrics = evaluate_ranking(retrieved_ids, [str(v) for v in case["relevant_chunk_ids"]], args.k)
        rows.append({
            "question": case["question"],
            "document_id": case["document_id"],
            "relevant_chunk_ids": case["relevant_chunk_ids"],
            "retrieved_chunk_ids": retrieved_ids,
            "latency_ms": latency_ms,
            **metrics,
        })
        print(f"[{i}/{len(cases)}] recall@{args.k}={metrics['recall_at_k']:.3f}, MRR@{args.k}={metrics['reciprocal_rank_at_k']:.3f}, {latency_ms:.0f}ms")

    keys = ("precision_at_k", "recall_at_k", "reciprocal_rank_at_k", "hit_at_k", "latency_ms")
    summary = {key: round(statistics.mean(row[key] for row in rows), 4) for key in keys}
    summary["question_count"] = len(rows)
    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "k": args.k, "min_score": args.min_score, "summary": summary, "cases": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY", json.dumps(summary, indent=2))
    print(f"Report saved: {args.output}")


if __name__ == "__main__":
    main()
