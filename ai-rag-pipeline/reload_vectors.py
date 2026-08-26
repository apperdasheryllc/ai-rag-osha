# reload_vectors.py
import os, json
import chromadb
from chromadb.utils import embedding_functions

CHUNK_DIR  = "chunks"
STORE_PATH = "./chroma_store"
COLLECTION = "osha_regulations"

# Delete and recreate the collection for a clean reload
client   = chromadb.PersistentClient(path=STORE_PATH)
try:
    client.delete_collection(COLLECTION)
    print("Deleted old collection.")
except:
    pass

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.create_collection(
    name=COLLECTION,
    embedding_function=embed_fn
)

all_ids, all_docs, all_metas = [], [], []

for fname in sorted(os.listdir(CHUNK_DIR)):
    if not fname.endswith(".jsonl"):
        continue
    with open(os.path.join(CHUNK_DIR, fname)) as f:
        for line in f:
            rec = json.loads(line)
            all_ids.append(rec["chunk_id"])
            all_docs.append(rec["text"])
            all_metas.append({
                "label":       rec["label"],
                "citation":    rec.get("citation", ""),
                "source_url":  rec["source_url"],
                "chunk_index": rec["chunk_index"],
                "token_count": rec["token_count"],
            })

BATCH = 100
for i in range(0, len(all_ids), BATCH):
    collection.upsert(
        ids       = all_ids[i:i+BATCH],
        documents = all_docs[i:i+BATCH],
        metadatas = all_metas[i:i+BATCH],
    )
    print(f"  Loaded {min(i+BATCH, len(all_ids))}/{len(all_ids)} chunks...")

print(f"\n✅ Reloaded — {len(all_ids)} section-level chunks indexed.")