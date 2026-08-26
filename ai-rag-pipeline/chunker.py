# chunker.py  (v2 — section-aware)
import os, re, json
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

CLEAN_DIR = "clean_text"
CHUNK_DIR = "chunks"
META_DIR  = "metadata"
os.makedirs(CHUNK_DIR, exist_ok=True)

SECTION_MARKER  = "@@SECTION@@"
MAX_TOKENS      = 400   # Smaller than before — one section per chunk
OVERLAP_TOKENS  = 0     # No overlap needed when splitting by section
MIN_TOKENS      = 15    # Discard fragments shorter than this

enc = tiktoken.get_encoding("cl100k_base")

def token_len(text: str) -> int:
    return len(enc.encode(text))

# Fallback splitter for oversized single sections (appendices, tables)
fallback_splitter = RecursiveCharacterTextSplitter(
    chunk_size      = MAX_TOKENS,
    chunk_overlap   = 40,
    length_function = token_len,
    separators      = ["\n\n", "\n", ". ", " "],
)

def parse_section(raw: str) -> tuple[str, str]:
    """
    Parse a raw section block into (citation, text).
    Input looks like:
        [CITATION] 1926.104(d)
        [TEXT] Safety belt lanyard shall be...
    """
    cite_match = re.search(r'\[CITATION\]\s*(.+)', raw)
    text_match = re.search(r'\[TEXT\]\s*([\s\S]+)', raw)
    cite = cite_match.group(1).strip() if cite_match else ""
    text = text_match.group(1).strip() if text_match else raw.strip()
    return cite, text

def build_chunk_text(cite: str, text: str) -> str:
    """Assemble the final chunk text — citation always leads."""
    if cite:
        return f"{cite}\n{text}"
    return text

def load_metadata(base_name: str) -> dict:
    meta_path = os.path.join(META_DIR, f"{base_name}.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return json.load(f)
    return {}

def chunk_file(txt_filename: str):
    base     = os.path.splitext(txt_filename)[0]
    in_path  = os.path.join(CLEAN_DIR, txt_filename)
    out_path = os.path.join(CHUNK_DIR, f"{base}.jsonl")

    with open(in_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return

    meta     = load_metadata(base)
    sections = content.split(SECTION_MARKER)
    chunks   = []   # list of (cite, text) tuples

    for raw_section in sections:
        raw_section = raw_section.strip()
        if not raw_section:
            continue

        cite, text = parse_section(raw_section)

        if token_len(text) <= MAX_TOKENS:
            # Section fits in one chunk
            chunks.append((cite, text))
        else:
            # Section too long — split it, but preserve citation in every sub-chunk
            sub_chunks = fallback_splitter.split_text(text)
            for i, sub in enumerate(sub_chunks):
                sub_cite = f"{cite} (continued {i+1})" if cite else ""
                chunks.append((sub_cite, sub))

    # Write output
    with open(out_path, "w", encoding="utf-8") as f:
        written = 0
        for i, (cite, text) in enumerate(chunks):
            chunk_text = build_chunk_text(cite, text)
            tok_count  = token_len(chunk_text)

            if tok_count < MIN_TOKENS:
                continue  # Discard fragments

            record = {
                "chunk_id":     f"{base}_chunk_{i:04d}",
                "chunk_index":  i,
                "total_chunks": len(chunks),
                "token_count":  tok_count,
                "citation":     cite,
                "label":        meta.get("label", base),
                "source_url":   meta.get("url", ""),
                "fetched_at":   meta.get("fetched_at", ""),
                "text":         chunk_text,
            }
            f.write(json.dumps(record) + "\n")
            written += 1

if __name__ == "__main__":
    # Clear old chunks
    for f in os.listdir(CHUNK_DIR):
        if f.endswith(".jsonl"):
            os.remove(os.path.join(CHUNK_DIR, f))

    files = [f for f in os.listdir(CLEAN_DIR) if f.endswith(".txt")]
    print(f"Chunking {len(files)} documents (section-aware)...\n")
    for fname in tqdm(files):
        chunk_file(fname)

    total = sum(
        sum(1 for _ in open(os.path.join(CHUNK_DIR, f)))
        for f in os.listdir(CHUNK_DIR) if f.endswith(".jsonl")
    )
    print(f"\n✅ Done — {total} section-level chunks in /{CHUNK_DIR}/")