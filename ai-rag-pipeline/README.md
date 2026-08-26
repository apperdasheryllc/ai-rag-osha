# OSHA RAG Ingestion Pipeline

A demonstration Retrieval-Augmented Generation (RAG) pipeline for OSHA safety regulations. This example ai-rag-pipeline scrapes OSHA regulatory text from the web, processes it into chunks, generates embeddings, and provides semantic search capabilities.

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