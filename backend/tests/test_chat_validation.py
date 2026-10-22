
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_requires_document_id():
    response = client.post(
        "/chat",
        json={
            "question": "Summarize the document."
        },
    )

    assert response.status_code == 422


def test_chat_with_document_id():
    document_id = (
        "123e4567-e89b-12d3-a456-426614174000"
    )

    with patch(
        "app.api.chat.rag_service.answer_question"
    ) as mock_answer:

        mock_answer.return_value = {
            "answer": "Test answer",
            "sources": [],
            "session_id": None,
        }

        response = client.post(
            "/chat",
            json={
                "question": "Summarize the document.",
                "document_id": document_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer"

    assert (
        mock_answer.call_args.kwargs["document_id"]
        == document_id
    )
