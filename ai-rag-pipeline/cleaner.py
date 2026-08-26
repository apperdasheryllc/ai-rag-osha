# cleaner.py  (v3 — deduplication fix)
import os, re
from bs4 import BeautifulSoup
from tqdm import tqdm

RAW_DIR   = "raw_html"
CLEAN_DIR = "clean_text"
os.makedirs(CLEAN_DIR, exist_ok=True)

SECTION_MARKER = "\n\n@@SECTION@@\n"

def extract_regulation_body(soup: BeautifulSoup):
    for tag in soup.select("nav, header, footer, .breadcrumb, #top-nav, "
                            ".sidebar, script, style, .usa-nav, .usa-footer, "
                            ".back-to-top, .reg-history, #reg-history"):
        tag.decompose()
    for selector in ["#reg-text", ".reg-text", "main", "article", ".container"]:
        found = soup.select_one(selector)
        if found:
            return found
    return soup.body or soup

def normalize_fraction(text: str) -> str:
    fractions = {"½": "1/2", "¼": "1/4", "¾": "3/4", "⅓": "1/3", "⅔": "2/3"}
    for entity, replacement in fractions.items():
        text = text.replace(entity, replacement)
    return text

# ── Deduplicated section extraction ─────────────────────────────────────

def extract_osha_sections(body_tag) -> list[tuple[str, str]]:
    """
    Return a list of (citation, body_text) tuples by targeting OSHA's
    Drupal div structure directly.

    Primary path  — targets the known OSHA container class:
        div.paragraph--type--regulations-standard-number
        └── span[id]                    ← citation lives here as an attribute
        └── div.field--name-field-...   ← body text lives here only

    Fallback path — for any <p> or <div> NOT inside a known container,
    use the old bold/strong heuristic (handles preambles and appendices).
    """
    sections = []

    # ── Primary path: OSHA Drupal regulation containers ──────────────────────
    regulation_divs = body_tag.select(
        "div.paragraph--type--regulations-standard-number"
    )

    # Track which tags have been claimed so the fallback doesn't reprocess them
    claimed_tags = set()

    for reg_div in regulation_divs:
        claimed_tags.add(id(reg_div))

        # 1. Citation — prefer the span[id] attribute (most reliable)
        cite = ""
        cite_span = reg_div.find("span", id=True)
        if cite_span:
            candidate = cite_span["id"].strip()
            # Validate it looks like a CFR citation
            if re.match(r'^\d{3,4}[\.\d]*', candidate):
                cite = candidate
                claimed_tags.add(id(cite_span))

        # 2. Body text — pull ONLY from the inner field div, never the outer wrapper
        #    This is the critical change that prevents double-counting.
        body_text = ""
        field_div = reg_div.find(
            "div", class_=lambda c: c and "field--name-field" in c
        )
        if field_div:
            claimed_tags.add(id(field_div))
            body_text = normalize_fraction(
                field_div.get_text(separator=" ", strip=True)
            )
            body_text = re.sub(r'\s+', ' ', body_text).strip()

        # 3. Fallback body — if no inner field div, use the outer div minus the span
        if not body_text:
            # Temporarily remove the citation span to avoid including it in body
            if cite_span:
                cite_span_copy = cite_span.extract()
            body_text = normalize_fraction(
                reg_div.get_text(separator=" ", strip=True)
            )
            body_text = re.sub(r'\s+', ' ', body_text).strip()
            # Restore the span (in case anything else references the tree)
            if cite_span:
                reg_div.insert(0, cite_span_copy)

        if body_text and len(body_text) >= 20:
            sections.append((cite, body_text))

    # ── Fallback path: unclaimed <p> tags (preambles, notes, appendices) ──────
    for tag in body_tag.find_all("p"):
        if id(tag) in claimed_tags:
            continue
        # Skip if this <p> lives inside a claimed regulation div
        if any(id(parent) in claimed_tags for parent in tag.parents):
            continue

        text = normalize_fraction(tag.get_text(separator=" ", strip=True))
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) < 20:
            continue

        # Check for old-style inline citation (bold/strong leading the paragraph)
        cite = ""
        for selector in ["span.paranum", "b", "strong"]:
            node = tag.find(selector)
            if node:
                candidate = node.get_text(strip=True)
                if re.match(r'^\d{4}\.\d+', candidate) or \
                   re.match(r'^\(\w+\)', candidate):
                    cite = candidate
                    # Remove from tag so it's not duplicated in body text
                    node.decompose()
                    text = normalize_fraction(
                        tag.get_text(separator=" ", strip=True)
                    )
                    text = re.sub(r'\s+', ' ', text).strip()
                    break

        sections.append((cite, text))

    return sections


def process_html(html: str) -> str:
    """
    Convert an OSHA regulation HTML page to structured plain text.
    Each numbered section becomes:

        @@SECTION@@
        [CITATION] 1926.104(e)
        [TEXT] All safety belt and lanyard hardware shall be...
    """
    soup = BeautifulSoup(html, "lxml")
    body = extract_regulation_body(soup)

    sections     = extract_osha_sections(body)
    output_lines = []

    for cite, text in sections:
        if cite:
            output_lines.append(SECTION_MARKER)
            output_lines.append(f"[CITATION] {cite}")
            output_lines.append(f"[TEXT] {text}")
        else:
            output_lines.append(f"\n{text}")

    result = "\n".join(output_lines)
    result = re.sub(r'\n{4,}', '\n\n', result)
    return result.strip()


# ── Process the HTML file ─────────────────────────────────────────────────────────

def process_file(html_filename: str):
    base     = os.path.splitext(html_filename)[0]
    in_path  = os.path.join(RAW_DIR,   html_filename)
    out_path = os.path.join(CLEAN_DIR, f"{base}.txt")

    with open(in_path, "r", encoding="utf-8") as f:
        html = f.read()

    cleaned = process_html(html)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned)


if __name__ == "__main__":
    for f in os.listdir(CLEAN_DIR):
        os.remove(os.path.join(CLEAN_DIR, f))

    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".html")]
    print(f"Cleaning {len(files)} HTML files (deduplication fix)...\n")
    for fname in tqdm(files):
        process_file(fname)
    print(f"\n✅ Done — deduplicated structured text in /{CLEAN_DIR}/")