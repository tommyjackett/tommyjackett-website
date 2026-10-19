"""Stories: the index at /stories/ and one page per story at /stories/<slug>/. Data: data/stories.json.

Every story page shares the same bones (breadcrumb, h1, byline, the story, click-to-play videos, watch links, related
stories) but each `layout` sets the pieces differently so the pages do not read as one template:
  ranch   video first and wide, the Short stands beside the text
  ledger  text with a press column, the four videos laid out as a grid
  stack   two videos stacked on the left, text on the right
  count   one big number, then the video, then the text
  quote   his line set large, text and video side by side
Videos are a lightweight facade: a thumbnail link that loads the youtube-nocookie iframe only on click
(src/js/pages/film-stories.js). Without JS the link goes to YouTube.
Styles: src/css/pages/film-stories.css (.sp-* and .sx-* classes).
"""
import re

from lib import components as C
from lib import jsonld
from lib.core import esc, fmt_date, iso_melbourne

PLAY = ('<svg viewBox="0 0 72 72" width="72" height="72" focusable="false" aria-hidden="true">'
        '<circle cx="36" cy="36" r="34" fill="rgba(14,14,15,.55)" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M29 23.5v25l21-12.5z" fill="currentColor"/></svg>')


# ------------------------------------------------------------------ pieces
def watch_href(v):
    base = "https://www.youtube.com/shorts/" if v.get("short") else "https://www.youtube.com/watch?v="
    return base + v["id"]


def facade(ctx, v, sizes="100vw", tall=False, cap=True, priority=False):
    """Click-to-play video. Thumbnail (or a plain panel when there is none) inside a link to YouTube."""
    label = v.get("label") or ""
    if v.get("thumb"):
        media = ctx.img(v["thumb"], sizes=sizes, alt="", priority=priority)
    else:
        media = f'<span class="vf-blank"><span>{esc(label or "Video")}</span></span>'
    cls = "vf" + (" vf--tall" if tall else "")
    title = v["title"]
    box = (f'<div class="{cls}" data-yt="{esc(v["id"])}" data-title="{esc(title)}">'
           f'<a class="vf-link" href="{esc(watch_href(v))}">{media}'
           f'<span class="vf-play">{PLAY}</span>'
           f'<span class="vh">Play: {esc(title)}</span></a></div>')
    if not cap:
        return box
    lab = f'<span class="vc-label">{esc(label)}</span> ' if label else ""
    c = (f'<p class="vc">{lab}<span class="vc-title">{esc(title)}</span>'
         f'<span class="vc-by">A video by Tommy Jackett. <a href="{esc(watch_href(v))}">Watch on YouTube</a></span></p>')
    return f'<div class="vf-wrap">{box}{c}</div>'


def story_url(st):
    return f"/stories/{st['slug']}/"


def byline(ctx, st):
    pub = fmt_date(st["published"])
    upd = fmt_date(st["updated"])
    about = esc(ctx.url("/about/"))
    return (f'<p class="byline sp-by">By <a href="{about}">Tommy Jackett</a>. '
            f'Published <time datetime="{esc(st["published"])}">{esc(pub)}</time>. '
            f'Updated <time datetime="{esc(st["updated"])}">{esc(upd)}</time>.</p>')


def head(ctx, st, cls=""):
    trail = [("Stories", "/stories/"), (st["title"], None)]
    return (f'<header class="sp-head wrap {cls}">{C.breadcrumbs_html(ctx, trail)}'
            f'<h1 class="display sp-title">{esc(st["title"])}</h1>{byline(ctx, st)}</header>')


def paras(ctx, st, cls="sp-prose"):
    ps = "".join(f"<p>{ctx.md(p)}</p>" for p in st["body"])
    return f'<div class="{cls}">{ps}</div>'


