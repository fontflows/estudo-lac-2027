"""Dump the statement text of downloaded open.kattis.com problem pages.

Usage: python -I nac_kattis_text.py <dir with <shortname>.html> <out dir>
"""
import html
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("*.html")):
    s = f.read_text(encoding="utf8", errors="replace")
    m = re.search(r'<div class="problembody">(.*?)<div class="attribution|<div class="problembody">(.*)', s, re.S)
    body = (m.group(1) or m.group(2)) if m else s
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"</(p|div|h\d|li|tr|pre)>", "\n", body)
    t = html.unescape(re.sub(r"<[^>]+>", " ", body))
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    (out / (f.stem + ".txt")).write_text(t.strip()[:12000], encoding="utf8")
    print(f.stem, len(t))
