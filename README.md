# OSHA RAG Ingestion Pipeline

A demonstration Retrieval-Augmented Generation (RAG) pipeline for OSHA safety regulations. This example ai-rag-pipeline scrapes OSHA regulatory text from the web, processes it into chunks, generates embeddings, and provides semantic search capabilities.


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