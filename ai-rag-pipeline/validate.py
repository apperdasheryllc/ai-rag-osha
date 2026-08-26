# validate.py
import os, json

CHUNK_DIR = "chunks"
issues    = []

for fname in sorted(os.listdir(CHUNK_DIR)):
    if not fname.endswith(".jsonl"):
        continue
    path = os.path.join(CHUNK_DIR, fname)
    with open(path) as f:
        lines = f.readlines()
    if not lines:
        issues.append(f"EMPTY FILE: {fname}")
        continue
    for i, line in enumerate(lines):
        try:
            rec = json.loads(line)
            if not rec.get("text","").strip():
                issues.append(f"EMPTY CHUNK: {fname} line {i}")
            if rec.get("token_count", 0) < 20:
                issues.append(f"TINY CHUNK (<20 tokens): {fname} line {i}")
        except json.JSONDecodeError:
            issues.append(f"BAD JSON: {fname} line {i}")

if issues:
    print(f"⚠️  {len(issues)} issues found:")
    for iss in issues: print(f"   {iss}")
else:
    print("✅ All chunks valid — knowledge source is ready.")