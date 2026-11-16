"""Split a pdftotext dump of an ICPC problem set into problems and print a compact view.

Usage: python -I split_statements.py <contest.txt> [maxchars_story] [letters]
Prints, per problem: title, the start of the story (up to maxchars), and the Input section.
"""
import re
import sys


def split(txt):
    parts = re.split(r'\n\s*Problem ([A-Z]) - ([^\n]+)\n', txt)
    out = {}
    for i in range(1, len(parts) - 2, 3):
        L, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        if L in out:  # repeated page headers
            out[L]['body'] += body
        else:
            out[L] = {'title': title, 'body': body}
    return out


def main():
    txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    only = sys.argv[3] if len(sys.argv) > 3 else None
    for L, p in split(txt).items():
        if only and L not in only:
            continue
        body = re.sub(r'[ \t]+', ' ', p['body'])
        body = re.sub(r'\n\s*\n+', '\n', body)
        m = re.search(r'\nInput\n(.*?)\nOutput\n(.*?)(\nSample|\Z)', body, re.S)
        story = body[:m.start()] if m else body
        print(f"##### {L} - {p['title']}")
        print(story[:mx].strip())
        if m:
            print('-- INPUT:', m.group(1).strip()[:900])
            print('-- OUTPUT:', m.group(2).strip()[:400])
        print()


if __name__ == '__main__':
    main()
