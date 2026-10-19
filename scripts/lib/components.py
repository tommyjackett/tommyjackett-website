"""Shared HTML pieces: layout render, header, footer, buttons, embeds, forms. Pages import from here."""
import os
import re

from . import jsonld
from .core import ROOT, esc, typo_html

LAYOUT = None


def _layout():
    global LAYOUT
    if LAYOUT is None:
        with open(os.path.join(ROOT, "src", "layout.html"), encoding="utf-8") as f:
            LAYOUT = f.read()
    return LAYOUT


def fill(tpl, **kw):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: kw.get(m.group(1), ""), tpl)


# ------------------------------------------------------------------ small pieces
def btn(ctx, label, target, kind="primary", extra=""):
    """kind: 'primary' (solid) or 'ghost'. target resolved by ctx.resolve (film:watch, link:id, /path/, url)."""
    cls = "btn" + (" btn--ghost" if kind == "ghost" else "")
    return f'<a class="{cls}" href="{esc(ctx.resolve(target))}"{(" " + extra) if extra else ""}>{esc(label)}</a>'


def link_go(ctx, label, target, cls="link link-go"):
    return f'<a class="{cls}" href="{esc(ctx.resolve(target))}">{esc(label)}</a>'


def mark(n, text):
    return f'<p class="mark reveal"><span class="mark-n">{esc(n)}</span><span class="mark-t">{esc(text)}</span></p>'


def film_notice(ctx, inline=True):
    f = ctx.site["film"]
    return f"{f['contentNote']} {f['supportInline'] if inline else f['support']}"