def press_list(ctx, st):
    if not st.get("press"):
        return ""
    lis = []
    for p in st["press"]:
        lis.append(f'<li><a href="{esc(p["url"])}"><strong>{esc(p["outlet"])}</strong>'
                   f'<span>{esc(p["about"])}, {esc(fmt_date(p["date"]))}</span></a></li>')
    return f'<div class="sp-press"><p class="sp-label">In the press</p><ul class="linklist">{"".join(lis)}</ul></div>'


def extra_watch(st):
    """Watch links that are not already a video on the page (the click-to-play captions carry those)."""
    have = {watch_href(v) for v in st["videos"]} | {f"https://www.youtube.com/watch?v={v['id']}" for v in st["videos"]}
    return [w for w in st["watch"] if w["url"] not in have]


def watch_section(ctx, st, n="01"):
    items = extra_watch(st)
    if not items:
        return ""
    lis = "".join(f'<li><a href="{esc(w["url"])}"><strong>{esc(w["label"])}</strong></a></li>' for w in items)
    return (f'<section class="sec sec--tight" aria-label="Watch"><div class="wrap">{C.mark(n, "Also")}'
            f'<ul class="linklist sp-watch reveal">{lis}</ul></div></section>')


def related_section(ctx, st, n="02"):
    rows = []
    for slug in st.get("related", []):
        r = ctx.story(slug)
        if not r:
            continue
        href = esc(ctx.url(ctx.story_href(r)))
        thumb = ""
        if r.get("image"):
            fm = ctx.images[r["image"]].get("filmAsset")
            credit = f'<span class="sx-credit">{esc(ctx.credit(r["image"]))}</span>' if fm else ""
            thumb = f'<div class="sp-rel-img">{ctx.img(r["image"], sizes="(min-width: 900px) 22vw, 40vw", alt="")}{credit}</div>'
        rows.append(f'''<li class="sp-rel-row reveal">{thumb}<div class="sp-rel-text"><span class="story-y">{esc(r["year"])}</span>
  <h3 class="sp-rel-t"><a href="{href}">{esc(r["listTitle"])}</a></h3><p>{ctx.md(r["indexLine"])}</p></div></li>''')
    if not rows:
        return ""
    return (f'<section class="sec sec--tight band" aria-label="More stories"><div class="wrap">{C.mark(n, "More stories")}'
            f'<ul class="sp-rel">{"".join(rows)}</ul>'
            f'<p class="all-link reveal">{C.link_go(ctx, "All stories", "/stories/")}</p></div></section>')


# ------------------------------------------------------------------ layouts
def lay_ranch(ctx, st):
    p1, p2 = st["videos"][0], st["videos"][1]
    return f'''{head(ctx, st)}
<section class="wrap sp-ranch-top reveal">{facade(ctx, p1, sizes="(min-width: 1400px) 1400px, 100vw", priority=True)}</section>
<section class="sec sec--tight"><div class="wrap sp-ranch-cols">
  {paras(ctx, st, "sp-prose sp-prose--open")}
  <aside class="sp-short reveal" aria-label="Part 2, a YouTube Short">{facade(ctx, p2, tall=True)}</aside>
</div></section>
{watch_section(ctx, st)}'''


def lay_ledger(ctx, st):
    vids = "".join(f'<li class="reveal" style="--d:{.06 * i:.2f}s">{facade(ctx, v, sizes="(min-width: 900px) 44vw, 100vw")}</li>'
                   for i, v in enumerate(st["videos"]))
    return f'''{head(ctx, st)}
<section class="sec sec--tight"><div class="wrap sp-ledger">
  {paras(ctx, st, "sp-prose sp-prose--open")}
  {press_list(ctx, st)}
</div></section>
<section class="sec sec--tight" aria-label="The videos"><div class="wrap">{C.mark("01", "The videos")}
  <ul class="sp-grid">{vids}</ul></div></section>
{watch_section(ctx, st, "02")}'''


