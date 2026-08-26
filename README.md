# AI RAG OSHA Demo - Apperdashery

This repository showcases IT skills and modern technologies used in enterprise software development:
- **AI Engineering**: Anthropic, Retrieval Augmented Generation (RAG), ChromaDB, LiteLLM, Vector Databases
- **Backend API**: Python, FastAPI
- **Native Mobile Development**: iOS, Android

## ai-rag-pipeline
A retrieval and indexing pipeline for OSHA safety regulations.
It scrapes source pages, cleans and sections raw HTML, generates chunked JSONL records, embeds them with Sentence Transformers, and loads vectors into ChromaDB for downstream semantic retrieval.
Pipeline docs: [ai-rag-pipeline/README.md](ai-rag-pipeline/README.md)

## ai-rag-api
A FastAPI service that exposes health and OSHA PPE RAG endpoints.
It queries ChromaDB for relevant regulation chunks, uses Anthropic Claude (via LiteLLM) to produce grounded responses, and includes OpenAPI/Swagger docs for local testing.
API docs: [ai-rag-api/README.md](ai-rag-api/README.md)

## ai-rag-app
A native iOS app built with Swift and SwiftUI.
This client is intended to provide a mobile interface for OSHA PPE question/answer flows backed by the ai-rag-api service.
iOS docs: [ai-rag-app/README.md](ai-rag-app/README.md)

## ai-rag-android
A native Android app built with Kotlin and Jetpack Compose.
This client is intended to mirror the iOS experience and connect to the same FastAPI RAG backend for OSHA PPE guidance.
Android docs: [ai-rag-android/README.md](ai-rag-android/README.md)