def breadcrumbs_html(ctx, trail):
    """trail: [(name, path_or_None)] after the root. Visible breadcrumb; pair with jsonld.breadcrumb(ctx, trail)."""
    items = [("Tommy Jackett", "/")] + list(trail)
    lis = []
    for i, (name, path) in enumerate(items):
        if path and i < len(items) - 1:
            lis.append(f'<li><a href="{esc(ctx.url(path))}">{esc(name)}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{esc(name)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def video_embed(ctx, v, cap=True):
    """YouTube embed on the nocookie domain with the site's standard no-branding parameter set."""
    params = "autoplay=0&rel=0&modestbranding=1&iv_load_policy=3&playsinline=1&color=white"
    src = f"https://www.youtube-nocookie.com/embed/{v['id']}?{params}"
    title = f"{v['title']}, a video by Tommy Jackett"
    watch = f"https://www.youtube.com/watch?v={v['id']}"
    c = f'<p class="video-cap"><a href="{watch}">Watch on YouTube</a></p>' if cap else ""
    return (f'<div class="video-wrap"><div class="video"><iframe src="{src}" title="{esc(title)}" loading="lazy" '
            f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>{c}</div>')


def contact_form(ctx, redirect_path="/contact/"):
    """The contact form per data/form.json. Without site.formAccessKey it returns the email-only state."""
    s = ctx.site
    email = s["email"]
    key = s.get("formAccessKey", "")
    mailto = f'<a href="mailto:{esc(email)}">{esc(email)}</a>'
    if not key:
        return f'<p class="form-msg-static">The easiest way to reach me is email. {mailto}</p>'
    opts = ["Video or podcast production", "Hosting a screening of In Guns We Trust", "Press or interview", "Speaking or a collab", "Just saying hi"]
    options = "".join(f'<option>{esc(o)}</option>' for o in opts)
    return f'''<form class="form" method="post" action="https://api.web3forms.com/submit" data-enhance
  data-ok="Got it, thanks. I'll get back to you soon." data-err="That didn't go through. Try again, or email me directly.">
  <input type="hidden" name="access_key" value="{esc(key)}">
  <input type="hidden" name="subject" value="New enquiry from tommyjackett.com">
  <input type="hidden" name="from_name" value="tommyjackett.com">
  <input type="hidden" name="redirect" value="{esc(ctx.abs(redirect_path))}?sent=1">
  <div class="hp" aria-hidden="true"><label>Leave this empty<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label>
    <label>Leave this empty<input type="text" name="website_url" tabindex="-1" autocomplete="off"></label></div>
  <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required data-label="name"></div>
  <div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required data-label="email"></div>
  <div class="field"><label for="f-co">Company or project <span class="opt">(optional)</span></label><input id="f-co" name="company" type="text" autocomplete="organization"></div>
  <div class="field"><label for="f-type">What is it about?</label><select id="f-type" name="project_type">{options}</select></div>
  <div class="field"><label for="f-msg">What are you working on?</label><textarea id="f-msg" name="message" required data-label="message"></textarea><p class="hint">A few lines is plenty.</p></div>
  <div><button class="btn" type="submit">Send it</button><p class="small" style="margin-top:14px">I only use your details to reply to you.</p></div>
  <p class="form-msg" role="status" aria-live="polite" hidden></p>
  <p class="small" data-mailto-fallback hidden>Or email me directly: {mailto}</p>
</form>'''


# ------------------------------------------------------------------ header / footer
def header_html(ctx, current_path, home=False):
    s = ctx.site
    lis = "".join(
        f'<li><a href="{esc(ctx.url(n["path"]))}"{" aria-current=page" if current_path.startswith(n["path"]) else ""}>{esc(n["label"])}</a></li>'
        for n in s["nav"])
    menu_lis = "".join(
        f'<li><a href="{esc(ctx.url(n["path"]))}"{" aria-current=page" if current_path.startswith(n["path"]) else ""}>{esc(n["label"])}</a></li>'
        for n in s["nav"])
    cls = "site-header" + (" site-header--home" if home else " is-solid")
    soc = " ".join(ctx.a(i, cls="") for i in s["footer"]["socialIds"][:3])
    return f'''<header class="{cls}" id="site-header"><div class="wrap bar">
  <a class="brand" href="{esc(ctx.url("/"))}">{esc(s["name"])}</a>
  <nav class="nav-desktop" aria-label="Main"><ul class="">{lis}</ul></nav>
  <a class="nav-film" href="{esc(ctx.url(s["film"]["sitePath"]))}">Film</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
</div></header>
<div class="menu" id="menu" role="dialog" aria-label="Menu"><nav aria-label="Menu"><ul>{menu_lis}</ul></nav>
  <div class="menu-foot"><a class="btn" href="{esc(ctx.watch_url)}">Watch on YouTube</a><p class="small">{soc}</p></div></div>'''


def closer_html(ctx):
    return (f'<nav class="closer" aria-label="Before you go"><div class="wrap">'
            f'<a href="{esc(ctx.url(ctx.site["film"]["sitePath"]))}">Watch the film</a>'
            f'<a href="{esc(ctx.url("/contact/"))}">Get in touch</a></div></nav>')


def footer_html(ctx):
    s = ctx.site
    f = s["footer"]
    fm = "".join(f'<li><a href="{esc(ctx.url(i["path"]))}">{esc(i["label"])}</a></li>' for i in f["map"])
    soc = "".join(f'<li>{ctx.a(i)}</li>' for i in f["socialIds"] if ctx.link(i))
    mach = f'<li><a href="{esc(ctx.url("/feed.xml"))}">Notes feed (RSS)</a></li>'
    if ctx.machine_files:
        mach += f'<li><a href="{esc(ctx.url("/sitemap.xml"))}">Sitemap</a></li>'
    return f'''<footer class="site-footer"><div class="wrap">
  <div class="foot-grid">
    <div class="foot-id"><p>{esc(f["line1"])}</p><p class="small">{esc(f["line2"])}</p>
      <a class="btn" href="{esc(ctx.watch_url)}">Watch In Guns We Trust</a></div>
    <div class="foot-cols">
      <div class="foot-col"><h2>Map</h2><ul>{fm}</ul></div>
      <div class="foot-col"><h2>Elsewhere</h2><ul>{soc}</ul></div>
      <div class="foot-col"><h2>Feeds</h2><ul>{mach}</ul></div>
    </div>
  </div>
  <div class="foot-bottom"><p class="small">{esc(s["film"]["creditLine"])}</p>
    <p class="small">{esc(f["copyright"])}</p>
    <a class="foot-top" href="#top">Back to top</a></div>
</div><div class="foot-name" aria-hidden="true">Tommy Jackett</div></footer>'''


# ------------------------------------------------------------------ page render
def render_page(ctx, p):
    s = ctx.site
    path = p["path"]
    is_404 = path.endswith("404.html")
    canon_url = ctx.abs(path)
    robots = "noindex, nofollow" if (not ctx.production or p.get("noindex") or is_404) else "index, follow, max-image-preview:large"
    head = []
    head.append(f'<title>{esc(p["title"])}</title>')
    if p.get("description"):
        head.append(f'<meta name="description" content="{esc(p["description"])}">')
    head.append(f'<meta name="robots" content="{robots}">')
    if not is_404 and p.get("canonical", True):
        head.append(f'<link rel="canonical" href="{esc(canon_url)}">')
    # social
    og = p.get("og_image") or s["images"]["ogHome"]
    if og.endswith(".jpg") or og.endswith(".png"):
        og_url, ow, oh = ctx.abs("/img/" + og), 1200, 630
    else:
        im = ctx.images.get(og)
        social = im.get("social") if im else None
        if social:
            og_url, ow, oh = ctx.abs("/img/" + social), 1200, 630
        else:
            og_url, ow, oh = ctx.img_abs(og, 1280), im["width"] if im else 1280, im["height"] if im else 720
    og_alt = p.get("og_alt") or ctx.images.get(og, {}).get("alt", s["name"])
    og_title = p.get("og_title") or p["title"]
    if not is_404:
        head += [
            f'<meta property="og:site_name" content="{esc(s["name"])}">',
            f'<meta property="og:type" content="{esc(p.get("og_type", "website"))}">',
            f'<meta property="og:title" content="{esc(og_title)}">',
            f'<meta property="og:description" content="{esc(p.get("description", ""))}">',
            f'<meta property="og:url" content="{esc(canon_url)}">',
            f'<meta property="og:image" content="{esc(og_url)}">',
            f'<meta property="og:image:width" content="{ow}">',
            f'<meta property="og:image:height" content="{oh}">',
            f'<meta property="og:image:alt" content="{esc(og_alt)}">',
            f'<meta property="og:locale" content="{s["ogLocale"]}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc(og_title)}">',
            f'<meta name="twitter:description" content="{esc(p.get("description", ""))}">',
            f'<meta name="twitter:image" content="{esc(og_url)}">',
            f'<meta name="twitter:image:alt" content="{esc(og_alt)}">',
        ]
        a = p.get("article")
        if a:
            head.append(f'<meta property="article:published_time" content="{esc(a["published"])}">')
            head.append(f'<meta property="article:modified_time" content="{esc(a["modified"])}">')
            head.append(f'<meta property="article:author" content="{esc(ctx.abs("/about/"))}">')
    head += [
        '<meta name="theme-color" content="#0e0e0f">',
        '<meta name="color-scheme" content="dark">',
        f'<link rel="icon" type="image/png" sizes="48x48" href="{ctx.url("/icons/icon-48.png")}">',
        f'<link rel="icon" type="image/png" sizes="192x192" href="{ctx.url("/icons/icon-192.png")}">',
        f'<link rel="apple-touch-icon" href="{ctx.url("/icons/icon-180.png")}">',
        f'<link rel="alternate" type="application/rss+xml" title="Notes by Tommy Jackett" href="{ctx.url("/feed.xml")}">',
        f'<link rel="preload" href="{ctx.url("/fonts/anton-400-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
        f'<link rel="preload" href="{ctx.url("/fonts/inter-variable-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
    ]
    for pid_ in p.get("preload", []):
        im = ctx.images[pid_]
        ws = im["widths"]
        srcset = ", ".join(f"{ctx.url('/img/' + im['file'] + '-' + str(w) + '.webp')} {w}w" for w in ws)
        head.append(f'<link rel="preload" as="image" href="{ctx.img_url(pid_)}" imagesrcset="{srcset}" imagesizes="{esc(p.get("preload_sizes", "100vw"))}">')
    head.append(f'<link rel="stylesheet" href="{ctx.asset("site.css")}">')
    head.append("<script>document.documentElement.classList.add('js')</script>")
    if p.get("head_extra"):
        head.append(p["head_extra"])
    if p.get("jsonld"):
        head.append(jsonld.script(p["jsonld"]))
    home = path == "/"
    body_cls = (("home " if home else "") + p.get("body_class", "")).strip()
    cur = "" if home else path
    page_html = fill(_layout(),
                     lang=s["locale"], head="\n".join(head), body_class=body_cls,
                     header=header_html(ctx, cur, home=home), content=typo_html(p["content"]),
                     closer="" if p.get("no_closer") else closer_html(ctx),
                     footer=typo_html(footer_html(ctx)), js=ctx.asset("site.js"))
    return page_html
