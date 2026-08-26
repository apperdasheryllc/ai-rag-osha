# ai-rag-android

Native Android client for the OSHA PPE RAG experience, built with Kotlin and Jetpack Compose.

| Ask | Answer | Source |
| -------- | -------- | -------- |
| <img width="1080" height="2424" alt="Screenshot_20260826_183245" src="https://github.com/user-attachments/assets/07d97af7-66b1-4e67-ac36-06ac4308bc02" />  | <img width="1080" height="2424" alt="Screenshot_20260826_183301" src="https://github.com/user-attachments/assets/6fc0fd57-c891-4e02-bac1-ccfcb8103de2" />  | <img width="1080" height="2424" alt="Screenshot_20260826_192010" src="https://github.com/user-attachments/assets/4827d045-111a-4928-be47-d04158817ba7" />  |

## Scope

- Presents OSHA PPE question-and-answer workflows to users.
- Calls the backend API in `ai-rag-api` for retrieval and response generation.

## Project Layout

- `app/` - Android application module.
- `build.gradle.kts` and `settings.gradle.kts` - Gradle configuration.
- `gradlew` / `gradlew.bat` - Gradle wrapper scripts.

## Run locally

```bash
./gradlew assembleDebug
./gradlew installDebug
```

Open the project in Android Studio for emulator/device run and debugging.

## Backend dependency

This app is expected to integrate with the FastAPI backend in `ai-rag-api`.
Set the API base URL in app configuration before testing network flows.
