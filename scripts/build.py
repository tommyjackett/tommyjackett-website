#!/usr/bin/env python3
"""Build tommyjackett.com into public/. Dependency-free.

    python3 scripts/build.py                 staging: sub-path, noindex everywhere, robots blocks all
    python3 scripts/build.py --root          go-live: root domain, indexing on, sitemap, llms.txt, CNAME
                                             (refuses to run while the Web3Forms placeholder key is in data/form.json)
    python3 scripts/build.py --machine       staging that also writes sitemap.xml and llms.txt
    python3 scripts/build.py --state after   bake in the after-launch wording (default: before text, switched by a tiny script at launch)
    python3 scripts/build.py --base-path "" --site-url http://localhost:8841 --out /tmp/x     any target

Copy lives in data/pages.json and data/stories.json. Facts live in data/site.json, links in data/links.json,
photos in data/images.json (webp files in src/img named <file>-<width>.webp).
"""
import argparse
import datetime
import hashlib
import html as _html
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMD = chr(0x2014)
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def load(name):
    with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


SITE, STORIES, PAGES, LINKS, FORM = load("site"), load("stories"), load("pages"), load("links"), load("form")
SERIES = load("series")
IMAGES = {i["id"]: i for i in load("images")}
LINK = {l["id"]: l for l in LINKS}
P = {"base": "", "url": "", "prod": False, "bake_after": False, "versions": {}}


# ---------------------------------------------------------------- text
def esc(s):
    return _html.escape(str(s), quote=True)


def typo(s):
    s = re.sub(r"(?<=\w)'(?=\w)", "’", s)
    s = re.sub(r"(^|[\s(\[])'(?=\d)", lambda m: m.group(1) + "’", s)
    s = re.sub(r"(^|[\s(\[])'", lambda m: m.group(1) + "‘", s)
    s = s.replace("'", "’")
    s = re.sub(r'(^|[\s(\[])"', lambda m: m.group(1) + "“", s)
    return s.replace('"', "”")


def typo_html(h):
    parts = re.split(r"(<script.*?</script>|<style.*?</style>|<[^>]+>)", h, flags=re.S)
    for i in range(0, len(parts), 2):
        t = parts[i]
        if t and ("'" in t or '"' in t or "&#x27;" in t or "&quot;" in t):
            parts[i] = _html.escape(typo(_html.unescape(t)), quote=False)
    return "".join(parts)


def fdate(d, short=True):
    y, m, dd = [int(x) for x in d[:10].split("-")]
    return f"{dd} {MONTHS[m - 1][:3] if short else MONTHS[m - 1]} {y}"


def url(path):
    if re.match(r"^(https?:|mailto:|#)", path):
        return path
    return P["base"] + (path if path.startswith("/") else "/" + path)


def absu(path):
    return path if path.startswith("http") else P["url"] + (path if path.startswith("/") else "/" + path)


def resolve(t):
    if t.startswith("link:"):
        return LINK[t[5:]]["url"]
    return url(t)


def lnk(id_):
    l = LINK.get(id_)
    return l if l and l.get("verified") else None


def when(kind="short", strip=""):
    """Launch wording. Default: the before text in the HTML, with both texts in data attributes so a tiny script
    switches it at the launch moment. With --state after the after text is baked in and no script is needed."""
    f = SITE["film"]["lead" if kind == "lead" else ("whenShort" if kind == "short" else "whenFull")]
    b, a = f["before"].replace(strip, "", 1), f["after"].replace(strip, "", 1)
    if P["bake_after"]:
        return esc(a)
    return f'<span data-launch="{esc(SITE["film"]["launchISO"])}" data-before="{esc(b)}" data-after="{esc(a)}">{esc(b)}</span>'


WATCH = SITE["film"]["watchUrl"]


# ---------------------------------------------------------------- images
def img(id_, sizes="100vw", cls="", priority=False, alt=None, focal=True, style=""):
    im = IMAGES[id_]
    ws = im["widths"]
    srcset = ", ".join(f"{url('/img/' + im['file'] + '-' + str(w) + '.webp')} {w}w" for w in ws)
    pick = max([w for w in ws if w <= 1280] or ws)
    st = []
    if focal and im.get("focal"):
        st.append("object-position:" + im["focal"])
    if style:
        st.append(style)
    a = [f'src="{url("/img/" + im["file"] + "-" + str(pick) + ".webp")}"', f'srcset="{srcset}"', f'sizes="{esc(sizes)}"',
         f'width="{im["width"]}"', f'height="{im["height"]}"', f'alt="{esc(im["alt"] if alt is None else alt)}"']
    if cls:
        a.append(f'class="{cls}"')
    a += ['loading="eager" fetchpriority="high"' if priority else 'loading="lazy"', 'decoding="async"']
    if st:
        a.append(f'style="{";".join(st)}"')
    return "<img " + " ".join(a) + ">"


def keyart(priority=False):
    """Key art on wide screens, the portrait poster on phones. Both untouched."""
    k, p = IMAGES["igwt-key-art"], IMAGES["igwt-poster"]
    ss = lambda im: ", ".join(f"{url('/img/' + im['file'] + '-' + str(w) + '.webp')} {w}w" for w in im["widths"])
    pri = 'loading="eager" fetchpriority="high"' if priority else 'loading="lazy"'
    return (f'<picture class="keyart"><source media="(max-width: 699px)" srcset="{ss(p)}" sizes="100vw" width="{p["width"]}" height="{p["height"]}">'
            f'<img src="{url("/img/igwt-key-art-1280.webp")}" srcset="{ss(k)}" sizes="100vw" width="{k["width"]}" height="{k["height"]}" alt="{esc(k["alt"])}" {pri} decoding="async"></picture>')


def img_abs(id_, w=None):
    im = IMAGES[id_]
    w = w if w in im["widths"] else max([x for x in im["widths"] if x <= 1280] or im["widths"])
    return absu(f"/img/{im['file']}-{w}.webp")


# ---------------------------------------------------------------- pieces
def btn(label, target, extra=""):
    return f'<a class="btn" href="{esc(resolve(target))}"{(" " + extra) if extra else ""}>{esc(label)}</a>'


def go(label, target):
    return f'<a class="go" href="{esc(resolve(target))}">{esc(label)}</a>'


def rv(delay=0):
    return f' style="--d:{delay}s"' if delay else ""


