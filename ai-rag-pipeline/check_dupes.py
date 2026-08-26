# check_dupes.py
# Scans every cleaned .txt file for repeated sentences within a single section.
import os, re

CLEAN_DIR = "clean_text"
SECTION_MARKER = "@@SECTION@@"

total_dupes = 0

for fname in sorted(os.listdir(CLEAN_DIR)):
    if not fname.endswith(".txt"):
        continue
    path = os.path.join(CLEAN_DIR, fname)
    with open(path) as f:
        content = f.read()

    sections = content.split(SECTION_MARKER)
    for i, section in enumerate(sections):
        # Extract sentences from [TEXT] block
        text_match = re.search(r'\[TEXT\]\s*([\s\S]+)', section)
        if not text_match:
            continue
        text = text_match.group(1).strip()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]

        seen = set()
        for sentence in sentences:
            if sentence in seen:
                print(f"  DUPE in {fname}, section {i}: \"{sentence[:80]}...\"")
                total_dupes += 1
            seen.add(sentence)

if total_dupes == 0:
    print("✅ No duplicate sentences found across all cleaned files.")
else:
    print(f"\n⚠️  {total_dupes} duplicate sentence(s) found — check HTML structure above.")