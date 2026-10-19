"""Core of the tommyjackett.com build: config, data, URL helpers, text helpers, page writer.

Dependency-free. Every page module in scripts/pages/ receives a Ctx and calls ctx.add_page(...).
"""
import datetime
import hashlib
import html as _html
import json
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def esc(s):
    return _html.escape(str(s), quote=True)


# ---------------------------------------------------------------- typography
def typo(s):
    """Curly quotes and apostrophes. Applied to text only, never to URLs or JSON."""
    s = re.sub(r"(?<=\w)'(?=\w)", "\u2019", s)               # don't, Domino's
    s = re.sub(r"(^|[\s(\[])'(?=\d)", lambda m: m.group(1) + "\u2019", s)  # '70s
    s = re.sub(r"(^|[\s(\[])'", lambda m: m.group(1) + "\u2018", s)        # opening single
    s = s.replace("'", "\u2019")
    s = re.sub(r'(^|[\s(\[])"', lambda m: m.group(1) + "\u201c", s)
    s = s.replace('"', "\u201d")
    return s


def typo_html(h):
    """Apply typo() to the text nodes of an HTML fragment (skips script, style, pre and tags)."""
    parts = re.split(r"(<script.*?</script>|<style.*?</style>|<pre.*?</pre>|<[^>]+>)", h, flags=re.S)
    for i in range(0, len(parts), 2):
        t = parts[i]
        if t and ("'" in t or '"' in t or "&#x27;" in t or "&quot;" in t or "&#39;" in t):
            parts[i] = _html.escape(typo(_html.unescape(t)), quote=False)
    return "".join(parts)


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def fmt_date(d):
    """'2026-10-19' -> '19 October 2026'"""
    y, m, dd = [int(x) for x in d[:10].split("-")]
    return f"{dd} {MONTHS[m - 1]} {y}"


def _first_sunday(y, m):
    d = datetime.date(y, m, 1)
    return d + datetime.timedelta(days=(6 - d.weekday()) % 7)


def melbourne_offset(d):
    """+11:00 from the first Sunday in October to the first Sunday in April, else +10:00."""
    y, m, dd = [int(x) for x in d[:10].split("-")]
    day = datetime.date(y, m, dd)
    if _first_sunday(y, 4) <= day < _first_sunday(y, 10):
        return "+10:00"
    return "+11:00"


def iso_melbourne(d, hhmm="09:00"):
    return f"{d[:10]}T{hhmm}:00{melbourne_offset(d)}"


def rfc822(d):
    y, m, dd = [int(x) for x in d[:10].split("-")]
    dt = datetime.date(y, m, dd)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    off = melbourne_offset(d).replace(":", "")
    return f"{days[dt.weekday()]}, {dd:02d} {MONTHS[m - 1][:3]} {y} 09:00:00 {off}"