def video(v, big=False):
    """Click-to-play facade. The anchor goes to YouTube when scripts are off."""
    watch = f"https://www.youtube.com/watch?v={v['id']}"
    if not v.get("thumb"):
        return f'<p class="th-lk"><a class="go" href="{watch}">Watch the Short</a></p>'
    cls = "vid vid--short" if v.get("short") else "vid"
    sizes = "(min-width: 900px) 62vw, 100vw" if big else "(min-width: 900px) 40vw, 100vw"
    if v.get("short"):
        sizes = "320px"
    cap = f'<p class="vid-cap"><span>{esc(v["title"])}</span><a href="{watch}">Watch on YouTube</a></p>'
    return (f'<div><div class="{cls}"><a class="vid-play" href="{watch}" data-yt="{v["id"]}" data-title="{esc(v["title"])}" aria-label="Play: {esc(v["title"])}">'
            f'{img(v["thumb"], sizes=sizes, alt="")}<span class="vid-ic"></span></a></div>{cap}</div>')


def find_links(ids, cls=""):
    return "".join(f'<li><a href="{esc(LINK[i]["url"])}">{esc(LINK[i]["label"])}</a></li>' for i in ids if lnk(i))


# ---------------------------------------------------------------- header, footer
def header(cur, home=False):
    def items(c):
        return "".join(f'<li><a href="{esc(url(n["path"]))}">{esc(n["label"])}</a></li>' for n in SITE["nav"])
    watch_link = f'<a class="hd-watch" href="{esc(WATCH)}">Watch</a>' if cur == SITE["film"]["sitePath"] else ""
    return f'''<header class="hd" id="hd"><div class="wrap hd-in">
<a class="hd-name" href="{esc(url("/"))}#top" aria-label="Tommy Jackett, back to top"><span>Tommy</span><span>Jackett</span></a>
<nav class="hd-nav" aria-label="Main"><ul>{items(cur)}</ul></nav>
{watch_link}<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
</div></header>
<div class="menu" id="menu"><nav aria-label="Menu"><ul>{items(cur)}</ul></nav>
<div class="menu-foot"><a class="btn" href="{esc(WATCH)}">Watch In Guns We Trust</a></div></div>'''


def footer(film_credit):
    nav = "".join(f'<li><a href="{esc(url(n["path"]))}">{esc(n["label"])}</a></li>' for n in SITE["nav"])
    find = find_links(SITE["footer"]["findIds"])
    credit = f'<p class="small">{esc(SITE["film"]["creditLine"])}</p>' if film_credit else ""
    return f'''<footer class="ft"><div class="wrap">
<div class="ft-row"><ul class="ft-nav">{nav}</ul><a class="go ft-top" href="#top" style="--x:0">Back to top</a></div>
{social_icons("soc ft-soc")}
<div class="ft-fine">{credit}<p class="small">{esc(SITE["footer"]["copyright"])}</p></div>
</div></footer>'''


# ---------------------------------------------------------------- JSON-LD
def person_ld():
    same = [l["url"] for l in LINKS if l.get("verified") and l.get("sameAs")]
    return {"@type": "Person", "@id": absu("/") + "#person", "name": SITE["name"], "url": absu("/"),
            "image": img_abs(SITE["images"]["person"], 1184), "description": SITE["entityStatement"], "jobTitle": SITE["jobTitle"],
            "nationality": {"@type": "Country", "name": "Australia"}, "homeLocation": {"@type": "Place", "name": "Melbourne, Australia"},
            "worksFor": {"@id": absu("/") + "#vidpod"}, "knowsAbout": SITE["knowsAbout"], "sameAs": same}


def vidpod_ld():
    v = SITE["vidpod"]
    return {"@type": "Organization", "@id": absu("/") + "#vidpod", "name": v["name"], "url": v["url"], "sameAs": v["sameAs"]}


def website_ld():
    return {"@type": "WebSite", "@id": absu("/") + "#website", "url": absu("/"), "name": SITE["name"], "inLanguage": SITE["locale"],
            "publisher": {"@id": absu("/") + "#person"}}


def breadcrumb_ld(trail):
    items = [("Tommy Jackett", "/")] + trail
    out = []
    for i, (n, p) in enumerate(items, 1):
        d = {"@type": "ListItem", "position": i, "name": n}
        if p:
            d["item"] = absu(p)
        out.append(d)
    return {"@type": "BreadcrumbList", "itemListElement": out}


def film_id():
    return SITE["film"]["filmSite"].rstrip("/") + "/#film"


def movie_ld():
    """A pointer to the film as the official site describes it. Not a rival entity: url and sameAs go to the film's own properties."""
    f = SITE["film"]
    return {"@type": "Movie", "@id": film_id(), "name": f["title"], "url": f["filmSite"], "description": f["oneLiner"],
            "sameAs": [LINK[i]["url"] for i in ("film-imdb", "film-youtube")],
            "actor": {"@id": absu("/") + "#person"}, "creator": {"@id": absu("/") + "#person"}}


