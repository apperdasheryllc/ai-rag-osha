# diagnose.py
# Run this to see exactly what a JSONL chunk file contains around a target section.
import os, json

CHUNK_DIR   = "chunks"
TARGET_CITE = "1926.104"  # Change to whatever section you're testing

for fname in sorted(os.listdir(CHUNK_DIR)):
    if not fname.endswith(".jsonl"):
        continue
    with open(os.path.join(CHUNK_DIR, fname)) as f:
        for rec in map(json.loads, f):
            if TARGET_CITE in rec["text"]:
                print(f"\n{'='*60}")
                print(f"File:    {fname}")
                print(f"Chunk:   {rec['chunk_id']}")
                print(f"Tokens:  {rec['token_count']}")
                print(f"Text:\n{rec['text']}")