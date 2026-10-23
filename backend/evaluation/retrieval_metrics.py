"""Dependency-free retrieval ranking metrics."""


def evaluate_ranking(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> dict:
    if k < 1:
        raise ValueError("k must be positive")
    relevant = set(relevant_ids)
    top_k = list(dict.fromkeys(retrieved_ids))[:k]
    hits = sum(item in relevant for item in top_k)
    first_rank = next((rank for rank, item in enumerate(top_k, 1) if item in relevant), None)
    return {
        "precision_at_k": hits / k,
        "recall_at_k": hits / len(relevant) if relevant else 0.0,
        "reciprocal_rank_at_k": 1 / first_rank if first_rank else 0.0,
        "hit_at_k": int(hits > 0),
    }
