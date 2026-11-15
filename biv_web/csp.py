"""Stamp a Content-Security-Policy into the pages.

Scripts may come only from the pinned D3 file (checked by its integrity hash) and from the
page's own inline script, identified by its SHA-256. Data may be fetched only from the page's
own site. Fonts and their stylesheet only from Google Fonts. Nothing else.

Usage: python -m biv_web.csp docs/index.html docs/pair.html
The hash changes whenever the inline script changes, so run this after editing a page
(`python -m biv_web config_explore.toml` and `biv_web.standalone` already do).
"""
import base64
import hashlib
import re
import sys
from pathlib import Path

META = re.compile(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">')


def policy(html: str) -> str:
    hashes = []
    for m in re.finditer(r"<script>(.*?)</script>", html, flags=re.S):
        digest = base64.b64encode(hashlib.sha256(m.group(1).encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    return "; ".join([
        "default-src 'none'",
        "script-src https://cdn.jsdelivr.net " + " ".join(hashes),
        "style-src 'unsafe-inline' https://fonts.googleapis.com",
        "font-src https://fonts.gstatic.com",
        "img-src 'self' data:",
        "connect-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
    ])


def stamp_text(html: str) -> str:
    meta = '<meta http-equiv="Content-Security-Policy" content="__P__">'
    if META.search(html):
        html = META.sub(meta, html, count=1)
    else:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + meta, 1)
    return html.replace("__P__", policy(html), 1)


def stamp(path) -> Path:
    path = Path(path)
    path.write_text(stamp_text(path.read_text(encoding="utf-8")), encoding="utf-8")
    return path


if __name__ == "__main__":
    for f in sys.argv[1:] or ["docs/index.html"]:
        print("stamped", stamp(f))
