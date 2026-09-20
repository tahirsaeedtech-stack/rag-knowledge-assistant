from app.services.retrieval_service import (
    retrieval_service,
)


TEST_CASES = [
    {
        "question": (
            "How many years of front-end "
            "experience does Tahir have?"
        ),
        "expected_keywords": [
            "10+ years",
            "front-end",
        ],
    },
    {
        "question": (
            "Which company did Tahir work "
            "for from 2015 to 2018?"
        ),
        "expected_keywords": [
            "SSA SOFT SOLUTIONS",
        ],
    },
    {
        "question": (
            "What technologies did Tahir "
            "use as a front-end developer?"
        ),
        "expected_keywords": [
            "React",
            "JavaScript",
            "HTML",
            "CSS",
        ],
    },
]


def evaluate_retrieval():

    passed = 0

    print("\nRAG Retrieval Evaluation")
    print("=" * 50)

    for test in TEST_CASES:

        results = retrieval_service.search(
            query=test["question"],
            limit=5,
            min_score=0.0,
        )

        retrieved_text = " ".join(
            result["text"]
            for result in results
        ).lower()

        keyword_found = any(
            keyword.lower() in retrieved_text
            for keyword in test[
                "expected_keywords"
            ]
        )

        if keyword_found:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"

        print(
            f"\n{status}: "
            f"{test['question']}"
        )

        if results:
            print(
                "Top score:",
                results[0]["score"],
            )

    total = len(TEST_CASES)

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    print("\n" + "=" * 50)

    print(
        f"Retrieval Hit Rate: "
        f"{passed}/{total} "
        f"({accuracy:.1f}%)"
    )


if __name__ == "__main__":
    evaluate_retrieval()
