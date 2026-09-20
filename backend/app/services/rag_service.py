from openai import OpenAI

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)
from app.services.retrieval_service import retrieval_service


class RAGService:

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        self.sessions = {}

    def answer_question(
        self,
        question: str,
        limit: int = 3,
        min_score: float = 0.35,
        document_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        retrieved_chunks = retrieval_service.search(
            query=question,
            limit=limit,
            min_score=min_score,
            document_id=document_id,
        )

        if not retrieved_chunks:
            return {
                "answer": (
                    "I could not find sufficiently relevant "
                    "information in the indexed documents."
                ),
                "sources": [],
                "session_id": session_id,
            }

        context_parts = []

        for index, result in enumerate(
            retrieved_chunks,
            start=1,
        ):
            context_parts.append(
                f"""
SOURCE {index}

Filename: {result.get("filename")}
Page: {result.get("page_number")}
Chunk: {result.get("chunk_id")}

Content:
{result.get("text")}
"""
            )

        context = "\n".join(context_parts)

        history = []

        if session_id:
            history = self.sessions.get(
                session_id,
                [],
            )

        system_prompt = """
You are a retrieval-augmented knowledge assistant.

Use ONLY the supplied document context.

Rules:
1. Do not invent facts.
2. Do not use outside knowledge.
3. If the context is insufficient, say so clearly.
4. Keep answers concise and useful.
5. Cite evidence using [Source 1], [Source 2], etc.
6. Only cite sources that genuinely support the answer.
7. Conversation history may help understand follow-up questions,
   but factual answers must still be supported by retrieved context.
"""

        user_prompt = f"""
QUESTION:
{question}

DOCUMENT CONTEXT:
{context}
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        response = (
            self.client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages,
                temperature=0.1,
            )
        )

        answer = (
            response.choices[0]
            .message.content
        )

        if not answer:
            answer = "No answer was generated."

        if session_id:
            self.sessions.setdefault(
                session_id,
                []
            )

            self.sessions[session_id].append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            self.sessions[session_id].append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            self.sessions[session_id] = (
                self.sessions[session_id][-10:]
            )

        sources = []

        for index, result in enumerate(
            retrieved_chunks,
            start=1,
        ):
            sources.append(
                {
                    "source_id": index,
                    "filename": result.get(
                        "filename"
                    ),
                    "page_number": result.get(
                        "page_number"
                    ),
                    "chunk_id": result.get(
                        "chunk_id"
                    ),
                    "score": result.get(
                        "score"
                    ),
                    "snippet": result.get(
                        "snippet",
                        result.get(
                            "text",
                            ""
                        )[:300]
                    ),
                }
            )

        return {
            "answer": answer.strip(),
            "sources": sources,
            "session_id": session_id,
        }


rag_service = RAGService()
