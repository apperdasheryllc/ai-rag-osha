"""Protected OSHA PPE RAG endpoint backed by Chroma and Anthropic Claude."""

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException

from ..models.schemas import OshaSource, OshaStandardQuery, OshaStandardResponse
from ..rag.chroma_client import get_osha_collection
from ..rag.query_utils import expand_query

router = APIRouter(prefix="/v1", tags=["osha/ppe"])
logger = logging.getLogger(__name__)

ANTHROPIC_OSHA_RAG_MODEL = os.getenv(
    "ANTHROPIC_OSHA_RAG_MODEL",
    "anthropic/claude-haiku-4-5-20251001",
)


def _require_anthropic_api_key() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
    return api_key


def _normalize_text(document: Any, metadata: dict[str, Any]) -> str:
    if isinstance(document, str) and document.strip():
        return document.strip()
    return str(metadata.get("text", "")).strip()


def _query_osha_sources(query: str, results: int) -> list[OshaSource]:
    query_variants = expand_query(query)
    collection = get_osha_collection()

    sources: list[OshaSource] = []
    seen: set[str] = set()

    for query_variant in query_variants:
        response = collection.query(
            query_texts=[query_variant],
            n_results=results,
            include=["documents", "metadatas"],
        )

        ids_list = response.get("ids") or [[]]
        documents_list = response.get("documents") or [[]]
        metadatas_list = response.get("metadatas") or [[]]

        ids = ids_list[0] if ids_list else []
        documents = documents_list[0] if documents_list else []
        metadatas = metadatas_list[0] if metadatas_list else []

        max_items = max(len(ids), len(documents), len(metadatas))
        for index in range(max_items):
            metadata = metadatas[index] if index < len(metadatas) and isinstance(metadatas[index], dict) else {}
            document = documents[index] if index < len(documents) else ""
            source = OshaSource(
                citation=str(metadata.get("citation", "")).strip(),
                label=str(metadata.get("label", "")).strip(),
                source_url=str(metadata.get("source_url", "")).strip(),
                text=_normalize_text(document, metadata),
            )

            dedupe_key = str(metadata.get("chunk_id", "")).strip() or f"{source.citation}|{source.text}"
            if not source.text or dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            sources.append(source)

            if len(sources) >= results:
                return sources

    return sources


def _build_rag_prompt(query: str, query_variants: list[str], sources: list[OshaSource]) -> str:
    source_blocks = [
        (
            f"[SOURCE {index}]\n"
            f"citation: {source.citation or 'unknown'}\n"
            f"label: {source.label or 'unknown'}\n"
            f"source_url: {source.source_url or 'unknown'}\n"
            f"text: {source.text}"
        )
        for index, source in enumerate(sources, start=1)
    ]
    sources_text = "\n\n".join(source_blocks)

    variants_text = "\n".join(f"- {variant}" for variant in query_variants)
    return (
        "You are an OSHA PPE compliance assistant. Answer using only the provided regulatory chunks.\n"
        "If the evidence is not sufficient, state that directly.\n"
        "Cite relevant citations inline like (1926.104(e)).\n\n"
        f"User query:\n{query}\n\n"
        f"Query expansions used for retrieval:\n{variants_text}\n\n"
        f"Retrieved sources:\n{sources_text}\n"
    )


def _run_claude_rag(prompt: str) -> str:
    try:
        import litellm
    except ImportError as error:
        raise RuntimeError("litellm is not installed") from error

    try:
        response = litellm.completion(
            model=ANTHROPIC_OSHA_RAG_MODEL,
            api_key=_require_anthropic_api_key(),
            messages=[
                {"role": "system", "content": "Return a concise OSHA PPE compliance answer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except Exception as error:
        raise RuntimeError(
            "Claude completion failed. Verify ANTHROPIC_API_KEY and "
            f"ANTHROPIC_OSHA_RAG_MODEL='{ANTHROPIC_OSHA_RAG_MODEL}'. Original error: {error}"
        ) from error

    choices = getattr(response, "choices", None)
    if not choices:
        raise RuntimeError("Claude returned no completion choices")

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "") if message is not None else ""
    if isinstance(content, list):
        text = "\n".join(
            str(item.get("text", "")).strip()
            for item in content
            if isinstance(item, dict) and str(item.get("text", "")).strip()
        )
    else:
        text = str(content).strip()

    if not text:
        raise RuntimeError("Claude returned an empty response")
    return text


def generate_osha_ppe_rag_response(query: str, results: int) -> OshaStandardResponse:
    query_variants = expand_query(query)
    sources = _query_osha_sources(query=query, results=results)
    if not sources:
        raise RuntimeError("No OSHA chunks were found for the requested query")

    prompt = _build_rag_prompt(query=query, query_variants=query_variants, sources=sources)
    answer = _run_claude_rag(prompt)
    return OshaStandardResponse(answer=answer, sources=sources)


@router.post(
    "/osha/ppe",
    response_model=OshaStandardResponse,
    summary="Answer an OSHA PPE question",
    description=(
        "Runs retrieval over indexed OSHA PPE chunks in ChromaDB, then generates a grounded "
        "answer using the configured Anthropic model via LiteLLM."
    ),
    responses={
        500: {
            "description": "RAG processing error (configuration, retrieval, or model invocation failure)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Claude completion failed. Verify ANTHROPIC_API_KEY and model configuration."
                    }
                }
            },
        }
    },
)
async def osha_ppe_rag(
    payload: OshaStandardQuery,
) -> OshaStandardResponse:
    try:
        return generate_osha_ppe_rag_response(payload.query, payload.results)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        logger.exception("Unhandled OSHA PPE RAG error")
        raise HTTPException(status_code=500, detail=f"OSHA PPE RAG request failed: {error}") from error
