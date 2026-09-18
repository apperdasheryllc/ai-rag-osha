"""paste_urls.py – extract OSHA_URLS entries from HTML pasted into htmlInput.

Usage
-----
Paste raw HTML into the ``htmlInput`` variable below, then run:

    python3 paste_urls.py

The script parses every <a href="..."> in htmlInput, keeps links that
point to OSHA regulations, and prints a Python list of the results into
url_list.py.

For most subpart pages, prefer fetch_urls.py, which fetches the page and
extracts these links automatically — no copy/paste required. This script
is still useful for debugging fetch_urls.py's extraction (paste in the
same HTML it fetched to compare results) or for loading OSHA subpart
pages that don't fetch cleanly, by pasting their HTML in by hand.
"""

from __future__ import annotations

import sys

from url_utils import extract_osha_urls, report_and_write

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


def main() -> None:
    if not htmlInput.strip():
        print("htmlInput is empty. Paste HTML into the variable and re-run.", file=sys.stderr)
        sys.exit(1)

    entries = extract_osha_urls(htmlInput)
    report_and_write(entries, empty_message="No OSHA regulation links found in the pasted content.")


if __name__ == "__main__":
    main()
