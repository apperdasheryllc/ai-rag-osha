# test_rag.py  (v2 — with query expansion)
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_store")
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_collection("osha_regulations", embedding_function=embed_fn)

def expand_query(query: str) -> list[str]:
    """
    Return the original query plus regulatory paraphrases.
    In production this would call Claude to generate paraphrases.
    For the demo, use a small hardcoded map for known question types.
    """
    expansions = {
        "how long":      ["maximum length", "minimum length", "length requirement"],
        "how high":      ["minimum height", "maximum height", "height requirement"],
        "how much":      ["minimum load", "minimum force", "breaking strength", "capacity"],
        "what is":       ["requirement", "shall be", "must be"],
        "do i need":     ["shall", "must", "required", "requirement"],
        "when should":   ["shall", "required when", "required if"],
    }
    extra = [query]
    for trigger, phrases in expansions.items():
        if trigger in query.lower():
            for phrase in phrases:
                extra.append(f"{query} {phrase}")
    return extra

def search(query: str, n_results: int = 5):
    queries = expand_query(query)

    # Query with each expansion and deduplicate by chunk_id
    seen_ids = set()
    results  = []

    for q in queries:
        res = collection.query(query_texts=[q], n_results=n_results)
        for doc, meta, dist, cid in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
            res["ids"][0],
        ):
            if cid not in seen_ids:
                seen_ids.add(cid)
                results.append((dist, doc, meta))

    # Sort by distance (lower = more similar) and return top n
    results.sort(key=lambda x: x[0])
    return results[:n_results]

if __name__ == "__main__":
    query = "How long does a safety belt lanyard need to be?"
    print(f"Query: {query}\n{'='*60}\n")

    for dist, doc, meta in search(query):
        print(f"Citation:  {meta.get('citation', 'N/A')}")
        print(f"Regulation: {meta['label']}")
        print(f"Source:    {meta['source_url']}")
        print(f"Distance:  {dist:.4f}")
        print(f"\n{doc}\n")
        print("-"*60)