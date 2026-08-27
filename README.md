# AI RAG OSHA Demo - Apperdashery
*Artificial Intelligence · Retrieval-Augmented Generation · Occupational Safety and Health Administration*

## What it demonstrates
- AI engineering
- Retrieval-Augmented Generation (RAG)
- Document ingestion
- Vector search
- LLM integration
- Mobile AI integration
- FastAPI web service

## Business Use Cases

This architecture can be adapted for field service, construction, healthcare, financial services, insurance, manufacturing, and other environments where employees need rapid access to organizational knowledge.



https://github.com/user-attachments/assets/c4442a6a-e43d-419c-8f8a-f58dddf0c2e0



## Architecture

How a user's question flows through the system, end to end:

```mermaid
flowchart TD
    iOS["📱 iOS App<br/>(Swift/SwiftUI)"]
    AND["📱 Android App<br/>(Kotlin/Compose)"]
    API["🖥️ ai-rag-api<br/>(FastAPI)"]
    VDB[("🗄️ ChromaDB<br/>Vector Store")]
    LLM["🤖 Claude<br/>(via LiteLLM)"]

    iOS <-->|"1 ask →<br/>6 ← answer"| API
    AND <-->|"1 ask →<br/>6 ← answer"| API
    API <-->|"2 search →<br/>3 ← chunks"| VDB
    API <-->|"4 question + context →<br/>5 ← grounded answer"| LLM

    subgraph Pipeline["⚙️ ai-rag-pipeline — offline indexing"]
        direction LR
        SRC["OSHA Regulation Pages"] --> CHUNK["Scrape, Clean & Chunk"] --> EMBED["Embed<br/>(Sentence Transformers)"]
    end
    EMBED -.->|pre-indexes| VDB
```

1. The user asks a question in the iOS or Android app, which is sent to **ai-rag-api**.
2. **ai-rag-api** embeds the question and searches **ChromaDB** for the most relevant OSHA regulation chunks (indexed ahead of time by **ai-rag-pipeline**). Retrieval happens entirely in the API — Claude never queries the vector store directly.
3. The API builds a prompt from the question plus the retrieved chunks and sends it to **Claude** (via LiteLLM).
4. Claude returns a grounded, cited answer as plain text, which the API relays back to the mobile app.

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

<img width="350" alt="Simulator Screenshot - iPhone 17 - 2026-08-26 at 16 07 44" src="https://github.com/user-attachments/assets/0080e54a-1e7f-4683-8291-6680396cb297" />


## ai-rag-android
A native Android app built with Kotlin and Jetpack Compose.
This client is intended to mirror the iOS experience and connect to the same FastAPI RAG backend for OSHA PPE guidance.
Android docs: [ai-rag-android/README.md](ai-rag-android/README.md)

<img width="350" alt="Screenshot_20260826_183900" src="https://github.com/user-attachments/assets/73507f57-c400-4b74-82f7-7b2636e80ac2" />

