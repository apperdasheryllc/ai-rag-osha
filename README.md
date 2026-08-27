# AI RAG OSHA Demo - Apperdashery

This repository showcases AI engineering skills and modern technologies used in enterprise software development:
- **AI Engineering**: Anthropic, Retrieval Augmented Generation (RAG), ChromaDB, LiteLLM, Vector Databases
- **Backend API**: Python, FastAPI
- **Native Mobile Development**: iOS, Android

## ai-rag-pipeline
A retrieval and indexing pipeline for OSHA safety regulations.
It scrapes source pages, cleans and sections raw HTML, generates chunked JSONL records, embeds them with Sentence Transformers, and loads vectors into ChromaDB for downstream semantic retrieval.
Pipeline docs: [ai-rag-pipeline/README.md](ai-rag-pipeline/README.md)

<img width="970" height="534" alt="Screenshot 2026-08-27 at 10 02 06 AM" src="https://github.com/user-attachments/assets/6084bc8b-4a11-4c08-bb09-6fa055770224" />


## ai-rag-api
A FastAPI service that exposes health and OSHA PPE RAG endpoints.
It queries ChromaDB for relevant regulation chunks, uses Anthropic Claude (via LiteLLM) to produce grounded responses, and includes OpenAPI/Swagger docs for local testing.
API docs: [ai-rag-api/README.md](ai-rag-api/README.md)

<img width="1171" height="614" alt="Screenshot 2026-08-27 at 10 05 13 AM" src="https://github.com/user-attachments/assets/8e3e7d18-4b9f-4195-92fa-613d5d74aa7c" />


## ai-rag-app
A native iOS app built with Swift and SwiftUI.
This client is intended to provide a mobile interface for OSHA PPE question/answer flows backed by the ai-rag-api service.
iOS docs: [ai-rag-app/README.md](ai-rag-app/README.md)

<img width="1206" height="2622" alt="Simulator Screenshot - iPhone 17 - 2026-08-26 at 16 07 44" src="https://github.com/user-attachments/assets/0080e54a-1e7f-4683-8291-6680396cb297" />


## ai-rag-android
A native Android app built with Kotlin and Jetpack Compose.
This client is intended to mirror the iOS experience and connect to the same FastAPI RAG backend for OSHA PPE guidance.
Android docs: [ai-rag-android/README.md](ai-rag-android/README.md)

<img width="1080" height="2424" alt="Screenshot_20260826_183900" src="https://github.com/user-attachments/assets/73507f57-c400-4b74-82f7-7b2636e80ac2" />