class Ctx:
    def __init__(self, production=False, base_path=None, site_url=None, out="public", machine=False, state=None):
        self.production = production
        self.machine = machine
        self.machine_files = production or machine
        self.out = os.path.join(ROOT, out)
        self.data = {}
        for name in ("site", "stories", "notes", "links", "images", "videos", "form"):
            p = os.path.join(ROOT, "data", f"{name}.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    self.data[name] = json.load(f)
        self.site = self.data["site"]
        self.stories = self.data.get("stories", [])
        self.notes = sorted(self.data.get("notes", []), key=lambda n: n["date"], reverse=True)
        self.videos = self.data.get("videos", [])
        self.form = self.data.get("form", {})
        self.images = {i["id"]: i for i in self.data["images"]}
        self.links_all = {l["id"]: l for l in self.data["links"]}
        u = self.site["urls"]
        if production:
            self.base_path = "" if base_path is None else base_path
            self.site_url = (site_url or u["production"]).rstrip("/")
        else:
            self.base_path = u["stagingBasePath"] if base_path is None else base_path
            self.site_url = (site_url or u["staging"]).rstrip("/")
        self.pages = []
        self.warnings = []
        self._hash_cache = {}
        launch = datetime.datetime.fromisoformat(self.site["film"]["launchISO"])
        if state in ("before", "after"):
            self.is_live = state == "after"
        else:
            self.is_live = datetime.datetime.now(datetime.timezone.utc) >= launch

    # ------------------------------------------------------------ urls
    def url(self, path):
        """Internal path ('/stories/') -> URL including BASE_PATH. External URLs pass through."""
        if re.match(r"^(https?:|mailto:|tel:|#)", path):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.base_path + path

    def abs(self, path):
        """Absolute canonical URL for an internal path."""
        if re.match(r"^https?:", path):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.site_url + path

    def resolve(self, target):
        """Resolve a data-file link target: 'film:watch', 'link:<id>', '/path/', or a full URL."""
        if target == "film:watch":
            return self.watch_url
        if target.startswith("link:"):
            return self.links_all[target[5:]]["url"]
        return self.url(target)

    def asset(self, rel):
        v = getattr(self, "versions", {}).get(rel)
        return self.url("/assets/" + rel) + (f"?v={v}" if v else "")

    def id_url(self, frag):
        return self.abs("/") + "#" + frag

    # ------------------------------------------------------------ film / launch state
    @property
    def watch_url(self):
        return self.site["film"]["watchUrl"]

    def film_when(self, kind="short"):
        key = "whenShort" if kind == "short" else "whenFull"
        return self.site["film"][key]["after" if self.is_live else "before"]

    # ------------------------------------------------------------ links
    def link(self, id):
        """A verified link dict, or None when unverified or missing. Never publish unverified links."""
        l = self.links_all.get(id)
        if l and l.get("verified"):
            return l
        return None

    def links_in(self, group):
        return [l for l in self.links_all.values() if l["group"] == group and l.get("verified")]

    def same_as(self):
        return [l["url"] for l in self.links_all.values() if l.get("verified") and l.get("sameAs")]

    def a(self, id, label=None, cls="", extra=""):
        """Anchor for a verified link by id; returns '' if held back."""
        l = self.link(id)
        if not l:
            return ""
        c = f' class="{cls}"' if cls else ""
        return f'<a{c} href="{esc(l["url"])}"{(" " + extra) if extra else ""}>{esc(label or l["label"])}</a>'

    # ------------------------------------------------------------ inline text
    def md(self, s):
        """Tiny inline markup for data strings: [label](target), **bold**, [[gap]]. Returns safe HTML."""
        out, pos = [], 0
        tok = re.compile(r"\[\[(.+?)\]\]|\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*")
        for m in tok.finditer(s):
            out.append(esc(typo(s[pos:m.start()])))
            if m.group(1) is not None:
                if self.production:
                    self.warnings.append(f"GAP in production build: [[{m.group(1)}]]")
                out.append(f'<mark class="gap">[[{esc(m.group(1))}]]</mark>')
            elif m.group(2) is not None:
                href = self.resolve(m.group(3))
                out.append(f'<a href="{esc(href)}">{esc(typo(m.group(2)))}</a>')
            else:
                out.append(f"<strong>{esc(typo(m.group(4)))}</strong>")
            pos = m.end()
        out.append(esc(typo(s[pos:])))
        return "".join(out)

    def plain(self, s):
        """Plain text version of a data string (for meta, JSON-LD, RSS). No curly quotes in JSON-LD."""
        s = re.sub(r"\[\[(.+?)\]\]", "", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)
        return re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()

    # ------------------------------------------------------------ images
    def img_url(self, id, width=None):
        im = self.images[id]
        ws = im["widths"]
        w = width if width in ws else (max([x for x in ws if x <= 1280] or ws))
        return self.url(f"/img/{im['file']}-{w}.webp")

    def img_abs(self, id, width=None):
        return self.abs(self.img_url(id, width)[len(self.base_path):])

    def img(self, id, sizes="100vw", cls="", loading="lazy", priority=False, alt=None, focal=True, style=""):
        im = self.images[id]
        ws = im["widths"]
        srcset = ", ".join(f"{self.url('/img/' + im['file'] + '-' + str(w) + '.webp')} {w}w" for w in ws)
        src = self.img_url(id)
        st = []
        if focal and im.get("focal"):
            st.append(f"object-position:{im['focal']}")
        if style:
            st.append(style)
        attrs = [
            f'src="{src}"', f'srcset="{srcset}"', f'sizes="{esc(sizes)}"',
            f'width="{im["width"]}"', f'height="{im["height"]}"',
            f'alt="{esc(im["alt"] if alt is None else alt)}"',
        ]
        if cls:
            attrs.append(f'class="{cls}"')
        if priority:
            attrs += ['loading="eager"', 'fetchpriority="high"']
        else:
            attrs.append(f'loading="{loading}"')
        attrs.append('decoding="async"')
        if st:
            attrs.append(f'style="{";".join(st)}"')
        return "<img " + " ".join(attrs) + ">"

    def credit(self, id):
        return self.images[id].get("credit", "")

    # ------------------------------------------------------------ files
    def file_hash(self, path):
        if path not in self._hash_cache:
            with open(path, "rb") as f:
                self._hash_cache[path] = hashlib.md5(f.read()).hexdigest()[:8]
        return self._hash_cache[path]

    # ------------------------------------------------------------ notes and stories
    def note(self, n):
        """A note with the after-launch swap applied when the film is live. Returns a new dict."""
        n = dict(n)
        al = n.get("afterLaunch")
        if al and self.is_live:
            for k in ("title", "metaTitle", "summary", "metaDescription"):
                if al.get(k):
                    n[k] = al[k]
            body = []
            for para in n["body"]:
                for a, b in al.get("bodyReplace", []):
                    para = para.replace(a, b)
                body.append(para)
            n["body"] = body
        return n

    def story(self, slug):
        return next((x for x in self.stories if x["slug"] == slug), None)

    def story_href(self, st):
        return st.get("href") or f"/stories/{st['slug']}/"

    # ------------------------------------------------------------ pages
    def add_page(self, path, title, description, content, **kw):
        """Register a page. path: '/' or '/stories/' (folder URL) or '/404.html'.

        kw: og_image (image id or filename in img/), og_alt, og_type, jsonld (list of dicts for @graph),
            body_class, noindex, canonical (bool), in_sitemap (bool), lastmod, preload (list of image ids),
            head_extra (raw html), article (dict for article:* tags)
        """
        self.pages.append(dict(path=path, title=title, description=description, content=content, **kw))