def video_ld(v, page):
    d = {"@type": "VideoObject", "name": v["title"], "description": v["desc"], "uploadDate": v["date"],
         "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}", "contentUrl": f"https://www.youtube.com/watch?v={v['id']}",
         "publisher": {"@id": absu("/") + "#person"}, "inLanguage": "en"}
    d["thumbnailUrl"] = [img_abs(v["thumb"], 1280)] if v.get("thumb") else [f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"]
    if v.get("duration"):
        d["duration"] = v["duration"]
    return d


def ld_script(graph):
    txt = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{txt}</script>'


# ---------------------------------------------------------------- pages registry
PAGE_LIST = []


def add(path, title, desc, content, og, og_alt="", ld=None, cls="", preload=None, film_credit=False, lastmod="2026-10-20", cur=None, noindex=False):
    PAGE_LIST.append(dict(path=path, title=title, desc=desc, content=content, og=og, og_alt=og_alt, ld=ld or [], cls=cls,
                          preload=preload or [], film_credit=film_credit, lastmod=lastmod, cur=cur if cur is not None else path, noindex=noindex))


SOCIAL_ICONS = {
    "tj-instagram": ('Instagram', '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".9" fill="currentColor" stroke="none"/>'),
    "tj-youtube": ('YouTube', '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10.2 9.4v5.2l4.4-2.6z" fill="currentColor" stroke="none"/>'),
    "tj-tiktok": ('TikTok', '<path d="M13.6 3.5v11.2a3.4 3.4 0 1 1-3.4-3.4"/><path d="M13.6 3.5c.4 2.5 2.2 4.3 4.9 4.6"/>'),
    "tj-linkedin": ('LinkedIn', '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8.2 10.6v5.9"/><circle cx="8.2" cy="7.7" r=".55" fill="currentColor"/><path d="M11.8 16.5v-5.9"/><path d="M11.8 13.1c0-1.5 1-2.6 2.4-2.6s2.2 1 2.2 2.6v3.4"/>'),
    "tj-facebook": ('Facebook', '<path d="M13.9 20.5v-7.3h2.6l.4-3h-3V8.4c0-.9.3-1.5 1.5-1.5h1.6V4.2c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.2H8.3v3h2.6v7.3"/>'),
    "tj-imdb": ('IMDb', '<rect x="2.5" y="6.5" width="19" height="11" rx="2.5"/><text x="12" y="14.4" text-anchor="middle" font-size="6.6" font-weight="700" font-family="Inter, Arial, sans-serif" fill="currentColor" stroke="none">IMDb</text>'),
}
SOCIAL_ORDER = ["tj-instagram", "tj-youtube", "tj-tiktok", "tj-linkedin", "tj-facebook", "tj-imdb"]


def social_icons(cls="soc"):
    items = []
    for i in SOCIAL_ORDER:
        if i not in LINK:
            continue
        name, svg = SOCIAL_ICONS[i]
        items.append(f'<li><a href="{esc(LINK[i]["url"])}" rel="me" aria-label="Tommy Jackett on {name}" title="{name}">'
                     f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{svg}</svg></a></li>')
    return f'<ul class="{cls}">' + "".join(items) + '</ul>'


def linked(text):
    """Escape copy, then turn [[dts]], [[vidpod]] and [[josh:Label]] markers into links. Tommy: always link The Daily Talk Show and Josh."""
    out = esc(text)
    out = out.replace("[[dts]]", '<a class="link" href="https://www.thedailytalkshow.com">The Daily Talk Show</a>')
    out = out.replace("[[vidpod]]", '<a class="link" href="https://www.vidpod.com.au">VIDPOD</a>')
    out = re.sub(r"\[\[josh:([^\]]+)\]\]", lambda m: f'<a class="link" href="https://joshjanssen.com">{m.group(1)}</a>', out)
    return out


def film_links(cls):
    """Followed links out to the film's own properties. Descriptive anchor text, same tab, no nofollow."""
    rows = [("film-site", "In Guns We Trust, the official site"), ("film-press", "In Guns We Trust press kit"),
            ("film-youtube", "In Guns We Trust on YouTube"), ("film-imdb", "In Guns We Trust on IMDb")]
    lk = "".join(f'<a href="{esc(LINK[i]["url"])}">{esc(l)}</a>' for i, l in rows if lnk(i))
    return f'<p class="{cls}">{lk}</p>'



def form_html():
    d = PAGES["contact"]
    key = FORM["accessKey"]
    live = key and key != FORM["placeholder"]
    opts = "".join(f"<option>{esc(o)}</option>" for o in d["options"])
    m = FORM["messages"]
    return f'''<form class="form" method="post" action="{esc(FORM["endpoint"])}" novalidate data-form data-live="{1 if live else 0}" data-endpoint="{esc(FORM["endpoint"])}"
 data-ok="{esc(m["ok"])}" data-err="{esc(m["err"])}" data-notlive="{esc(m["notLive"])}">
<input type="hidden" name="access_key" value="{esc(key)}"><input type="hidden" name="subject" value="New message from tommyjackett.com"><input type="hidden" name="from_name" value="tommyjackett.com">
<div class="hp" aria-hidden="true"><label>Leave this empty <input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label><label>Leave this empty <input type="text" name="website_url" tabindex="-1" autocomplete="off"></label></div>
<div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required data-label="name"></div>
<div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required data-label="email"></div>
<div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="message" required data-label="message"></textarea></div>
<div class="form-go"><button class="btn" type="submit">{esc(d["send"])}</button></div>
<p class="form-msg" role="status" aria-live="polite" hidden></p></form>'''


# ---------------------------------------------------------------- HOME (single page)
def build_home():
    h = PAGES["home"]
    f = SITE["film"]
    hero = f'''<section class="hero" aria-label="Introduction">
<div class="hero-pic hero-photo">{img("salt-flats-tommy-wide", sizes="(min-width: 900px) 56vw, 150vw", priority=True, focal=False)}</div>
<h1 class="hero-name" aria-label="Tommy Jackett"><span class="hn hn1" aria-hidden="true">Tommy</span> <span class="hn hn2" aria-hidden="true">Jackett</span></h1>
<div class="hero-pic hero-cut" aria-hidden="true">{img("salt-flats-tommy-cutout", sizes="(min-width: 900px) 56vw, 150vw", priority=True, alt="", focal=False)}</div>
<div class="hero-copy">
{social_icons("soc hero-soc")}
<p class="hero-l1">{esc(h["heroLine1"])}</p>
<p class="hero-l2">{esc(h["heroLine2"])}</p>
<p><a class="btn" href="{esc(WATCH)}">{esc(h["heroButton"])}</a></p>
</div></section>'''

    doco = f'''<section class="doco3" id="doco" aria-labelledby="doco-h">
<figure class="doco3-art rv">{keyart()}</figure>
<div class="wrap doco3-info rv">
<p class="kicker">Our feature documentary</p>
<h2 class="sec-h" id="doco-h">In Guns We Trust</h2>
<p class="doco3-syn">{linked(h["docoSyn"])}</p>
<p class="doco3-now">{esc(h["docoNow"])}</p>
<p class="doco3-credits">Hosted by Tommy Jackett and <a href="https://joshjanssen.com">Josh Janssen</a>. Story by <a href="https://joshjanssen.com">Josh Janssen</a>, Naysan Naraqi and Tommy Jackett. Directed by <a href="https://joshjanssen.com/in-guns-we-trust/">Josh Janssen</a>.</p>
<div class="doco3-btns"><a class="btn" href="{esc(WATCH)}">Watch on YouTube</a><a class="btn btn--ghost" href="{esc(LINK["film-site"]["url"])}">About the doco</a></div>
</div></section>'''

    ser = SERIES["series"]

    def ids(s):
        if s.get("external"):
            return []
        long = [v["id"] for v in s["videos"] if not v.get("short")]
        short = [v["id"] for v in s["videos"] if v.get("short")]
        return long + short

    def cover_src(s, w):
        im = IMAGES[s["cover"]]
        ws = [x for x in im["widths"] if x <= w] or im["widths"][:1]
        return url(f'/img/{im["file"]}-{ws[-1]}.webp')

    payload = [{"slug": s["slug"], "title": s["title"], "line": s["line"], "ids": ids(s),
                "href": s["external"]["url"] if s.get("external") else "",
                "cover": cover_src(s, 1280), "thumb": cover_src(s, 640), "alt": IMAGES[s["cover"]]["alt"],
                "sq": bool(s.get("square"))} for s in ser]
    first = ser[0]
    rows = "".join(
        (f'<li><a class="sl" href="{esc(s["external"]["url"])}">' if s.get("external") else f'<li{" hidden" if s is first else ""}><button class="sl" type="button" data-pick="{esc(s["slug"])}">')
        + f'<span class="sl-pic{" sl-pic--sq" if s.get("square") else ""}">' + img(s["cover"], sizes="(min-width: 900px) 150px, 34vw", focal=False)
        + f'</span><span class="sl-txt"><span class="sl-t">{esc(s["title"])}</span><span class="sl-l">{esc(s["line"])}</span></span>'
        + ('<span class="sl-go" aria-hidden="true">&nearr;</span></a></li>' if s.get("external") else '<span class="sl-go" aria-hidden="true">&rarr;</span></button></li>')
        for s in ser)
    lately = (f'<section class="sec series3" id="series" aria-labelledby="series-h"><div class="wrap wrap--narrow">'
              f'<div class="series3-head rv"><h2 class="sec-h" id="series-h">{esc(h["latelyTitle"])}</h2>'
              f'<p class="series3-line">{esc(h["latelyLine"])}</p></div>'
              f'<div class="series3-grid" data-series>'
              f'<div class="ft3 rv"><div class="ft3-pic"><img data-ft-img src="{esc(cover_src(first, 1280))}" alt="{esc(IMAGES[first["cover"]]["alt"])}" width="1280" height="720" loading="lazy">'
              f'<span class="ft3-tag" data-ft-tag>Latest</span>'
              f'<button class="play" type="button" data-play aria-label="Play {esc(first["title"])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></button></div>'
              f'<h3 class="ft3-t" data-ft-title>{esc(first["title"])}</h3><p class="ft3-l" data-ft-line>{esc(first["line"])}</p></div>'
              f'<ul class="sl-list rv" data-list>{rows}</ul>'
              f'</div></div>'
              f'<script type="application/json" id="series-data">{json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")}</script>'
              f'<dialog class="player" data-player aria-label="Video player"><div class="player-in"><button class="player-x" type="button" data-close aria-label="Close video">&times;</button>'
              f'<div class="player-frame" data-frame></div></div></dialog>'
              f'</section>')

    about = (f'<section class="sec about5" id="about" aria-labelledby="about-h"><div class="wrap wrap--narrow about5-in">'
             f'<figure class="about5-pic rv">' + img("salt-flats-tommy-portrait", sizes="(min-width: 900px) 380px, 100vw") + '</figure>'
             f'<div class="about5-text rv"><h2 class="sec-h" id="about-h">About Tommy Jackett</h2>'
             f'<p class="about5-bio">{linked(h["aboutBio"])} <a class="link" href="#doco">In Guns We Trust</a> {linked(h["aboutBioDoco"])}</p>'
             f'<p class="about5-vp">{linked(h["aboutVidpodLine"])}</p>'
             f'<a class="btn btn--ghost" href="https://www.vidpod.com.au">Visit VIDPOD</a></div>'
             f'</div></section>')

    contact = f'''<section class="sec contact2" id="contact" aria-labelledby="contact-h"><div class="wrap contact2-in">
<div class="rv"><h2 class="sec-h" id="contact-h">Get in touch</h2><p>{esc(h["contactLine"])}</p></div>
<div class="rv">{form_html()}</div>
</div></section>'''

    ld = [website_ld(), person_ld(), vidpod_ld(), movie_ld()]
    add("/", SITE["home"]["title"], SITE["home"]["description"], "\n".join([hero, doco, lately, about, contact]),
        og="salt-flats-tommy-wide", og_alt="Tommy Jackett standing alone on the Bonneville Salt Flats at dusk", ld=ld,
        cls="home", preload=["salt-flats-tommy-wide", "salt-flats-tommy-cutout"], film_credit=False, cur="")



# ---------------------------------------------------------------- SERIES
def build_series():
    ld_videos = []

    def vlinks(s):
        if s.get("external"):
            return f'<div class="sr-btns"><a class="btn" href="{esc(s["external"]["url"])}">{esc(s["external"]["label"])}</a></div>'
        out = []
        for k, v in enumerate(s["videos"][:3]):
            label = v["label"] if len(s["videos"]) > 1 else "Watch"
            cls = "btn" if k == 0 else "btn btn--ghost"
            out.append(f'<a class="{cls}" href="https://www.youtube.com/watch?v={esc(v["id"])}">{esc(label)}</a>')
            if v.get("date"):
                ld_videos.append({"@type": "VideoObject", "name": v["title"], "description": s["line"], "uploadDate": v["date"],
                                  "contentUrl": "https://www.youtube.com/watch?v=" + v["id"], "embedUrl": "https://www.youtube-nocookie.com/embed/" + v["id"],
                                  "thumbnailUrl": ["https://i.ytimg.com/vi/" + v["id"] + "/hqdefault.jpg"], "publisher": {"@id": absu("/") + "#person"}})
        return '<div class="sr-btns">' + "".join(out) + '</div>'

    blocks = []
    for n, s in enumerate(SERIES["series"]):
        flip = " sr--flip" if n % 2 else ""
        sq = " sr-pic--sq" if s.get("square") else ""
        blocks.append(f'<article class="sr{flip}" id="{esc(s["slug"])}"><figure class="sr-pic rv{sq}">'
                      + img(s["cover"], sizes="(min-width: 900px) 50vw, 100vw", focal=False)
                      + f'</figure><div class="sr-info rv"><h2 class="sr-h">{esc(s["title"])}</h2><p>{esc(s["line"])}</p>' + vlinks(s) + '</div></article>')
    tests = "".join(f'<article class="st2 rv" id="{esc(s["slug"])}"><figure>' + img(s["cover"], sizes="(min-width: 900px) 40vw, 100vw", focal=False)
                    + f'</figure><h3 class="st2-h">{esc(s["title"])}</h3><p>{esc(s["line"])}</p>' + vlinks(s) + '</article>' for s in SERIES["tests"])
    content = (f'<div class="wrap sr-top"><p class="kicker">What I\'m up to lately</p><h1 class="sec-h">Series</h1><p class="sr-intro">{esc(SERIES["intro"])}</p></div>'
               + '<div class="wrap sr-list">' + "".join(blocks) + '</div>')
               
    ld = [website_ld(), person_ld(), {"@type": "CollectionPage", "name": "Series by Tommy Jackett", "url": absu("/series/"),
          "about": {"@id": absu("/") + "#person"}, "hasPart": ld_videos}, breadcrumb_ld([("Series", None)])]
    add("/series/", "Series by Tommy Jackett: The Jackett Ranch, DJ Daka and more",
        "The Jackett Ranch, DJ Daka, The Daily Talk Show, and the 7-Eleven and O Bike rabbit holes. The series Tommy Jackett makes on his own channels.",
        content, og="thumb-ranch-part-1", og_alt="The Jackett Ranch, Part 1", ld=ld, cls="series-pg", cur="/series/")

# ---------------------------------------------------------------- DOCO
def build_doco():
    d = PAGES["doco"]
    f = SITE["film"]
    art = f'<h1 class="vh">{esc(d["h1"])}</h1><figure class="dc-art art">{keyart(True)}</figure>'
    cta = f'''<div class="wrap dc-cta"><a class="btn" href="{esc(WATCH)}">Watch on YouTube</a><p class="dc-fact">{esc(d["facts"])} {when("full")}</p></div>'''
    body = f'''<div class="wrap dc-body">
<p class="dc-lead rv">{when("lead")}</p>
<p class="syn rv"{rv(.05)}>{esc(d["synopsis"])}</p>
{film_links("dc-links rv")}
<p class="small rv">{esc(d["filmLinksLine"])} <a class="link" href="{esc(LINK["film-site"]["url"])}">ingunswetrustfilm.com</a></p></div>'''
    stills = ''
    bts = f'''<div class="wrap dc-bts"><p class="dc-bts-go">{go("Making In Guns We Trust, in my own photos", "/stories/making-in-guns-we-trust/")}</p></div>'''
    end = f'''<div class="wrap dc-end rv"><img class="logo" src="{esc(url("/img/igwt-title-white-1280.webp"))}" width="1280" height="761" alt="In Guns We Trust" loading="lazy"><a class="btn" href="{esc(WATCH)}">Watch In Guns We Trust</a></div>
<div class="wrap dc-note"><p class="small"><strong>{esc(f["contentNote"])}</strong> {esc(f["supportInline"])}</p>
<p class="small">{esc(d["film"])}</p>
<p class="small dc-mail"><span>Screenings: <a class="link" href="mailto:screenings@ingunswetrustfilm.com">screenings@ingunswetrustfilm.com</a></span><span>Press: <a class="link" href="mailto:press@ingunswetrustfilm.com">press@ingunswetrustfilm.com</a></span></p></div>'''
    ld = [website_ld(), person_ld(), vidpod_ld(), movie_ld(),
          {"@type": "WebPage", "@id": absu(f["sitePath"]) + "#webpage", "url": absu(f["sitePath"]), "name": d["metaTitle"], "description": d["metaDescription"],
           "isPartOf": {"@id": absu("/") + "#website"}, "about": {"@id": absu("/") + "#person"}, "mentions": {"@id": film_id()}},
          breadcrumb_ld([("The doco", None)])]
    add(f["sitePath"], d["metaTitle"], d["metaDescription"], "\n".join([art, cta, body, stills, bts, end]), og="igwt-key-art",
        og_alt="In Guns We Trust key art: Tommy Jackett with a boom microphone and Josh Janssen with a camera, standing on a map of America",
        ld=ld, cls="doco-pg", film_credit=True, preload=["igwt-key-art"])


# ---------------------------------------------------------------- STORIES
def build_stories_index():
    d = PAGES["stories"]
    rows = []
    for st in STORIES:
        href = resolve(st["external"]) if st.get("external") else url(f"/stories/{st['slug']}/")
        mod = " ix-i--sq" if st["slug"] == "the-daily-talk-show" else (" ix-i--p" if st.get("homeTile") else "")
        ext = ' rel="noopener"' if st.get("external") else ""
        pic = st.get("homeTile") or st["tile"]
        rows.append(f'''<a class="ix-i{mod} rv" href="{esc(href)}"{ext}><figure>{img(pic, sizes="(min-width: 900px) 52vw, 100vw")}</figure>
<div class="ix-tx"><h2 class="ix-t">{esc(st["title"])}</h2><p class="ix-l">{esc(st["indexLine"])}</p><p class="ix-s">{esc(st["status"])}</p></div></a>''')
    content = f'<div class="wrap pg-h"><h1>{esc(d["h1"])}</h1></div><div class="wrap ix">{"".join(rows)}</div>'
    ld = [website_ld(), person_ld(), {"@type": "CollectionPage", "name": "Stories", "url": absu("/stories/"), "description": d["metaDescription"],
                                      "isPartOf": {"@id": absu("/") + "#website"},
                                      "hasPart": [{"@type": "WebPage", "url": absu(f"/stories/{s['slug']}/")} for s in STORIES if not s.get("external")]},
          breadcrumb_ld([("Stories", None)])]
    add("/stories/", d["metaTitle"], d["metaDescription"], content, og="thumb-ranch-part-1", og_alt="The Jackett Ranch video thumbnail", ld=ld, cls="stories-pg")


def thread_html(st):
    hero_id = st["videos"][0]["id"] if st["videos"] else None
    vids = {v["id"]: v for v in st.get("videos", [])}
    rows = []
    for t in st["thread"]:
        d = fdate(t["date"]) if t.get("date") else t.get("label", "")
        cls = "" if t.get("date") else ' class="th-next"'
        inner = f'<p class="th-x">{esc(t["text"])}</p>'
        extra = ""
        v = vids.get(t.get("video")) if t.get("video") else None
        if v and v["id"] != hero_id:
            extra += video(v)
        if t.get("photos"):
            extra += '<div class="th-ph">' + "".join(
                f'<figure>{img(pid, sizes="(min-width: 900px) 22vw, 50vw")}<figcaption>{esc(IMAGES[pid]["caption"])}</figcaption></figure>' for pid in t["photos"]) + "</div>"
        if t.get("press") and lnk(t["press"]):
            extra += f'<p class="th-lk"><a class="go" href="{esc(LINK[t["press"]]["url"])}">{esc(LINK[t["press"]]["label"])}</a></p>'
        rows.append(f'<li{cls}><p class="th-d">{esc(d)}</p><div class="th-v">{inner}{extra}</div></li>')
    return f'<ol class="th">{"".join(rows)}</ol>'


def build_story(st):
    path = f"/stories/{st['slug']}/"
    nxt = next(s for s in STORIES if s["slug"] == st["next"])
    nxt_href = resolve(nxt["external"]) if nxt.get("external") else url(f"/stories/{nxt['slug']}/")
    vids = st["videos"]
    first = vids[0] if vids else None
    crumb = f'<p class="sp-crumb"><a href="{esc(url("/stories/"))}">Stories</a></p>'
    long_ = " rn-long" if len(st["title"]) > 10 else ""
    fs = f' style="--fs:{st["titleSize"]}"' if st.get("titleSize") else ""
    lead = f'<div class="rn-lead"><p class="sp-st ser">{esc(st["status"])}</p><p class="sp-lede lead">{esc(st["lede"])}</p></div>'
    h1 = f'<h1 class="sp-t">{esc(st["title"])}</h1>'
    if st.get("heroPhoto"):
        top = f'''<div class="wrap rn rn--photo{long_}"{fs}>{crumb}{h1}
<figure class="rn-hero rv">{img(st["heroPhoto"], sizes="(min-width: 900px) 56vw, 100vw", priority=True)}</figure>
{lead}</div>
{('<div class="wrap sp-media rv">' + video(first, big=True) + '</div>') if first else ''}'''
    else:
        top = f'''<div class="wrap rn{long_}"{fs}>{crumb}{h1}
<figure class="rn-hero rn-vid rv">{video(first, big=True)}</figure>
{lead}</div>'''
    links = ""
    if st.get("links"):
        links = '<div class="wrap sp-links">' + "".join(f'<a class="go" href="{esc(LINK[i]["url"])}">{esc(LINK[i]["label"])}</a>' for i in st["links"] if lnk(i)) + "</div>"
    content = f'''{top}
<div class="wrap sp-thread">{thread_html(st)}</div>
{links}
<div class="wrap sp-nx rv"><a href="{esc(nxt_href)}"><p class="small">Next story</p><p class="nt">{esc(nxt["title"])}</p></a></div>'''
    og = next((i for i in (st["tile"],) if IMAGES[i].get("social")), st["tile"])
    ld = [website_ld(), person_ld(), breadcrumb_ld([("Stories", "/stories/"), (st["title"], None)])]
    ld += [video_ld(v, path) for v in vids if v.get("thumb")]
    add(path, st["metaTitle"], st["metaDescription"], content, og=og, og_alt=IMAGES[st["tile"]]["alt"], ld=ld, cls="story-pg", lastmod="2026-10-20")


# ---------------------------------------------------------------- ABOUT
def build_about():
    d = PAGES["about"]
    hero = f'''<div class="wrap ab"><h1 class="ab-h1">{esc(d["h1"])}<span class="vh"> {esc(d["h1Hidden"])}</span></h1>
<figure>{img("trip-tank", sizes="(min-width: 900px) 46vw, 100vw", priority=True)}</figure></div>'''
    paras = "".join(f'<p class="rv">{esc(t)}</p>' for t in d["body"])
    bio = f'<div class="wrap bio"><div class="bio-tx">{paras}</div><figure class="bio-fig rv">{img("tommy-portrait-mono", sizes="(min-width: 900px) 30vw, 100vw")}</figure></div>'
    rows = []
    for r in d["timeline"]:
        th = f'<span class="tl-th">{img(r["thumb"], sizes="(min-width: 900px) 22vw, 40vw")}</span>' if r.get("thumb") else ""
        cl = ' class="has-th"' if th else ""
        rows.append(f'<li{cl}><span class="tl-y">{esc(r["year"])}</span><span class="tl-x">{esc(r["text"])}</span>{th}</li>')
    press = "".join(f'<a href="{esc(LINK[i]["url"])}">{esc(LINK[i]["label"])}</a>' for i in d["press"])
    content = f'''{hero}{bio}<div class="wrap"><ol class="tl">{"".join(rows)}</ol></div>
<div class="wrap ab-press rv"><span class="ab-press-k">{esc(d["pressLine"])}</span>{press}</div>
<div class="wrap ab-go acts rv">{"".join(go(l["label"], l["target"]) for l in d["goLinks"])}</div>'''
    ld = [website_ld(), person_ld(), vidpod_ld(),
          {"@type": "ProfilePage", "url": absu("/about/"), "dateModified": "2026-10-20", "mainEntity": {"@id": absu("/") + "#person"}},
          breadcrumb_ld([("About", None)])]
    add("/about/", d["metaTitle"], d["metaDescription"], content, og="salt-flats-tommy-portrait", og_alt=IMAGES["salt-flats-tommy-portrait"]["alt"], ld=ld, cls="about-pg", preload=["trip-tank"])


# ---------------------------------------------------------------- WORK
def build_work():
    d = PAGES["work"]
    content = f'''<div class="wrap wk"><h1 class="vh">{esc(d["h1"])}</h1>
<img class="logo rv" src="{esc(url("/img/vidpod-logo-white-1117.webp"))}" width="1117" height="400" alt="VIDPOD">
<p class="wk-lead lead rv">{esc(d["lead"])}</p>
<div class="wk-side rv"><p class="wk-tx">{esc(d["text"])}</p>
<div class="acts"><a class="btn" href="{esc(url("/contact/"))}">{esc(d["buttonA"])}</a>{go(d["buttonB"], "link:vidpod")}</div></div></div>'''
    ld = [website_ld(), person_ld(), vidpod_ld(), breadcrumb_ld([("Work", None)])]
    add("/work/", d["metaTitle"], d["metaDescription"], content, og="vidpod-set", og_alt=IMAGES["vidpod-set"]["alt"], ld=ld, cls="work-pg")


# ---------------------------------------------------------------- CONTACT
def build_contact():
    d = PAGES["contact"]
    key = FORM["accessKey"]
    live = key and key != FORM["placeholder"]
    opts = "".join(f"<option>{esc(o)}</option>" for o in d["options"])
    m = FORM["messages"]
    form = f'''<form class="form rv" method="post" action="{esc(FORM["endpoint"])}" novalidate data-form data-live="{1 if live else 0}" data-endpoint="{esc(FORM["endpoint"])}"
 data-ok="{esc(m["ok"])}" data-err="{esc(m["err"])}" data-notlive="{esc(m["notLive"])}">
<input type="hidden" name="access_key" value="{esc(key)}"><input type="hidden" name="subject" value="New message from tommyjackett.com"><input type="hidden" name="from_name" value="tommyjackett.com"><input type="hidden" name="redirect" value="{esc(absu("/contact/?sent=1"))}">
<div class="hp" aria-hidden="true"><label>Leave this empty <input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label><label>Leave this empty <input type="text" name="website_url" tabindex="-1" autocomplete="off"></label></div>
<div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required data-label="name"></div>
<div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required data-label="email"></div>
<div class="field"><label for="f-type">What's it about?</label><select id="f-type" name="topic">{opts}</select></div>
<div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="message" required data-label="message"></textarea></div>
<div class="form-go"><button class="btn" type="submit">{esc(d["send"])}</button><p class="small" style="margin-top:14px">{esc(d["fine"])}</p></div>
<p class="form-msg" role="status" aria-live="polite" hidden></p></form>'''
    find = find_links(["tj-youtube", "tj-instagram", "tj-tiktok", "tj-facebook", "tj-imdb"]).replace("<li>", "").replace("</li>", "")
    content = f'''<div class="wrap ct"><h1>{esc(d["h1"])}</h1>
<div class="ct-l"><p class="lead rv" style="max-width:16ch">{esc(d["lead"])}</p>
<figure class="ct-pic rv">{img("tommy-boom-josh-camera", sizes="(min-width: 900px) 40vw, 100vw")}</figure></div>
<div>{form}<p class="find rv"><span class="ser">{esc(d["findLine"])}</span>{find}</p></div></div>'''
    ld = [website_ld(), person_ld(), {"@type": "ContactPage", "name": "Contact Tommy Jackett", "url": absu("/contact/"), "mainEntity": {"@id": absu("/") + "#person"}},
          breadcrumb_ld([("Contact", None)])]
    add("/contact/", d["metaTitle"], d["metaDescription"], content, og="salt-flats-tommy-wide", og_alt=IMAGES["salt-flats-tommy-wide"]["alt"], ld=ld, cls="contact-pg")


def build_404():
    d = PAGES["notFound"]
    content = f'<div class="wrap nf"><h1>{esc(d["h1"])}</h1><p class="lead">{esc(d["text"])}</p><div class="acts">{go("Home", "/")}{go("The doco", "/#doco")}</div></div>'
    add("/404.html", "Page not found | Tommy Jackett", "", content, og="salt-flats-tommy-wide", cls="nf-pg", noindex=True)


# ---------------------------------------------------------------- render
def render(p):
    path = p["path"]
    is404 = path.endswith("404.html")
    robots = "noindex, nofollow" if (not P["prod"] or p["noindex"] or is404) else "index, follow, max-image-preview:large"
    canon = absu(path)
    og = p["og"]
    im = IMAGES.get(og)
    if im and im.get("social"):
        og_url, ow, oh = absu("/img/" + im["social"]), 1200, 630
    elif im:
        og_url, ow, oh = img_abs(og, 1280), im["width"], im["height"]
    else:
        og_url, ow, oh = absu("/img/" + og), 1200, 630
    h = [f"<title>{esc(p['title'])}</title>"]
    if p["desc"]:
        h.append(f'<meta name="description" content="{esc(p["desc"])}">')
    h.append(f'<meta name="robots" content="{robots}">')
    if not is404:
        h.append(f'<link rel="canonical" href="{esc(canon)}">')
        h += [f'<meta property="og:site_name" content="{esc(SITE["name"])}">', '<meta property="og:type" content="website">',
              f'<meta property="og:title" content="{esc(p["title"])}">', f'<meta property="og:description" content="{esc(p["desc"])}">',
              f'<meta property="og:url" content="{esc(canon)}">', f'<meta property="og:image" content="{esc(og_url)}">',
              f'<meta property="og:image:width" content="{ow}">', f'<meta property="og:image:height" content="{oh}">',
              f'<meta property="og:image:alt" content="{esc(p["og_alt"] or SITE["name"])}">', f'<meta property="og:locale" content="{SITE["ogLocale"]}">',
              '<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:title" content="{esc(p["title"])}">',
              f'<meta name="twitter:description" content="{esc(p["desc"])}">', f'<meta name="twitter:image" content="{esc(og_url)}">']
    h += ['<meta name="theme-color" content="#0d0d0e">', '<meta name="color-scheme" content="dark">',
          f'<link rel="icon" type="image/png" sizes="48x48" href="{url("/icons/icon-48.png")}">',
          f'<link rel="icon" type="image/png" sizes="192x192" href="{url("/icons/icon-192.png")}">',
          f'<link rel="apple-touch-icon" href="{url("/icons/icon-180.png")}">',
          f'<link rel="preload" href="{url("/fonts/anton-400-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
          f'<link rel="preload" href="{url("/fonts/inter-variable-latin.woff2")}" as="font" type="font/woff2" crossorigin>']
    for pid in p["preload"]:
        i2 = IMAGES[pid]
        ss = ", ".join(f"{url('/img/' + i2['file'] + '-' + str(w) + '.webp')} {w}w" for w in i2["widths"])
        h.append(f'<link rel="preload" as="image" href="{url("/img/" + i2["file"] + "-" + str(max([w for w in i2["widths"] if w <= 1280] or i2["widths"])) + ".webp")}" imagesrcset="{ss}" imagesizes="100vw">')
    h.append(f'<link rel="stylesheet" href="{url("/assets/site.css")}?v={P["versions"]["css"]}">')
    h.append("<script>document.documentElement.classList.add('js')</script>")
    if p["ld"]:
        h.append(ld_script(p["ld"]))
    cur = p["cur"]
    page = f'''<!doctype html>
<html lang="{SITE["locale"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{chr(10).join(h)}
</head>
<body id="top" class="{p["cls"]}">
<a class="skip" href="#main">Skip to content</a>
{header(cur)}
<main id="main">
{typo_html(p["content"])}
</main>
{typo_html(footer(p["film_credit"]))}
<script src="{url("/assets/site.js")}?v={P["versions"]["js"]}" defer></script>
</body>
</html>
'''
    return page


# ---------------------------------------------------------------- machine files
def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {absu('/sitemap.xml')}\n" if P["prod"] else "User-agent: *\nDisallow: /\n"


def sitemap():
    rows = [f"  <url><loc>{esc(absu(p['path']))}</loc><lastmod>{p['lastmod']}</lastmod></url>" for p in PAGE_LIST if not p["path"].endswith("404.html")]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"


def llms():
    f = SITE["film"]
    L = ["# Tommy Jackett\n", f"> {SITE['entityStatement']}\n",
         (f"Facts that stay the same: In Guns We Trust is a {f['runtimeMinutes']} minute documentary, free on YouTube worldwide from Thursday 22 October 2026 at 8pm US Eastern "
          f"(Friday 23 October 2026 at 11am Melbourne time, AEDT). It is directed by Josh Janssen and made by 2A Film, Full Stack Films and Rethink Films. "
          f"Tommy Jackett co-hosts and co-wrote it. The film takes no side on guns.\n"),
         "## Pages", f"- [Home]({absu('/')}): who Tommy is and what he is making",
         f"- [The doco]({absu(f['sitePath'])}): In Guns We Trust, the documentary",
         f"- [Stories]({absu('/stories/')}): the stories he has told, in the order they happened",
         f"- [About]({absu('/about/')}): his bio and career, from breakfast radio to film",
         f"- [Work]({absu('/work/')}): VIDPOD, his video production company",
         f"- [Contact]({absu('/contact/')}): send a message\n", "## Stories"]
    for s in STORIES:
        if s.get("external"):
            L.append(f"- [{s['title']}]({resolve(s['external'])}): {s['indexLine']}")
        else:
            L.append(f"- [{s['title']}]({absu('/stories/' + s['slug'] + '/')}): {s['lede']}")
    L += ["", "## Elsewhere"] + [f"- [{l['label']}]({l['url']})" for l in LINKS if l["group"] == "tommy" and l.get("verified")]
    L += [f"- [The Daily Talk Show]({LINK['dts']['url']})", f"- [VIDPOD]({SITE['vidpod']['url']})", f"- [In Guns We Trust, official site]({LINK['film-site']['url']})", ""]
    return "\n".join(L)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    return re.sub(r"\s*([{};,>])\s*", r"\1", css).strip() + "\n"


# ---------------------------------------------------------------- checks
def checks(out, pages_html):
    errors, warnings = [], []
    titles, descs = {}, {}
    for p in PAGE_LIST:
        html = pages_html[p["path"]]
        pa = p["path"]
        if EMD in html:
            errors.append(f"{pa}: em dash in output")
        if len(re.findall(r"<h1[ >]", html)) != 1:
            errors.append(f"{pa}: needs exactly one h1")
        for m in re.finditer(r"<img [^>]*>", html):
            if " alt=" not in m.group(0):
                errors.append(f"{pa}: image without alt")
        if re.search(r"\[\[|\{\{", html):
            errors.append(f"{pa}: unresolved placeholder")
        for m in re.finditer(r'href="(mailto:[^"]+)"', html):
            if "ingunswetrustfilm.com" not in m.group(1) or pa != SITE["film"]["sitePath"]:
                errors.append(f"{pa}: mailto link {m.group(1)} (only the film's own addresses, on the film page)")
        if re.search(r"tel:|@tommyjackett\.com|x\.com/tommyjackett|\bNotes\b|\bCracks\b", html):
            errors.append(f"{pa}: contains a banned item (phone, email, X link, Notes or Cracks)")
        if not p["path"].endswith("404.html"):
            if p["title"] in titles:
                errors.append(f"{pa}: duplicate title with {titles[p['title']]}")
            titles[p["title"]] = pa
            if p["desc"] in descs:
                errors.append(f"{pa}: duplicate description with {descs[p['desc']]}")
            descs[p["desc"]] = pa
        rob = re.search(r'name="robots" content="([^"]+)"', html).group(1)
        if not P["prod"] and "noindex" not in rob:
            errors.append(f"{pa}: staging page lacks noindex")
        if P["prod"] and "noindex" in rob and not pa.endswith("404.html"):
            errors.append(f"{pa}: root page has noindex")
        for m in re.finditer(r'(?:href|src)="([^"#?]+)', html):
            u = m.group(1)
            if u.startswith(P["base"] + "/") or (P["base"] == "" and u.startswith("/")):
                rel = u[len(P["base"]):].lstrip("/")
                tgt = os.path.join(out, rel)
                if not (os.path.isfile(tgt) or os.path.isfile(os.path.join(tgt, "index.html"))):
                    errors.append(f"{pa}: dead internal link {u}")
        # srcset
        for m in re.finditer(r'srcset="([^"]+)"', html):
            for part in m.group(1).split(","):
                u = part.strip().split(" ")[0]
                rel = u[len(P["base"]):].lstrip("/")
                if not os.path.isfile(os.path.join(out, rel)):
                    errors.append(f"{pa}: missing image {u}")
    # source scan
    for dp, _, fns in os.walk(ROOT):
        parts = os.path.relpath(dp, ROOT).split(os.sep)
        if any(x in parts for x in (".git", "public", "node_modules", "__pycache__")):
            continue
        for fn in fns:
            if fn.endswith((".json", ".css", ".js", ".py", ".html", ".md", ".sh", ".yml")):
                try:
                    txt = open(os.path.join(dp, fn), encoding="utf-8").read()
                except Exception:
                    continue
                if EMD in txt:
                    errors.append(f"em dash in source: {os.path.relpath(os.path.join(dp, fn), ROOT)}")
                if "/Users/" in txt and fn.endswith(".json"):
                    errors.append(f"local /Users/ path in data: {os.path.relpath(os.path.join(dp, fn), ROOT)}")
    return errors, warnings


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="store_true")
    ap.add_argument("--machine", action="store_true")
    ap.add_argument("--base-path", default=None)
    ap.add_argument("--site-url", default=None)
    ap.add_argument("--out", default="public")
    ap.add_argument("--state", choices=["before", "after"], default=None)
    a = ap.parse_args()

    if a.root and (not FORM["accessKey"] or FORM["accessKey"] == FORM["placeholder"]):
        print("REFUSING TO BUILD for the root domain: data/form.json still has the placeholder Web3Forms key.")
        print("Create a new Web3Forms form for tommyjackett.com, paste its access key into data/form.json (accessKey), then run this again.")
        sys.exit(1)

    u = SITE["urls"]
    P["prod"] = a.root
    P["base"] = ("" if a.base_path is None else a.base_path) if a.root else (u["stagingBasePath"] if a.base_path is None else a.base_path)
    P["url"] = ((a.site_url or u["production"]) if a.root else (a.site_url or u["staging"])).rstrip("/")
    P["bake_after"] = a.state == "after"

    out = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    css = minify_css(open(os.path.join(ROOT, "src", "css", "site.css"), encoding="utf-8").read())
    js = open(os.path.join(ROOT, "src", "js", "site.js"), encoding="utf-8").read()
    P["versions"] = {"css": hashlib.md5(css.encode()).hexdigest()[:8], "js": hashlib.md5(js.encode()).hexdigest()[:8]}

    build_home(); build_404()

    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    rendered = {}
    for p in PAGE_LIST:
        html = render(p)
        rendered[p["path"]] = html
        dest = os.path.join(out, p["path"].lstrip("/"))
        if p["path"].endswith("/"):
            dest = os.path.join(dest, "index.html")
        write(dest, html)
    shutil.copytree(os.path.join(ROOT, "src", "fonts"), os.path.join(out, "fonts"), ignore=shutil.ignore_patterns("*.md"))
    # ship only the images the built pages and the stylesheet actually use
    used = set()
    for html in list(rendered.values()) + [css]:
        used.update(re.findall(r"/img/([A-Za-z0-9._-]+\.(?:webp|jpg|png))", html))
    os.makedirs(os.path.join(out, "img"))
    for fn in sorted(used):
        shutil.copy(os.path.join(ROOT, "src", "img", fn), os.path.join(out, "img", fn))
    if os.path.isdir(os.path.join(ROOT, "src", "icons")):
        shutil.copytree(os.path.join(ROOT, "src", "icons"), os.path.join(out, "icons"))
    if os.path.exists(os.path.join(out, "icons", "icon-48.png")):
        shutil.copy(os.path.join(out, "icons", "icon-48.png"), os.path.join(out, "favicon.ico"))
    write(os.path.join(out, "assets", "site.css"), css)
    write(os.path.join(out, "assets", "site.js"), js)
    write(os.path.join(out, "robots.txt"), robots())
    write(os.path.join(out, ".nojekyll"), "")
    if a.root or a.machine:
        write(os.path.join(out, "sitemap.xml"), sitemap())
        write(os.path.join(out, "llms.txt"), llms())
    if a.root:
        write(os.path.join(out, "CNAME"), "tommyjackett.com\n")
    errors, warnings = checks(out, rendered)
    print(f"Built {len(PAGE_LIST)} pages [{'ROOT (go-live)' if a.root else 'STAGING'}] base_path={P['base'] or '(none)'} site_url={P['url']} launch_state={'after (baked)' if P['bake_after'] else 'switches on the client'}")
    for w in warnings:
        print("  warn:", w)
    for e in errors:
        print("  ERROR:", e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
