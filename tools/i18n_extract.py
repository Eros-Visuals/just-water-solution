#!/usr/bin/env python3
"""List every translatable string in index.html (text between tags and the alt / aria-label /
placeholder / meta content attributes). Shared by build_es.py so both see the same strings."""
import re, sys, json

SKIP_BLOCKS = re.compile(r'<(script|style|svg)\b.*?</\1>', re.S)
ATTRS = re.compile(r'\b(alt|aria-label|placeholder)="([^"]+)"')
META = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description)") content=")([^"]+)(")')
TEXT = re.compile(r'>([^<]+)<')


def has_words(s):
    return re.search(r'[A-Za-z]{2,}', s) is not None


def strings(html):
    out = []
    body = SKIP_BLOCKS.sub(lambda m: '<' + m.group(1) + '></' + m.group(1) + '>', html)
    for m in TEXT.finditer(body):
        t = m.group(1).strip()
        if t and has_words(t):
            out.append(t)
    for m in ATTRS.finditer(html):
        if has_words(m.group(2)):
            out.append(m.group(2))
    for m in META.finditer(html):
        out.append(m.group(2))
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); uniq.append(s)
    return uniq


if __name__ == '__main__':
    html = open(sys.argv[1] if len(sys.argv) > 1 else 'index.html', encoding='utf-8').read()
    print(json.dumps(strings(html), ensure_ascii=False, indent=1))
