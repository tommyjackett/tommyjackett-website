"""About: 'Hey, I'm Tommy.' Copy from copy-deck.md section 5, mirrored in data/about.json."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cwa  # noqa: E402
from lib import components as C  # noqa: E402
from lib import jsonld  # noqa: E402
from lib.core import esc  # noqa: E402

PATH = "/about/"


def film_when_sentence(ctx):
    """The full launch sentence, started with 'It's' so it follows the film name. Flips on the launch date."""
    full = ctx.film_when("full")
    return full.replace("In Guns We Trust is ", "It's ", 1)


def build(ctx):
    d = _cwa.load("about")
    s = ctx.site
    trail = [("About", None)]
    body = [t.replace("%FILM_WHEN%", film_when_sentence(ctx)) for t in d["body"]]

    portrait = ctx.img("tommy-portrait-close", sizes="(min-width: 1440px) 1300px, 100vw", priority=True)
    flats = ctx.img("salt-flats-tommy-chair", sizes="(min-width: 900px) 34vw, 100vw")

    head = f'''<section class="page-head wrap ab-head">
  {C.breadcrumbs_html(ctx, trail)}
  <h1 class="display ab-h1">{esc(d["h1"])}</h1>
</section>
<div class="wrap"><figure class="ab-portrait">{portrait}<figcaption class="small">{esc(ctx.credit("tommy-portrait-close"))}</figcaption></figure></div>'''

    links = "".join(f'<li>{C.link_go(ctx, l["label"], l["target"], cls="ab-go link-go")}</li>' for l in d["links"])
    story = f'''<section class="wrap ab-story" aria-label="About Tommy">
  <div class="ab-story-text">
    <p class="ab-lead reveal">{ctx.md(d["lead"])}</p>
    <p class="ab-p reveal">{ctx.md(body[0])}</p>
    <p class="ab-p reveal">{ctx.md(body[1])}</p>
    <p class="ab-p reveal">{ctx.md(body[2])}</p>
    <ul class="ab-links reveal">{links}</ul>
  </div>
  <figure class="ab-flats reveal">{flats}<figcaption class="small">{esc(ctx.credit("salt-flats-tommy-chair"))}</figcaption></figure>
</section>'''

    short = f'''<section class="wrap sx" aria-labelledby="ab-short">{_cwa.label("01", d["shortVersionLabel"]).replace("<h2 ", '<h2 id="ab-short" ', 1)}
  <div class="sx-body"><p class="ab-short reveal">{esc(s["entityStatement"])}</p></div></section>'''

    faq_rows = "".join(
        f'<details><summary>{esc(q)}</summary><p>{ctx.md(a)}</p></details>' for q, a in d["faq"])
    faq = f'''<section class="wrap sx" aria-labelledby="ab-faq">{_cwa.label("02", d["faqLabel"]).replace("<h2 ", '<h2 id="ab-faq" ', 1)}
  <div class="sx-body"><div class="faq reveal">{faq_rows}</div></div></section>'''

    elsewhere = "".join(f"<li>{ctx.a(i)}</li>" for i in ("tj-youtube", "tj-instagram", "tj-tiktok", "tj-facebook", "tj-x", "tj-imdb", "vidpod", "dts") if ctx.link(i))
    find = f'''<section class="wrap sx" aria-labelledby="ab-find">{_cwa.label("03", "Elsewhere").replace("<h2 ", '<h2 id="ab-find" ', 1)}
  <div class="sx-body"><ul class="ab-elsewhere reveal">{elsewhere}</ul></div></section>'''

    content = "\n".join([head, story, short, faq, find])

    graph = [
        jsonld.website(ctx), jsonld.person(ctx), jsonld.vidpod(ctx),
        jsonld.profile_page(ctx, PATH, "2026-10-19", "2026-10-20"),
        jsonld.faq(ctx, [(q, ctx.plain(a)) for q, a in d["faq"]]),
        jsonld.breadcrumb(ctx, trail),
    ]
    ctx.add_page(PATH, d["metaTitle"], d["metaDescription"], content,
                 og_image=s["images"]["ogHome"], og_alt="Tommy Jackett smiling in a black bomber jacket",
                 jsonld=graph, body_class="p-about", preload=["tommy-portrait-close"], preload_sizes="(min-width: 1440px) 1300px, 100vw",
                 lastmod="2026-10-20")
