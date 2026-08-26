# ai-rag-app (iOS)

Native iOS client for the OSHA PPE RAG experience, built with Swift and SwiftUI.

## Scope

- Presents OSHA PPE question-and-answer workflows to users.
- Calls the backend API in `ai-rag-api` for retrieval and response generation.

## Project Layout

- `ai-rag-app/ai-rag-app.xcodeproj` - Xcode project.
- `ai-rag-app/ai-rag-app/` - App source code.

## Run locally

1. Open `ai-rag-app/ai-rag-app.xcodeproj` in Xcode.
2. Select an iOS Simulator target.
3. Build and run the app.

## Backend dependency

This app is expected to integrate with the FastAPI backend in `ai-rag-api`.
Set the API base URL in app configuration before testing network flows.
