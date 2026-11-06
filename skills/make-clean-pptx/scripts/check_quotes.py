#!/usr/bin/env python3
"""Check that the quotations in a deck spec really appear in the source text.

    check_quotes.py deck.json source.txt [--min-words 4]

Looks at every text value of the spec for passages between quotation marks
(" ", « », “ ”) of at least --min-words words, and searches each in the source
(ignoring case, accents, quote styles and spacing). Quotes not found are listed:
fix the wording, mark it as a paraphrase, or check the source again.

Prints JSON: {"checked": N, "missing": [{"slide": n, "quote": "..."}]}. Exit 0 when
every quote is found (or there is none), 1 otherwise, 2 when a file cannot be read.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

QUOTE = re.compile(r"«\s*([^»]+?)\s*»|“([^”]+)”|\"([^\"]+)\"")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"[^a-z0-9']+", " ", text).strip()


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def check(spec: dict, source: str, min_words: int = 4) -> dict:
    src = " " + norm(source) + " "
    checked, missing = 0, []
    for n, slide in enumerate(spec.get("slides", []), 1):
        for s in strings([slide.get("fill", {}), slide.get("insert", []), slide.get("notes", "")]):
            for m in QUOTE.finditer(s):
                q = next(g for g in m.groups() if g)
                if len(q.split()) < min_words:
                    continue
                checked += 1
                if " " + norm(q) + " " not in src:
                    missing.append({"slide": n, "quote": q})
    return {"checked": checked, "missing": missing}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("source")
    ap.add_argument("--min-words", type=int, default=4)
    args = ap.parse_args(argv)
    try:
        spec = json.load(open(args.spec, encoding="utf-8"))
        source = open(args.source, encoding="utf-8", errors="replace").read()
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"cannot read input: {exc}"}))
        return 2
    report = check(spec, source, args.min_words)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["missing"] else 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        getattr(_s, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
