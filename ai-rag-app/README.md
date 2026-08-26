# ai-rag-app (iOS)

Native iOS client for the OSHA PPE RAG experience, built with Swift and SwiftUI.

| Ask | Answer | Source |
| -------- | -------- | -------- |
| <img width="1206" height="2622" alt="Simulator Screenshot - iPhone 17 - 2026-08-26 at 16 06 35" src="https://github.com/user-attachments/assets/9f6c4df2-9d32-4572-932f-7429b8425b58" /> | <img width="1206" height="2622" alt="Simulator Screenshot - iPhone 17 - 2026-08-26 at 16 07 44" src="https://github.com/user-attachments/assets/8bc72686-69df-4a67-abea-8dc2ed940707" /> | <img width="1206" height="2622" alt="Simulator Screenshot - iPhone 17 - 2026-08-26 at 16 08 30" src="https://github.com/user-attachments/assets/cb5272bd-ff71-4505-ac67-b0caf91dda51" /> |

https://github.com/user-attachments/assets/5da762e2-322c-45bd-9d67-e68b9e27c1b9

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
