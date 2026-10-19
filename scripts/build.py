#!/usr/bin/env python3
"""Build the tommyjackett.com static site into public/.

    python3 scripts/build.py                 staging build (sub-path, noindex, robots Disallow all)
    python3 scripts/build.py --root          root-domain build (indexing on, CNAME, sitemap, llms.txt)
    python3 scripts/build.py --machine       staging build that also writes sitemap.xml and llms.txt (for testing them)
    python3 scripts/build.py --state after   force the after-launch wording (default: decided by the clock)
    python3 scripts/build.py --base-path /x --site-url https://example.com/x     override the target

Dependency-free. Reads data/*.json and src/, calls every module in scripts/pages/, writes public/.
"""
import argparse
import importlib.util
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import checks, components, machine  # noqa: E402
from lib.core import ROOT, Ctx  # noqa: E402


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    return css.strip() + "\n"


def bundle(src_dir, main, ext):
    parts = [os.path.join(src_dir, main)]
    pages = os.path.join(src_dir, "pages")
    if os.path.isdir(pages):
        parts += sorted(os.path.join(pages, f) for f in os.listdir(pages) if f.endswith(ext))
    return "\n".join(open(p, encoding="utf-8").read() for p in parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="store_true", help="root-domain build (go-live)")
    ap.add_argument("--machine", action="store_true", help="write sitemap.xml and llms.txt on staging too")
    ap.add_argument("--base-path", default=None)
    ap.add_argument("--site-url", default=None)
    ap.add_argument("--out", default="public")
    ap.add_argument("--state", choices=["before", "after"], default=None)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args()

    ctx = Ctx(production=a.root, base_path=a.base_path, site_url=a.site_url, out=a.out, machine=a.machine, state=a.state)
    out = ctx.out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    # bundles first, so page links carry a content hash for cache busting
    css_text = minify_css(bundle(os.path.join(ROOT, "src", "css"), "site.css", ".css"))
    js_text = bundle(os.path.join(ROOT, "src", "js"), "site.js", ".js")
    import hashlib
    ctx.versions = {"site.css": hashlib.md5(css_text.encode()).hexdigest()[:8], "site.js": hashlib.md5(js_text.encode()).hexdigest()[:8]}

    # page modules
    pdir = os.path.join(ROOT, "scripts", "pages")
    for fn in sorted(os.listdir(pdir)):
        if fn.endswith(".py") and not fn.startswith("_"):
            spec = importlib.util.spec_from_file_location("page_" + fn[:-3], os.path.join(pdir, fn))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.build(ctx)

    # render and write pages
    rendered = {}
    for p in ctx.pages:
        html = components.render_page(ctx, p)
        rendered[p["path"]] = html
        dest = os.path.join(out, p["path"].lstrip("/"))
        if p["path"].endswith("/"):
            dest = os.path.join(dest, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html)

    # static assets
    shutil.copytree(os.path.join(ROOT, "src", "fonts"), os.path.join(out, "fonts"), ignore=shutil.ignore_patterns("*.md"))
    shutil.copytree(os.path.join(ROOT, "src", "img"), os.path.join(out, "img"))
    if os.path.isdir(os.path.join(ROOT, "src", "icons")):
        shutil.copytree(os.path.join(ROOT, "src", "icons"), os.path.join(out, "icons"))
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    with open(os.path.join(out, "assets", "site.css"), "w", encoding="utf-8") as f:
        f.write(css_text)
    with open(os.path.join(out, "assets", "site.js"), "w", encoding="utf-8") as f:
        f.write(js_text)

    # machine files
    machine.write(os.path.join(out, "robots.txt"), machine.robots(ctx))
    machine.write(os.path.join(out, "feed.xml"), machine.feed(ctx))
    machine.write(os.path.join(out, ".nojekyll"), "")
    if ctx.machine_files:
        machine.write(os.path.join(out, "sitemap.xml"), machine.sitemap(ctx))
        machine.write(os.path.join(out, "llms.txt"), machine.llms(ctx))
    if ctx.production:
        machine.write(os.path.join(out, "CNAME"), "tommyjackett.com\n")
        rb = open(os.path.join(out, "robots.txt")).read()
        if "Disallow: /" in rb:
            print("ERROR: production robots.txt disallows everything")
            sys.exit(1)

    errors, warnings = checks.run(ctx, rendered)
    mode = "ROOT (go-live)" if ctx.production else "STAGING"
    print(f"Built {len(ctx.pages)} pages [{mode}] base_path={ctx.base_path or '(none)'} site_url={ctx.site_url} launch_state={'after' if ctx.is_live else 'before'}")
    for w in warnings:
        print("  warn:", w)
    for e in errors:
        print("  ERROR:", e)
    if errors or (a.strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
