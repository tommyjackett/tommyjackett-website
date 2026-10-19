#!/usr/bin/env python3
"""Check every external link in public/ (HEAD then GET, browser user agent, threaded).

    python3 scripts/check_links.py            checks the built site in public/
Prints OK / BLOCKED / FAIL per URL. BLOCKED means the site refuses scripts (IMDb 202, Facebook 400, LinkedIn 999,
Instagram login walls): look at those in a browser once. Internal links are checked by scripts/build.py itself.
"""
import concurrent.futures
import os
import re
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SKIP = ("fonts.googleapis", "schema.org", "w3.org", "purl.org", "sitemaps.org", "ogp.me")


def urls():
    found = {}
    for dp, _, fn in os.walk(os.path.join(ROOT, "public")):
        for f in fn:
            if f.endswith((".html", ".xml", ".txt")):
                txt = open(os.path.join(dp, f), encoding="utf-8").read()
                for m in re.finditer(r'https?://[^\s"\'<>)\]]+', txt):
                    u = m.group(0).rstrip(".,;")
                    if not any(s in u for s in SKIP) and "tommyjackett.github.io" not in u and "tommyjackett.com" not in u:
                        found.setdefault(u, set()).add(os.path.relpath(os.path.join(dp, f), os.path.join(ROOT, "public")))
    return found


def check(u):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(u, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return u, r.status
        except urllib.error.HTTPError as e:
            code = e.code
            if method == "GET":
                return u, code
        except Exception as e:  # noqa: BLE001
            if method == "GET":
                return u, str(e)[:60]
    return u, "?"


def main():
    found = urls()
    bad = 0
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for u, code in sorted(ex.map(check, sorted(found))):
            if isinstance(code, int) and 200 <= code < 400:
                tag = "OK     "
            elif code in (202, 400, 403, 405, 429, 999) or code == 401:
                tag = "BLOCKED"
            else:
                tag = "FAIL   "
                bad += 1
            print(f"{tag} {code}  {u}  ({len(found[u])} page(s))")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
