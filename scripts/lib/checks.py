"""Build-time checks. Returns (errors, warnings). Errors make the build exit non-zero."""
import os
import re

from .core import ROOT

EM = chr(0x2014)


def run(ctx, rendered):
    """rendered: {path: html}. Checks content rules, SEO rules and internal links."""
    errors, warnings = [], list(ctx.warnings)
    titles, descs, pending = {}, {}, {}
    out = ctx.out
    for path, html in rendered.items():
        is404 = path.endswith("404.html")
        t = re.search(r"<title>(.*?)</title>", html, re.S)
        d = re.search(r'<meta name="description" content="(.*?)">', html)
        if not is404:
            if not t:
                errors.append(f"{path}: no title")
            else:
                if t.group(1) in titles:
                    errors.append(f"{path}: duplicate title with {titles[t.group(1)]}")
                titles[t.group(1)] = path
                if len(t.group(1)) > 70:
                    warnings.append(f"{path}: title is {len(t.group(1))} chars")
            if not d:
                errors.append(f"{path}: no meta description")
            else:
                if d.group(1) in descs:
                    errors.append(f"{path}: duplicate description with {descs[d.group(1)]}")
                descs[d.group(1)] = path
                if not 70 <= len(d.group(1)) <= 160:
                    warnings.append(f"{path}: description is {len(d.group(1))} chars")
            if not re.search(r'<link rel="canonical"', html):
                errors.append(f"{path}: no canonical")
        h1s = len(re.findall(r"<h1[\s>]", html))
        if h1s != 1:
            errors.append(f"{path}: {h1s} h1 elements (want 1)")
        if EM in html:
            errors.append(f"{path}: contains an em dash")
        if re.search(r"\bCracks\b", re.sub(r"<[^>]+>", " ", html)):
            errors.append(f"{path}: contains the word 'Cracks'")
        if ctx.production:
            if "noindex" in html and not is404:
                errors.append(f"{path}: noindex in a production build")
            if "[[" in html:
                errors.append(f"{path}: unresolved [[gap]] in a production build")
        else:
            if "noindex" not in html:
                errors.append(f"{path}: staging page without noindex")
            if "[[" in html:
                warnings.append(f"{path}: unresolved [[gap]] (shown highlighted on staging)")
        # images without alt, sizes
        for m in re.finditer(r"<img\b[^>]*>", html):
            tag = m.group(0)
            if " alt=" not in tag:
                errors.append(f"{path}: img without alt")
            if " width=" not in tag or " height=" not in tag:
                warnings.append(f"{path}: img without width/height")
        # internal links and assets (srcset entries included)
        refs = [m.group(1) for m in re.finditer(r'(?:href|src)="([^"]+)"', html)]
        for m in re.finditer(r'(?:srcset|imagesrcset)="([^"]+)"', html):
            refs += [c.strip().split(" ")[0] for c in m.group(1).split(",")]
        for u in refs:
            if re.match(r"^(https?:|mailto:|tel:|data:)", u):
                continue
            if u.startswith("#"):
                if u != "#" and f'id="{u[1:]}"' not in html:
                    errors.append(f"{path}: dead anchor {u}")
                continue
            u = u.split("#")[0].split("?")[0]
            if ctx.base_path and not u.startswith(ctx.base_path + "/") and u != ctx.base_path:
                errors.append(f"{path}: internal link without BASE_PATH: {u}")
                continue
            rel = u[len(ctx.base_path):] if ctx.base_path else u
            fs = os.path.join(out, rel.lstrip("/"))
            if rel.endswith("/"):
                fs = os.path.join(fs, "index.html")
            if not os.path.exists(fs):
                known = {n["path"] for n in ctx.site["nav"]} | {i["path"] for i in ctx.site["footer"]["map"]}
                if rel in known or rel.startswith(("/stories/", "/notes/", "/sitemap", "/llms")):
                    pending.setdefault(u, set()).add(path)
                else:
                    errors.append(f"{path}: link target not built: {u}")
    for u, pgs in sorted(pending.items()):
        warnings.append(f"not built yet: {u} (linked from {len(pgs)} page(s))")
    # source hygiene: no em dashes in the repo's own files
    for base in ("data", "scripts", "src/css", "src/js", "src/layout.html", "README.md"):
        full = os.path.join(ROOT, base)
        files = []
        if os.path.isdir(full):
            for dp, _, fn in os.walk(full):
                files += [os.path.join(dp, f) for f in fn if f.endswith((".py", ".json", ".css", ".js", ".md", ".html"))]
        elif os.path.exists(full):
            files = [full]
        for f in files:
            try:
                if EM in open(f, encoding="utf-8").read():
                    errors.append(f"source file contains an em dash: {os.path.relpath(f, ROOT)}")
            except Exception:
                pass
    return errors, warnings
