from fastapi import FastAPI

app = FastAPI(title="AI RAG API")


@app.get("/v1/health")
def hello_world() -> dict[str, str]:
    return {"message": "API is up and running."}