def lay_stack(ctx, st):
    vids = "".join(f'<div class="reveal" style="--d:{.08 * i:.2f}s">{facade(ctx, v, sizes="(min-width: 900px) 46vw, 100vw")}</div>'
                   for i, v in enumerate(st["videos"]))
    return f'''{head(ctx, st)}
<section class="sec sec--tight"><div class="wrap sp-stack">
  {paras(ctx, st, "sp-prose sp-prose--open")}
  <div class="sp-stack-vids">{vids}</div>
</div></section>
{watch_section(ctx, st)}'''


def lay_count(ctx, st):
    v1, v2 = st["videos"][0], st["videos"][1]
    quote = st.get("pullQuote", "")
    body = st["body"]
    return f'''{head(ctx, st)}
<section class="wrap sp-count" aria-label="The count">
  <p class="sp-count-n display reveal">53</p>
  <div class="sp-count-t reveal"><p class="lead">slices of pepperoni, counted on camera. The promise was 100.</p></div>
</section>
<section class="wrap sp-count-vid reveal">{facade(ctx, v1, sizes="(min-width: 1100px) 1000px, 100vw")}</section>
<section class="sec sec--tight"><div class="wrap sp-count-cols">
  <div class="sp-prose sp-prose--open">{"".join(f"<p>{ctx.md(p)}</p>" for p in body[:2])}</div>
  <blockquote class="sp-pull reveal"><p>"{esc(quote)}"</p></blockquote>
</div></section>
<section class="sec sec--tight band"><div class="wrap sp-count-cols sp-count-2">
  <div class="sp-prose">{"".join(f"<p>{ctx.md(p)}</p>" for p in body[2:])}{press_list(ctx, st)}</div>
  <div class="reveal">{facade(ctx, v2, sizes="(min-width: 900px) 40vw, 100vw")}</div>
</div></section>
{watch_section(ctx, st)}'''


def lay_quote(ctx, st):
    v = st["videos"][0]
    quote = st.get("pullQuote", "")
    return f'''{head(ctx, st)}
<section class="wrap sp-quote" aria-label="The idea">
  <blockquote class="sp-bigq reveal"><p>"{esc(quote)}"</p></blockquote>
</section>
<section class="sec sec--tight"><div class="wrap sp-quote-cols">
  {paras(ctx, st, "sp-prose sp-prose--open")}
  <div class="sp-quote-vid reveal">{facade(ctx, v, sizes="(min-width: 900px) 40vw, 100vw")}</div>
</div></section>
{watch_section(ctx, st)}'''


def lay_plain(ctx, st):
    vids = "".join(f'<div class="reveal">{facade(ctx, v, sizes="(min-width: 900px) 60vw, 100vw")}</div>' for v in st["videos"])
    return f'{head(ctx, st)}<section class="sec sec--tight"><div class="wrap">{paras(ctx, st)}{vids}</div></section>{watch_section(ctx, st)}'


LAYOUTS = {"ranch": lay_ranch, "ledger": lay_ledger, "stack": lay_stack, "count": lay_count, "quote": lay_quote}


# ------------------------------------------------------------------ story page
def story_page(ctx, st):
    path = story_url(st)
    n_rel = (1 if st.get("layout") == "ledger" else 0) + (1 if extra_watch(st) else 0)
    body = LAYOUTS.get(st.get("layout"), lay_plain)(ctx, st) + related_section(ctx, st, f"{n_rel + 1:02d}")
    desc = st["metaDescription"]
    social = ctx.images[st["image"]].get("social") if st.get("image") else None
    image_abs = ctx.abs("/img/" + social) if social else ctx.img_abs(st["image"], 1280)
    trail = [("Stories", "/stories/"), (st["title"], None)]
    graph = [
        jsonld.person(ctx),
        jsonld.web_page(ctx, path, st["title"], desc),
        jsonld.article(ctx, path, st["title"], desc, image_abs,
                       iso_melbourne(st["published"]), iso_melbourne(st["updated"])),
    ]
    for i, v in enumerate(st["videos"], 1):
        graph.append(jsonld.video_object(ctx, v, path, slug=str(i)))
    graph.append(jsonld.breadcrumb(ctx, trail))
    og = social or st["image"]
    ctx.add_page(path, st["metaTitle"], desc, body, og_image=og,
                 og_alt=ctx.images[st["image"]]["alt"] if st.get("image") else None,
                 og_type="article", jsonld=graph, body_class=f"story-page story-{st.get('layout', 'plain')}",
                 article={"published": iso_melbourne(st["published"]), "modified": iso_melbourne(st["updated"])},
                 lastmod=st["updated"])


