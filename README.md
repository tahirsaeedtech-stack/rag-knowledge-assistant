# RAG Knowledge Assistant

A full-stack Retrieval-Augmented Generation (RAG) application for querying information contained in PDF documents.

## Overview

The application processes uploaded PDFs, converts extracted text into vector embeddings, retrieves relevant passages through semantic search, and generates answers using an LLM.

## Technology Stack

- Backend: Python, FastAPI
- PDF extraction: PyMuPDF
- Embeddings: SentenceTransformers (`all-MiniLM-L6-v2`)
- Vector database: Qdrant
- LLM integration: OpenRouter
- Frontend: React, Vite
- Infrastructure: Docker Compose
- Testing: pytest, GitHub Actions

## RAG Architecture

1. PDF upload and validation
2. Page-level text extraction
3. Text cleaning and overlapping chunk generation
4. Embedding generation
5. Qdrant vector indexing
6. Semantic retrieval with optional document filtering
7. Context-grounded answer generation
8. Display of retrieved source passages

## Core Features

- PDF document ingestion
- Duplicate document detection using SHA-256
- Semantic search
- Document-grounded question answering
- Source metadata including page references
- Conversation sessions
- Docker-based local infrastructure

## Local Development

The backend requires Python, its dependencies, a running Qdrant instance, and configured environment variables.

The frontend requires Node.js and npm.

Environment variables include:

- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `EMBEDDING_DIMENSION`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `VITE_API_URL` (frontend)

Never commit API keys or production credentials.

## Testing

Run backend tests:

```bash
cd backend
python -m pytest -v
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Current Limitations

- Authentication and per-user document ownership are not yet implemented.
- The application currently supports text-based PDFs.
- Retrieval relevance and answer faithfulness require systematic benchmarking.
- Production-grade monitoring and ingestion job management are future improvements.

## Planned Engineering Improvements

- Retrieval evaluation dataset and benchmark suite
- Improved document isolation
- Citation verification
- Prompt-injection resistance
- Observability and latency measurements
- More comprehensive CI/CD checks

## Engineering Focus

This project demonstrates end-to-end integration of document processing, vector retrieval, LLM generation, API development, frontend development, and automated testing.
