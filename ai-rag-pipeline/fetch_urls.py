"""fetch_urls.py – fetch an OSHA subpart page and extract its regulation links.

Usage
-----
    python3 fetch_urls.py [URL]

If URL is omitted, DEFAULT_URL below is used. The script downloads the page,
isolates the <article> element that holds the list of standard links (the
same links you'd otherwise copy/paste into paste_urls.py), and writes the
resulting OSHA_URLS list to url_list.py — reusing url_utils.py's parsing
and formatting so both scripts produce identical output.
"""

from __future__ import annotations

import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from url_utils import OSHA_BASE, extract_osha_urls, report_and_write

DEFAULT_URL = "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926SubpartE"

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0"}
TIMEOUT_SEC = 40


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEC)
    resp.raise_for_status()
    return resp.text


def extract_article_html(html: str, page_url: str) -> str:
    """Return the HTML of the <article> element that holds the standard links.

    OSHA subpart pages wrap the content in
    ``<article data-history-node-id="..." about="/laws-regs/.../1926SubpartE">``.
    Falling back to any <article data-history-node-id> (or the full page)
    keeps this working if the ``about`` path doesn't match exactly.
    """
    soup = BeautifulSoup(html, "lxml")
    page_path = urlparse(page_url).path

    article = soup.find("article", attrs={"about": page_path})
    if article is None:
        article = soup.find("article", attrs={"data-history-node-id": True})
    if article is None:
        print(
            "Warning: could not locate the <article> container; scanning the entire page instead.",
            file=sys.stderr,
        )
        return html
    return str(article)


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    print(f"Fetching {url} ...")
    html = fetch_html(url)
    article_html = extract_article_html(html, url)

    entries = extract_osha_urls(article_html)
    # Drop a self-referential link back to the subpart page itself, if present.
    entries = [e for e in entries if e["url"] not in (url, OSHA_BASE + urlparse(url).path)]

    report_and_write(entries, empty_message="No OSHA regulation links found on that page.")


if __name__ == "__main__":
    main()
