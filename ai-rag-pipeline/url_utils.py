"""url_utils.py – shared parsing/formatting helpers for paste_urls.py and fetch_urls.py.

Both scripts turn OSHA regulation HTML (pasted or fetched) into the same
``OSHA_URLS`` list format used by ``url_list.py``. This module holds that
common logic in one place:

- ``extract_osha_urls``      – parse HTML, return structured link info
- ``format_as_python_list``  – render extracted links as a Python list literal
- ``report_and_write``       – print the result and save it to ``url_list.py``
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Base used to resolve relative hrefs found in scraped/pasted HTML.
OSHA_BASE = "https://www.osha.gov"

# Path fragment that identifies a regulation link.
REGULATION_PATH_PREFIX = "/laws-regs/regulations/standardnumber/"

OUTPUT_FILE = Path(__file__).resolve().parent / "url_list.py"

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def normalize_href(href: str, page_base: str = OSHA_BASE) -> str | None:
    """Return an absolute URL for *href*, or None if it isn't usable."""
    href = href.strip()
    if not href or href.startswith(("#", "javascript:", "mailto:")):
        return None
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return OSHA_BASE + href
    if href.startswith("http"):
        return href
    # Relative path – resolve against the page base.
    return urljoin(page_base, href)


def is_osha_regulation_url(url: str) -> bool:
    """Return True if *url* points at an OSHA regulation standard page."""
    parsed = urlparse(url)
    return "osha.gov" in parsed.netloc and parsed.path.startswith(REGULATION_PATH_PREFIX)


def parse_standard_segment(segment: str) -> dict[str, str | None]:
    """Extract part, subpart, and standard_number from a URL path segment.

    Examples
    --------
    ``1926``          → part=1926, subpart=None,  standard_number=1926
    ``1926SubpartM``  → part=1926, subpart=M,     standard_number=1926SubpartM
    ``1926.502``      → part=1926, subpart=None,  standard_number=1926.502
    ``1910.147``      → part=1910, subpart=None,  standard_number=1910.147
    """
    # Try "SubpartX" pattern first.
    subpart_match = re.match(r"^(\d+)Subpart([A-Z]{1,3})$", segment, re.IGNORECASE)
    if subpart_match:
        return {
            "part": subpart_match.group(1),
            "subpart": subpart_match.group(2).upper(),
            "standard_number": segment,
        }

    # Try numbered standard like "1926.502" or "1910.147(b)".
    standard_match = re.match(r"^(\d+)(\.\S+)?$", segment)
    if standard_match:
        return {
            "part": standard_match.group(1),
            "subpart": None,
            "standard_number": segment,
        }

    return {"part": None, "subpart": None, "standard_number": segment}


def build_label(title: str, part: str | None, subpart: str | None, standard_number: str) -> str:
    """Build a human-readable label matching the url_list.py convention."""
    if title:
        # Collapse whitespace that often appears in scraped link text.
        title = re.sub(r"\s+", " ", title).strip()
    if title:
        return title

    # Fallback: synthesize label from parsed components.
    if subpart:
        return f"{part} Subpart {subpart}"
    return standard_number


def extract_osha_urls(html: str) -> list[dict[str, str | None]]:
    """Parse *html* and return a list of dicts with extracted OSHA URL info.

    Each dict contains:
        url             – absolute URL
        part            – CFR part number (e.g. "1926")
        subpart         – subpart letter if present (e.g. "M")
        standard_number – last path segment (e.g. "1926.502" or "1926SubpartM")
        title           – link text
        label           – ready-to-use label for url_list.py
    """
    soup = BeautifulSoup(html, "lxml")
    results: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        url = normalize_href(anchor["href"])
        if url is None or not is_osha_regulation_url(url):
            continue
        if url in seen:
            continue
        seen.add(url)

        path = urlparse(url).path  # e.g. /laws-regs/regulations/standardnumber/1926/1926SubpartM
        path_parts = [p for p in path.split("/") if p]
        # Last segment is the most specific identifier; second-to-last is the part dir.
        segment = path_parts[-1] if path_parts else ""
        parsed = parse_standard_segment(segment)

        title = anchor.get_text(separator=" ", strip=True)
        label = build_label(title, parsed["part"], parsed["subpart"], parsed["standard_number"])

        results.append(
            {
                "url": url,
                "part": parsed["part"],
                "subpart": parsed["subpart"],
                "standard_number": parsed["standard_number"],
                "title": title,
                "label": label,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Formatting & output
# ---------------------------------------------------------------------------


def format_as_python_list(entries: list[dict[str, str | None]], var_name: str = "OSHA_URLS") -> str:
    """Render *entries* as a Python list literal matching url_list.py style."""
    lines: list[str] = [f"{var_name} = ["]
    prev_part: str | None = None

    for entry in entries:
        part = entry["part"]
        if part and part != prev_part:
            if prev_part is not None:
                lines.append("")
            lines.append(f"    # ── Part {part} ────────────────────────────────────────────────────────────")
            prev_part = part

        label = entry["label"].replace('"', "'")
        url = entry["url"]
        lines.append(f'    ("{label}",')
        lines.append(f'     "{url}"),')

    lines.append("]")
    return "\n".join(lines)


def write_output(python_src: str) -> None:
    """Save *python_src* to url_list.py, overwriting its previous contents."""
    header = '"""Auto-generated by paste_urls.py / fetch_urls.py – review before relying on it."""\n\n'
    OUTPUT_FILE.write_text(header + python_src + "\n", encoding="utf-8")
    print(f"\nOutput written to: {OUTPUT_FILE}")


def report_and_write(entries: list[dict[str, str | None]], empty_message: str) -> None:
    """Print *entries* (or exit with *empty_message*) and write them to url_list.py."""
    if not entries:
        print(empty_message, file=sys.stderr)
        sys.exit(1)

    python_src = format_as_python_list(entries)

    print("\n" + "─" * 60)
    print(python_src)
    print("─" * 60)
    print(f"\nFound {len(entries)} regulation link(s).")

    write_output(python_src)
