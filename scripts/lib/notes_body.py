"""Render a note's body (a list of strings) to HTML. Used by the note page and by the RSS feed.

A plain string is a paragraph (inline markup from ctx.md). A few prefixes give a note more shape:

    "## A heading"                 h2
    "> A quote"                    blockquote
    "- an item"                    bullet list (consecutive lines group into one list)
    "image:<id> | caption"         a photo from data/images.json (film images keep their credit)
    "video:<youtubeId> | title"    a YouTube embed (the feed gets a link instead)

Everything stays a string so ctx.note() and the feed keep working on any note.
"""
from .core import esc


def _split(s, key):
    rest = s[len(key):]
    a, _, b = rest.partition("|")
    return a.strip(), b.strip()


def render(ctx, body, feed=False):
    from . import components as C  # late import: components imports core and jsonld only
    out, bullets = [], []

    def flush():
        if bullets:
            out.append("<ul>" + "".join(f"<li>{ctx.md(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for raw in body:
        s = raw.strip()
        if s.startswith("- "):
            bullets.append(s[2:])
            continue
        flush()
        if s.startswith("## "):
            out.append(f"<h2>{ctx.md(s[3:])}</h2>")
        elif s.startswith("> "):
            out.append(f"<blockquote><p>{ctx.md(s[2:])}</p></blockquote>")
        elif s.startswith("image:"):
            iid, cap = _split(s, "image:")
            im = ctx.images[iid]
            credit = ctx.credit(iid) if im.get("filmAsset") else ""
            caption = " ".join(x for x in (cap, credit) if x)
            if feed:
                img = f'<img src="{esc(ctx.img_abs(iid, 1280))}" width="{im["width"]}" height="{im["height"]}" alt="{esc(im["alt"])}">'
            else:
                img = ctx.img(iid, sizes="(min-width: 1100px) 760px, 100vw", focal=False)
            fc = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
            out.append(f'<figure class="figure nt-fig">{img}{fc}</figure>')
        elif s.startswith("video:"):
            vid, title = _split(s, "video:")
            v = {"id": vid, "title": title or "Video"}
            if feed:
                out.append(f'<p><a href="https://www.youtube.com/watch?v={esc(vid)}">{esc(v["title"])}</a></p>')
            else:
                out.append(f'<div class="nt-fig">{C.video_embed(ctx, v)}</div>')
        else:
            out.append(f"<p>{ctx.md(s)}</p>")
    flush()
    return "".join(out)