# ------------------------------------------------------------------ index
def index_page(ctx):
    live = sorted([s for s in ctx.stories if s.get("status", "live") == "live"], key=lambda s: s["order"])
    film = next((s for s in live if s.get("isFilm")), None)
    others = [s for s in live if not s.get("isFilm")]
    feature = ""
    if film:
        img = ctx.img(film["image"], sizes="(min-width: 900px) 62vw, 100vw", focal=False, priority=True)
        feature = f'''<section class="sx-feature"><div class="wrap sx-feature-grid">
  <figure class="figure sx-feature-art">{img}<figcaption class="small">{esc(ctx.credit(film["image"]))}</figcaption></figure>
  <div class="sx-feature-text"><span class="story-y">{esc(film["year"])}</span>
    <h2 class="sx-t">{esc(film["listTitle"])}</h2><p class="sx-l">{ctx.md(film["indexLine"])}</p>
    <p>{C.link_go(ctx, film["readLabel"], ctx.story_href(film), cls="link link-go sx-go")}</p></div>
</div></section>'''
    rows = []
    for i, st in enumerate(others):
        img = ""
        if st.get("image"):
            img = f'<div class="sx-img">{ctx.img(st["image"], sizes="(min-width: 900px) 34vw, 100vw", alt="")}</div>'
        rows.append(f'''<li class="sx-row reveal"><div class="sx-text"><span class="story-y">{esc(st["year"])}</span>
  <h2 class="sx-t"><a href="{esc(ctx.url(ctx.story_href(st)))}">{esc(st["listTitle"])}</a></h2>
  <p class="sx-l">{ctx.md(st["indexLine"])}</p>
  <span class="sx-go link-go" aria-hidden="true">{esc(st["readLabel"])}</span></div>{img}</li>''')
    yt = ctx.a("tj-youtube", "Go to my YouTube channel", cls="link link-go")
    content = f'''<header class="page-head wrap sx-head">{C.breadcrumbs_html(ctx, [("Stories", None)])}
  <h1 class="display sx-h1">Stories</h1>
  <p class="page-lede">I make videos that start with something I can't leave alone. These are the ones I'd point you to, newest first.</p>
</header>
{feature}
<section class="sec sec--tight" aria-label="All stories"><div class="wrap">
  <ol class="sx-list">{"".join(rows)}</ol>
  <p class="sx-end reveal">Older videos, and everything else, are on my YouTube channel. {yt}</p>
</div></section>'''
    title = "Stories by Tommy Jackett: videos and how they happened"
    desc = ("The videos I've made, the ones that took off and how each one came together, "
            "from the oBike fishing video to the Jackett Ranch.")
    paths = [ctx.story_href(s) for s in live]
    graph = [jsonld.person(ctx), jsonld.collection_page(ctx, "Stories by Tommy Jackett", "/stories/", desc, paths),
             jsonld.breadcrumb(ctx, [("Stories", None)])]
    ctx.add_page("/stories/", title, desc, content, og_image=ctx.site["images"]["ogFilm"],
                 og_alt="In Guns We Trust key art with Tommy Jackett and Josh Janssen on a map of the United States",
                 jsonld=graph, body_class="stories-index", lastmod="2026-10-20")


def build(ctx):
    index_page(ctx)
    for st in ctx.stories:
        if st.get("isFilm") or st.get("status", "live") != "live":
            continue
        story_page(ctx, st)
