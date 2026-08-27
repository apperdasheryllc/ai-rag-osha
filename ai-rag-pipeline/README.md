# OSHA RAG Ingestion Pipeline

A demonstration Retrieval-Augmented Generation (RAG) pipeline for OSHA safety regulations. This example ai-rag-pipeline scrapes OSHA regulatory text from the web, processes it into chunks, generates embeddings, and provides semantic search capabilities.

<img width="970" height="506" alt="Screenshot 2026-08-27 at 9 35 56 AM" src="https://github.com/user-attachments/assets/aa6f454e-3d10-4403-a9b8-f990b5623440" />


## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Pipeline Procedures

### 1. Prepare URLs (paste_urls.py)

**Purpose**: Extract OSHA regulation links from an HTML list.

**Usage**:
1. Copy the HTML list of regulation links from an OSHA page
2. Paste the HTML into the `htmlInput` variable in `paste_urls.py`
3. Run:
   ```bash
   python paste_urls.py
   ```

**Output**: 
- Parsed URLs are printed to console
- Results saved to `url_list.py`
- Extracts links matching `/laws-regs/regulations/standardnumber/` pattern


---

### 2. URL List (url_list.py)

**Purpose**: Curate the list of OSHA regulation URLs to ingest.

**Usage**:
1. Review the extracted URLs from `paste_urls.py`
2. Add desired URLs to the `OSHA_URLS` list in `url_list.py`
3. Each entry should be a tuple: `(label, url)`

**Example**:
```python
OSHA_URLS = [
    ("1926.95 - Criteria for personal protective equipment.",
     "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.95"),
    ("1926.100 - Head protection.",
     "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.100"),
]
```

---

### 3. Scraping (scraper.py)

**Purpose**: Download and cache HTML pages from OSHA.gov.

**Usage**:
```bash
python scraper.py
```

**Behavior**:
- Fetches each URL with a 2.5-second delay (respectful scraping)
- Skips already-cached pages
- Creates HTML files in `raw_html/` directory
- Stores metadata (URL, hash, timestamp) in `metadata/` directory
- Logs all activity to `logs/scraper.log`

**Output directories**:
- `raw_html/` – Raw HTML pages (one per regulation)
- `metadata/` – JSON metadata files with fetch info and content hashes

---

### 4. Cleaning (cleaner.py)

**Purpose**: Extract regulatory text from HTML and normalize formatting.

**Usage**:
```bash
python cleaner.py
```

**Process**:
1. Removes navigation, headers, footers, and other boilerplate
2. Targets OSHA's Drupal structure for regulation body extraction
3. Identifies sections marked with `@@SECTION@@` delimiter
4. Preserves citations (e.g., "1926.104(d)") for each section
5. Normalizes fractions (½ → 1/2, etc.)
6. Handles both primary regulation sections and fallback heuristics

**Output**:
- `clean_text/` – Cleaned text files with sections separated by `@@SECTION@@`
- Format: `[CITATION] <citation>\n[TEXT] <body_text>`

---

### 5. Chunking (chunker.py)

**Purpose**: Split cleaned text into semantically coherent chunks for embedding.

**Usage**:
```bash
python chunker.py
```

**Configuration**:
- `MAX_TOKENS` – 400 (target chunk size)
- `OVERLAP_TOKENS` – 0 (no overlap when splitting by section)
- `MIN_TOKENS` – 15 (discard fragments smaller than this)

**Process**:
1. Reads cleaned text files section-by-section
2. Groups sections into chunks respecting token limits
3. For oversized sections, uses recursive character splitting with fallback
4. Counts tokens using GPT-3 tokenizer (`cl100k_base`)
5. Preserves citation information in each chunk

**Output**:
- `chunks/` – JSONL files, one line per chunk
- Each chunk includes: `chunk_id`, `text`, `citation`, `label`, `source_url`, `chunk_index`, `token_count`

---

### 6. Validation (validate.py)

**Purpose**: Check for data quality issues in chunk files.

**Usage**:
```bash
python validate.py
```

**Checks**:
- ✓ No empty JSONL files
- ✓ No empty text chunks
- ✓ No chunks with fewer than 20 tokens
- ✓ All lines are valid JSON

**Output**:
- Prints list of issues if found
- Returns success message if all checks pass

---

### 7. De-duplicate (check_dupes.py)

**Purpose**: Identify repeated sentences within sections (indicates HTML parsing issues).

**Usage**:
```bash
python check_dupes.py
```

**Process**:
1. Scans all cleaned text files
2. Extracts sentences from each section's `[TEXT]` block
3. Flags sentences that repeat within the same section
4. Indicates possible HTML structure problems needing manual review

**Output**:
- Reports duplicate sentences with file and section location
- Suggests reviewing HTML structure

---

### 8. Diagnose (diagnose.py)

**Purpose**: Inspect specific chunks in detail for troubleshooting.

**Usage**:
1. Edit the `TARGET_CITE` variable (e.g., `"1926.104"`)
2. Run:
   ```bash
   python diagnose.py
   ```

**Output**:
- Displays all matching chunks with full content
- Shows filename, chunk ID, token count, and complete text
- Helpful for debugging specific regulations

---

### 9. Embed & Load (embed_and_load.py)

**Purpose**: Generate embeddings and populate the vector database.

**Usage**:
```bash
python embed_and_load.py
```

