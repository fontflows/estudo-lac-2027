"""Extract text of a contest/editorial PDF with PyMuPDF (compact, blank lines removed).
Usage: python -I pdf_to_text_latam.py <in.pdf> <out.txt>"""
import re, sys
import fitz
doc = fitz.open(sys.argv[1])
s = "\n".join(p.get_text() for p in doc)
s = re.sub(r"ICPC Latin American Regional . \d{4}\s*\n\s*\d+\s*\n", "", s)
s = re.sub(r"\n\s*\n+", "\n", s)
open(sys.argv[2], "w", encoding="utf-8").write(s)
print(sys.argv[1], len(s))
