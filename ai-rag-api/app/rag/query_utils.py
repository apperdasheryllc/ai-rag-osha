"""Query expansion helpers for regulatory RAG searches."""

from collections.abc import Iterable

EXPANSIONS = {
    "how long":     ["maximum length", "minimum length", "length requirement"],
    "how high":     ["minimum height", "maximum height", "height requirement"],
    "how heavy":    ["maximum load", "weight limit", "load capacity"],
    "how much":     ["minimum breaking strength", "force requirement", "capacity"],
    "how often":    ["inspection frequency", "shall be inspected", "periodic inspection"],
    "do i need":    ["shall be provided", "is required", "must be equipped"],
    "what ppe":     ["personal protective equipment", "shall wear", "eye protection",
                     "respiratory protection"],
    "when is":      ["required when", "shall be used when", "conditions requiring"],
    "who must":     ["employer shall", "competent person", "qualified person"],
    "what is the":  ["requirement", "shall be", "must not exceed", "minimum of"],
}

def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []

    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    return deduped


def expand_query(query: str) -> list[str]:
    """Expand conversational language into regulatory vocabulary variants."""
    normalized_query = query.strip()
    lowered_query = normalized_query.lower()

    expansions: list[str] = [normalized_query]
    for trigger, terms in EXPANSIONS.items():
        if trigger in lowered_query:
            expansions.extend(terms)

    return _dedupe_preserve_order(expansions)
