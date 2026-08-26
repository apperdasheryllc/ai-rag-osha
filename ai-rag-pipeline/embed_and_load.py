# embed_and_load.py
import os, json
import chromadb
from chromadb.utils import embedding_functions

CHUNK_DIR   = "chunks"
COLLECTION  = "osha_regulations"

client = chromadb.PersistentClient(path="./chroma_store")
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"   # Fast, good quality, runs locally
)

collection = client.get_or_create_collection(
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
                "label":      rec["label"],
                "source_url": rec["source_url"],
                "chunk_index": rec["chunk_index"],
            })

# Upsert in batches of 100
BATCH = 100
for i in range(0, len(all_ids), BATCH):
    collection.upsert(
        ids       = all_ids[i:i+BATCH],
        documents = all_docs[i:i+BATCH],
        metadatas = all_metas[i:i+BATCH],
    )
    print(f"  Loaded {min(i+BATCH, len(all_ids))}/{len(all_ids)} chunks...")

print(f"\n✅ Vector store ready — {len(all_ids)} chunks indexed in ./chroma_store")