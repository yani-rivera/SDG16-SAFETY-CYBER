"""One-file copy of the explorer page (data inlined), for sharing or previewing without a web server.

Usage: python -m biv_web.standalone docs            -> docs/standalone.html
"""
import sys
from pathlib import Path

from .csp import stamp_text

FETCH = "await Promise.all(['countries.geojson', 'variables.json'].map(f => fetch('data/explore/' + f).then(r => r.json())))"


def build(docs):
    docs = Path(docs)
    page = (docs / "index.html").read_text(encoding="utf-8")
    if FETCH not in page:
        raise ValueError("index.html no longer has the expected data-loading line")
    data = [(docs / "data" / "explore" / f).read_text(encoding="utf-8").replace("</", "<\\/")
            for f in ("countries.geojson", "variables.json")]
    out = docs / "standalone.html"
    out.write_text(stamp_text(page.replace(FETCH, f"[{data[0]}, {data[1]}]")), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "docs"))
