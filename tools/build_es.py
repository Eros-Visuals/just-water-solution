#!/usr/bin/env python3
"""Build the Spanish page (es/index.html) from the English page (index.html).

    python3 tools/build_es.py

index.html is the only page anyone edits. This script copies it to es/index.html with every
visible string, alt text, aria-label, placeholder and meta description swapped for its Spanish
version from tools/es.json, the asset paths pointed one folder up, and the EN / ES switch flipped.

It refuses to write the page when an English string has no Spanish entry, and prints the missing
ones, so an English edit can never ship a half-English Spanish page. Add the new strings to
tools/es.json (Latin American Spanish, "usted") and run it again.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from i18n_extract import strings, has_words  # noqa: E402

SKIP = re.compile(r'(<(script|style|svg)\b.*?</\2>)', re.S)
ATTR = re.compile(r'\b(alt|aria-label|placeholder)="([^"]+)"')
META = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description)") content=")([^"]+)(")')
TEXT = re.compile(r'>([^<]+)<')

EN_SWITCH = ('<a href="./" class="is-active" aria-current="true" hreflang="en" lang="en" data-lang="en">EN</a>'
             '<a href="es/" hreflang="es" lang="es" data-lang="es">ES</a>')
ES_SWITCH = ('<a href="../" hreflang="en" lang="en" data-lang="en">EN</a>'
             '<a href="./" class="is-active" aria-current="true" hreflang="es" lang="es" data-lang="es">ES</a>')
EN_PREF = "if(localStorage.getItem('jws-lang')==='es')location.replace('es/'+location.hash)"
ES_PREF = "if(localStorage.getItem('jws-lang')==='en')location.replace('../'+location.hash)"


def main():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    es = json.load(open(os.path.join(HERE, 'es.json'), encoding='utf-8'))

    missing = [s for s in strings(src) if s not in es]
    if missing:
        print('Missing Spanish for %d string(s); add them to tools/es.json:' % len(missing))
        for s in missing:
            print('  ' + json.dumps(s, ensure_ascii=False))
        sys.exit(1)

    def text_sub(m):
        raw = m.group(1); t = raw.strip()
        if not t or not has_words(t):
            return m.group(0)
        lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
        return '>' + lead + es[t] + trail + '<'

    # SKIP.split returns [text, block, tagname, text, block, tagname, ...]
    parts = SKIP.split(src)
    rebuilt = []
    for k, chunk in enumerate(parts):
        if k % 3 == 0:
            # next to an inline <svg> block a chunk starts or ends mid-content: give the text its '>' / '<' back
            pre = '>' if k else ''
            post = '<' if k + 1 < len(parts) else ''
            chunk = TEXT.sub(text_sub, pre + chunk + post)
            chunk = chunk[len(pre):len(chunk) - len(post)]
            chunk = ATTR.sub(lambda m: '%s="%s"' % (m.group(1), es.get(m.group(2), m.group(2))), chunk)
            chunk = META.sub(lambda m: m.group(1) + es[m.group(2)] + m.group(3), chunk)
            rebuilt.append(chunk)
        elif k % 3 == 1:
            block = chunk
            if 'application/ld+json' in block:
                for key in ('description', 'areaServed'):
                    block = re.sub(r'("%s": ")([^"]+)(")' % key, lambda m: m.group(1) + es.get(m.group(2), m.group(2)) + m.group(3), block)
            rebuilt.append(block)
        # k % 3 == 2 is the captured tag name, already inside the block
    html = ''.join(rebuilt)

    html = html.replace('<html lang="en">', '<html lang="es">', 1)
    # the Spanish page is its own canonical URL; the hreflang alternates stay the same on both pages
    for tag in ('<meta property="og:url" content="https://justwatersolution.com/">',
                '<link rel="canonical" href="https://justwatersolution.com/">'):
        assert tag in html, tag
        html = html.replace(tag, tag.replace('justwatersolution.com/"', 'justwatersolution.com/es/"'))
    assert EN_SWITCH in html and EN_PREF in html, 'language switch or preference script changed in index.html'
    html = html.replace(EN_SWITCH, ES_SWITCH).replace(EN_PREF, ES_PREF)
    for a in ('src="img/', 'data-full="img/', 'content="img/', 'href="assets/', 'src="assets/', '"image": "img/'):
        html = html.replace(a, a.replace('img/', '../img/').replace('assets/', '../assets/'))

    # nothing English may survive outside the allowed names
    keep = {k for k, v in es.items() if k == v}
    leftover = [s for s in strings(html) if s in es and s not in keep]
    if leftover:
        print('Still English after the build:', leftover)
        sys.exit(1)

    os.makedirs(os.path.join(ROOT, 'es'), exist_ok=True)
    open(os.path.join(ROOT, 'es', 'index.html'), 'w', encoding='utf-8').write(html)
    print('es/index.html written: %d strings translated' % len(strings(src)))


if __name__ == '__main__':
    main()
