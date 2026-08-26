"""paste_urls.py – extract OSHA_URLS entries from HTML stored in exampleHtmlInput.

Usage
-----
Paste raw HTML into the ``htmlInput`` variable below, then run:

    python3 paste_urls.py

The script parses every <a href="..."> in htmlInput, keeps links that
point to OSHA regulations, and prints a Python list of the results into
url_list.py. 
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Base used to resolve relative hrefs found in the pasted HTML.
OSHA_BASE = "https://www.osha.gov"

# Path fragment that identifies a regulation link.
REGULATION_PATH_PREFIX = "/laws-regs/regulations/standardnumber/"

OUTPUT_FILE = Path(__file__).resolve().parent / "url_list.py"

# ---------------------------------------------------------------------------
# Input – paste your HTML here
# ---------------------------------------------------------------------------

htmlInput = """
<ul>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.95" id="1926.95" title="1926.95" target="_self">1926.95 - Criteria for personal protective equipment.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.96" id="1926.96" title="1926.96" target="_self">1926.96 - Occupational foot protection.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.97" id="1926.97" title="1926.97" target="_self">1926.97 - Electrical protective equipment.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.98" id="1926.98" title="1926.98" target="_self">1926.98 - [Reserved] </a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.100" id="1926.100" title="1926.100" target="_self">1926.100 - Head protection.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.101" id="1926.101" title="1926.101" target="_self">1926.101 - Hearing protection.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.102" id="1926.102" title="1926.102" target="_self">1926.102 - Eye and face protection.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.103" id="1926.103" title="1926.103" target="_self">1926.103 - Respiratory protection.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.104" id="1926.104" title="1926.104" target="_self">1926.104 - Safety belts, lifelines, and lanyards.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.105" id="1926.105" title="1926.105" target="_self">1926.105 - Safety nets.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.106" id="1926.106" title="1926.106" target="_self">1926.106 - Working over or near water.</a></li>
	<li><a href="/laws-regs/regulations/standardnumber/1926/1926.107" id="1926.107" title="1926.107" target="_self">1926.107 - Definitions applicable to this subpart.</a></li>
</ul>
"""

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _normalize_href(href: str, page_base: str = OSHA_BASE) -> str | None:
    """Return an absolute URL or None if the href is not usable."""
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


def _is_osha_regulation_url(url: str) -> bool:
    parsed = urlparse(url)
    return (
        "osha.gov" in parsed.netloc
        and parsed.path.startswith(REGULATION_PATH_PREFIX)
    )


def _parse_standard_segment(segment: str) -> dict[str, str | None]:
    """Extract part, subpart, and standard_number from the URL path segment.

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


def _build_label(title: str, part: str | None, subpart: str | None, standard_number: str) -> str:
    """Build a human-readable label matching the url_list.py convention."""
    if title:
        # Collapse whitespace that often appears in scraped link text.
        title = re.sub(r"\s+", " ", title).strip()

    if title:
        return title

    # Fallback: synthesize label from parsed components.
    if subpart:
        return f"{part} Subpart {subpart}"
    if part and standard_number != part:
        return f"{standard_number}"
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
        url = _normalize_href(anchor["href"])
        if url is None or not _is_osha_regulation_url(url):
            continue
        if url in seen:
            continue
        seen.add(url)

        path = urlparse(url).path  # e.g. /laws-regs/regulations/standardnumber/1926/1926SubpartM
        path_parts = [p for p in path.split("/") if p]
        # Last segment is the most specific identifier; second-to-last is the part dir.
        segment = path_parts[-1] if path_parts else ""
        parsed = _parse_standard_segment(segment)

        title = anchor.get_text(separator=" ", strip=True)
        label = _build_label(title, parsed["part"], parsed["subpart"], parsed["standard_number"])

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
# Formatting
# ---------------------------------------------------------------------------

def _format_as_python_list(entries: list[dict[str, str | None]], var_name: str = "OSHA_URLS") -> str:
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

# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _write_output(python_src: str) -> None:
    header = (
        '"""Auto-generated by paste_urls.py – review and copy entries into url_list.py."""\n\n'
    )
    OUTPUT_FILE.write_text(header + python_src + "\n", encoding="utf-8")
    print(f"\nOutput written to: {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    html = htmlInput
    if not html.strip():
        print("htmlInput is empty. Paste HTML into the variable and re-run.", file=sys.stderr)
        sys.exit(1)

    entries = extract_osha_urls(html)

    if not entries:
        print("No OSHA regulation links found in the pasted content.", file=sys.stderr)
        sys.exit(1)

    python_src = _format_as_python_list(entries)

    print("\n" + "─" * 60)
    print(python_src)
    print("─" * 60)
    print(f"\nFound {len(entries)} regulation link(s).")

    _write_output(python_src)


if __name__ == "__main__":
    main()