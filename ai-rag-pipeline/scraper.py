# scraper.py
import os, time, json, hashlib, logging
import requests
from tqdm import tqdm
from url_list import OSHA_URLS

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DIR     = "raw_html"
META_DIR    = "metadata"
LOG_FILE    = "logs/scraper.log"
DELAY_SEC   = 2.5          # Be polite to OSHA servers
TIMEOUT_SEC = 40
HEADERS     = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0"}

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def url_to_filename(url: str) -> str:
    """Create a safe, stable filename from a URL."""
    slug = url.replace("https://www.osha.gov/laws-regs/regulations/standardnumber/", "")
    slug = slug.replace("/", "_").replace(".", "_")
    return slug

def fetch_and_save(label: str, url: str):
    filename = url_to_filename(url)
    html_path = os.path.join(RAW_DIR, f"{filename}.html")
    meta_path = os.path.join(META_DIR, f"{filename}.json")

    # Skip if already cached
    if os.path.exists(html_path):
        logging.info(f"SKIP (cached): {url}")
        return True

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEC)
        resp.raise_for_status()

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(resp.text)

        meta = {
            "label":        label,
            "url":          url,
            "filename":     filename,
            "status_code":  resp.status_code,
            "fetched_at":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "content_hash": hashlib.md5(resp.text.encode()).hexdigest(),
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        logging.info(f"OK: {url}")
        return True

    except Exception as e:
        logging.error(f"FAIL: {url} — {e}")
        print(f"  ⚠️  Failed: {url} ({e})")
        return False

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)
    print(f"Fetching {len(OSHA_URLS)} OSHA documents...\n")
    ok = fail = 0
    for label, url in tqdm(OSHA_URLS):
        success = fetch_and_save(label, url)
        if success: ok += 1
        else:       fail += 1
        time.sleep(DELAY_SEC)
    print(f"\n✅ Done — {ok} fetched, {fail} failed. See logs/scraper.log")