**Process**:
1. Reads all chunks from JSONL files
2. Uses `all-MiniLM-L6-v2` sentence transformer model (runs locally)
3. Generates embeddings for each chunk
4. Upserts chunks into ChromaDB in batches of 100
5. Creates persistent vector store in `chroma_store/`

**Output**:
- `chroma_store/` – Persistent ChromaDB database
- Console output shows loading progress
- Success message with total chunk count

**Note**: First run downloads the embedding model (~90MB) — takes 1-2 minutes on initial execution.

---

### 10. Testing (test_rag.py)

**Purpose**: Query the vector store with semantic search to validate ingestion.

**Usage**:
```bash
python test_rag.py
```

**Features**:
- Query expansion: Paraphrases questions using a heuristic map
- Returns top 5 results with distance scores
- Displays citation, regulation label, source URL, and full text
- Example query: "How long does a safety belt lanyard need to be?"

**Output**:
- For each result: Citation, regulation info, source URL, relevance distance
- Full chunk text for context

---

### 11. Reload (reload_vectors.py)

**Purpose**: Clear and rebuild the vector store when cleaning/chunking is modified.

**Usage** (when re-processing is needed):
```bash
python reload_vectors.py
```

**Process**:
1. Deletes the existing collection from ChromaDB
2. Recreates the collection fresh
3. Re-embeds and reloads all chunks
4. Useful after fixing HTML cleaning or chunking logic

**When to use**:
- After modifying `cleaner.py` or `chunker.py`
- If `diagnose.py` reveals chunk content issues
- To reset embeddings for a fresh start

<img width="841" height="349" alt="Screenshot 2026-08-26 at 6 59 42 PM" src="https://github.com/user-attachments/assets/c3f22e16-b9d8-440c-b38a-0cecc79f9969" />

---

## Troubleshooting

### Validation Issues

If `validate.py` reports problems:

1. **Empty chunks or low token counts**
   - Run `diagnose.py` to inspect specific sections
   - Check if HTML structure is being parsed correctly
   - May indicate incomplete regulation pages or parsing failures

2. **Duplicate sentences in sections**
   - Run `check_dupes.py` to identify which sections
   - Likely indicates OSHA HTML structure issue (duplicated content in page)
   - Review raw HTML in `raw_html/` to confirm duplication

### Content Quality Issues

1. **Poor search results from `test_rag.py`**
   - Check that chunks are being created correctly with `diagnose.py`
   - Verify embeddings are fresh; re-run `reload_vectors.py` if needed
   - Review chunking parameters in `chunker.py`

2. **Text extraction looks wrong**
   - Run `diagnose.py` on a known section (e.g., `1926.104`)
   - If text doesn't match the website, review HTML in `raw_html/`
   - May need to adjust CSS selectors in `cleaner.py`

### Common Workflows

**Full re-ingestion (after code changes)**:
```bash
python validate.py           # Check current state
python check_dupes.py        # Verify no duplication issues
python chunker.py           # Re-chunk if splitting changed
python reload_vectors.py     # Rebuild vector store
python test_rag.py          # Validate with test queries
```

**Incremental updates (add new regulations)**:
1. Add new URLs to `url_list.py`
2. Run `scraper.py`
3. Run `cleaner.py`
4. Run `reload_vectors.py` (requires full rebuild)

---

## Directory Structure

```
ai-rag-pipeline/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── paste_urls.py               # Extract URLs from HTML
├── url_list.py                 # Curated list of regulation URLs
├── scraper.py                  # Download and cache HTML
├── cleaner.py                 # Extract and normalize text
├── chunker.py                 # Split into semantic chunks
├── validate.py                 # Check chunk quality
├── check_dupes.py              # Detect duplicate sentences
├── diagnose.py                 # Inspect specific chunks
├── embed_and_load.py           # Generate embeddings & load DB
├── test_rag.py                # Query the vector store
├── reload_vectors.py           # Clear & rebuild vector store
│
├── raw_html/                   # Downloaded HTML pages
│   └── 1926_1926_95.html, etc.
├── metadata/                   # Scrape metadata (timestamps, hashes)
│   └── 1926_1926_95.json, etc.
├── clean_text/                 # Extracted and cleaned text
│   └── 1926_1926_95.txt, etc.
├── chunks/                     # Semantic chunks (JSONL format)
│   └── 1926_1926_95.jsonl, etc.
├── chroma_store/               # Vector database (persistent)
│   └── [ChromaDB collections]
└── logs/                        # Execution logs
    └── scraper.log
```

---

## Data Flow

```
URL List (url_list.py)
         ↓
    Scraper (scraper.py)
    [raw_html/, metadata/]
         ↓
    Cleaner (cleaner.py)
    [clean_text/]
         ↓
    Chunker (chunker.py)
    [chunks/]
         ↓
    Validate (validate.py)
    Deduplicate (check_dupes.py)
         ↓
    Embed & Load (embed_and_load.py)
    [chroma_store/]
         ↓
    Test & Query (test_rag.py)
         ↓
    Reload Vectors (reload_vectors.py)
    [chroma_store/]
         ↓
    Test & Query (test_rag.py)
```

---

## Notes

- All scripts use relative paths and expect to be run from the `ai-rag-pipeline/` directory
- Token counting uses the GPT-3 tokenizer (`cl100k_base`) for consistency with LLM context windows
- Embeddings use a lightweight local model (`all-MiniLM-L6-v2`) that runs without GPU
- ChromaDB stores vectors persistently in `chroma_store/` — safe to query repeatedly
- Scraper includes respectful delays (2.5 sec) between requests to avoid overloading OSHA servers
