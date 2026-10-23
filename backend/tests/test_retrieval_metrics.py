from evaluation.retrieval_metrics import evaluate_ranking


def test_relevant_chunk_first():
    metrics = evaluate_ranking(["a", "b", "c"], ["a"], 3)
    assert metrics["precision_at_k"] == 1 / 3
    assert metrics["recall_at_k"] == 1
    assert metrics["reciprocal_rank_at_k"] == 1
    assert metrics["hit_at_k"] == 1


def test_relevant_chunk_second():
    metrics = evaluate_ranking(["a", "b", "c"], ["b"], 3)
    assert metrics["reciprocal_rank_at_k"] == 0.5


def test_no_match():
    metrics = evaluate_ranking(["a", "b"], ["c"], 3)
    assert metrics["recall_at_k"] == 0
    assert metrics["reciprocal_rank_at_k"] == 0


def test_multiple_relevant_chunks():
    metrics = evaluate_ranking(["a", "b", "c"], ["b", "c", "d"], 3)
    assert metrics["recall_at_k"] == 2 / 3
