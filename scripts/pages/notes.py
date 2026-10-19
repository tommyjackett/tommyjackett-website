"""Notes: the journal. Index at /notes/, one page per entry in data/notes.json. See NOTES-HOWTO.md in the repo root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cwa  # noqa: E402
from lib import components as C  # noqa: E402
from lib import jsonld, notes_body  # noqa: E402
from lib.core import esc, fmt_date, iso_melbourne  # noqa: E402

INDEX = "/notes/"
TITLE = "Notes | Tommy Jackett"
DESC = "Notes from Tommy Jackett: things I'm working on, trying out and figuring out about video, stories and making films."


def note_path(n):
    return f"/notes/{n['slug']}/"


def index(ctx, notes):
    trail = [("Notes", None)]
    head = f'''<section class="page-head wrap nt-index-head">
  {C.breadcrumbs_html(ctx, trail)}
  <h1 class="display">Notes</h1>
  <p class="page-lede reveal">Things I'm working on, trying out and figuring out. Rough on purpose.</p>
</section>'''
    if not notes:
        body = '<div class="wrap"><p class="nt-empty">Nothing here yet. Check back soon.</p></div>'
    else:
        first, rest = notes[0], notes[1:]
        fi = first.get("image")
        fig = ""
        if fi:
            fig = (f'<figure class="nt-lead-fig">{ctx.img(fi, sizes="(min-width: 900px) 56vw, 100vw", focal=True)}'
                   f'<figcaption class="small">{esc(ctx.credit(fi)) if ctx.images[fi].get("filmAsset") else ""}</figcaption></figure>')
        lead = f'''<article class="nt-lead reveal">
  <a class="nt-lead-link" href="{esc(ctx.url(note_path(first)))}" tabindex="-1" aria-hidden="true">{fig}</a>
  <div class="nt-lead-text">
    <p class="nt-date"><time datetime="{esc(first["date"])}">{esc(fmt_date(first["date"]))}</time></p>
    <h2 class="nt-lead-title"><a href="{esc(ctx.url(note_path(first)))}">{esc(first["title"])}</a></h2>
    <p class="nt-sum">{ctx.md(first["summary"])}</p>
    <p>{C.link_go(ctx, "Read the note", note_path(first))}</p>
  </div>
</article>'''
        rows = "".join(f'''<li class="nt-row reveal"><p class="nt-date"><time datetime="{esc(n["date"])}">{esc(fmt_date(n["date"]))}</time></p>
  <h2 class="nt-title"><a href="{esc(ctx.url(note_path(n)))}">{esc(n["title"])}</a></h2>
  <p class="nt-sum">{ctx.md(n["summary"])}</p></li>''' for n in rest)
        older = f'<ul class="nt-list">{rows}</ul>' if rows else ""
        body = f'<div class="wrap">{lead}{older}</div>'
    feed = f'<div class="wrap nt-feed reveal"><p>{C.link_go(ctx, "Follow along with the RSS feed", "/feed.xml")}</p></div>'
    graph = [jsonld.website(ctx), jsonld.person(ctx),
             jsonld.collection_page(ctx, "Notes", INDEX, DESC, [note_path(n) for n in notes]),
             jsonld.breadcrumb(ctx, trail)]
    ctx.add_page(INDEX, TITLE, DESC, "\n".join([head, body, feed]),
                 og_image=ctx.site["images"]["ogFilm"] if not notes or not notes[0].get("image") else notes[0]["image"],
                 og_alt=(notes[0].get("imageAlt") if notes else None),
                 jsonld=graph, body_class="p-notes", lastmod=notes[0]["date"] if notes else None)


def post(ctx, n, newer, older):
    path = note_path(n)
    trail = [("Notes", INDEX), (n["title"], None)]
    pub = n["date"]
    mod = n.get("updated") or n["date"]
    pub_iso, mod_iso = iso_melbourne(pub), iso_melbourne(mod)
    img = n.get("image")
    fig = ""
    if img:
        cap = ctx.credit(img) if ctx.images[img].get("filmAsset") else ""
        fig = (f'<div class="wrap"><figure class="nt-hero reveal">{ctx.img(img, sizes="(min-width: 1440px) 1300px, 100vw", priority=True, focal=False)}'
               f'<figcaption class="small">{esc(cap)}</figcaption></figure></div>')
    updated = f' <span class="nt-upd">Updated <time datetime="{esc(mod)}">{esc(fmt_date(mod))}</time></span>' if n.get("updated") else ""
    head = f'''<header class="page-head wrap nt-head">
  {C.breadcrumbs_html(ctx, trail)}
  <h1 class="display nt-h1">{esc(n["title"])}</h1>
</header>'''
    meta = f'''<aside class="nt-meta" aria-label="About this note">
    <p class="byline">By <a href="{esc(ctx.url("/about/"))}">Tommy Jackett</a></p>
    <p class="byline">Published <time datetime="{esc(pub)}">{esc(fmt_date(pub))}</time>{updated}</p>
  </aside>'''
    btns = "".join(C.btn(ctx, b["label"], b["url"], "primary" if b.get("primary") else "ghost") for b in n.get("buttons", []))
    btnrow = f'<div class="btn-row nt-btns">{btns}</div>' if btns else ""
    nav = []
    if newer:
        nav.append(f'<li><span class="small">Newer</span>{C.link_go(ctx, newer["title"], note_path(newer))}</li>')
    if older:
        nav.append(f'<li><span class="small">Older</span>{C.link_go(ctx, older["title"], note_path(older))}</li>')
    nav.append(f'<li>{C.link_go(ctx, "All notes", INDEX)}</li>')
    bodyhtml = notes_body.render(ctx, n["body"])
    article = f'''<article class="wrap nt-wrap">
  {meta}
  <div class="nt-body">{bodyhtml}{btnrow}</div>
</article>
<nav class="wrap nt-nav" aria-label="More notes"><ul>{"".join(nav)}</ul></nav>'''

    desc = n["metaDescription"]
    if n.get("socialImage"):
        og = n["socialImage"]
    else:
        og = img or ctx.site["images"]["ogFilm"]
    image_abs = ctx.abs("/img/" + n["socialImage"]) if n.get("socialImage") else ctx.img_abs(og, 1280)
    graph = [jsonld.website(ctx), jsonld.person(ctx),
             jsonld.article(ctx, path, n["title"], desc, image_abs, pub_iso, mod_iso),
             jsonld.breadcrumb(ctx, trail)]
    ctx.add_page(path, n["metaTitle"], desc, "\n".join([head, fig, article]),
                 og_image=og, og_alt=n.get("imageAlt"), og_type="article",
                 article={"published": pub_iso, "modified": mod_iso},
                 jsonld=graph, body_class="p-note", lastmod=mod)


def build(ctx):
    notes = [ctx.note(n) for n in ctx.notes]  # newest first, after-launch wording applied
    index(ctx, notes)
    for i, n in enumerate(notes):
        post(ctx, n, notes[i - 1] if i > 0 else None, notes[i + 1] if i + 1 < len(notes) else None)
