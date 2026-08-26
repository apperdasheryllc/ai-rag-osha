# ai-rag-android

Native Android client for the OSHA PPE RAG experience, built with Kotlin and Jetpack Compose.

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
