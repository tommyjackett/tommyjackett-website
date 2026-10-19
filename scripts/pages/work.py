"""Work with me: video and podcast production through VIDPOD. Copy from copy-deck.md section 4, mirrored in data/work.json."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cwa  # noqa: E402
from lib import components as C  # noqa: E402
from lib import jsonld  # noqa: E402
from lib.core import esc  # noqa: E402

PATH = "/work/"


def build(ctx):
    d = _cwa.load("work")
    sent = _cwa.load("contact")["sent"]
    s = ctx.site
    email = s["email"]
    vp = ctx.link("vidpod")
    trail = [("Work", None)]

    def ps(items):
        return "".join(f'<p class="sx-p reveal" style="--d:{i * 0.07:.2f}s">{ctx.md(t)}</p>' for i, t in enumerate(items))

    def sec(n, text, body, cls="", sid=""):
        h = _cwa.label(n, text).replace("<h2 ", f'<h2 id="wk-{n}" ', 1)
        ident = f' id="{sid}"' if sid else ""
        return f'<section class="wrap sx {cls}"{ident} aria-labelledby="wk-{n}">{h}<div class="sx-body">{body}</div></section>'

    head = f'''<section class="page-head wrap wk-head">
  {C.breadcrumbs_html(ctx, trail)}
  <h1 class="display">{esc(d["h1"])}</h1>
  <p class="page-lede reveal">{ctx.md(d["lead"])}</p>
  <div class="btn-row wk-act reveal" style="--d:.1s">{C.btn(ctx, "Get in touch", "#talk")}{C.btn(ctx, "Go to VIDPOD", "link:vidpod", "ghost")}</div>
</section>'''
    media = (f'<div class="wrap"><figure class="wk-media reveal">{ctx.img("tommy-camera-harbour", sizes="(min-width: 1440px) 1300px, 100vw")}'
             f'<figcaption class="small">{esc(ctx.credit("tommy-camera-harbour"))}. On a shoot by the harbour.</figcaption></figure></div>')

    vidpod = ps(d["vidpod"]) + f'<p class="sx-links reveal">{C.link_go(ctx, "Go to VIDPOD", "link:vidpod")}{C.link_go(ctx, "The VIDPOD story page", "link:vidpod-story")}</p>'
    make = ps(d["make"])
    shows = ps(d["showsIntro"]) + '<ul class="wk-shows reveal">' + "".join(
        f'<li><span class="wk-show">{esc(x["show"])}</span>' + (f'<span class="wk-for">{esc(x["for"])}</span>' if x["for"] else "") + "</li>"
        for x in d["shows"]) + "</ul>"
    how = ps(d["how"])
    talk = (f'<p class="sx-p reveal">{ctx.md(d["close"])}</p>'
            f'<div class="reveal" style="--d:.08s">{_cwa.sent_banner(sent)}{_cwa.form(ctx, PATH)}</div>'
            f'<p class="small sx-after">Prefer email? Write to me directly. <a href="mailto:{esc(email)}">{esc(email)}</a></p>'
            f'<p class="sx-links reveal">{C.link_go(ctx, "Go to VIDPOD", "link:vidpod")}</p>')

    content = "\n".join([
        head, media,
        sec("01", "VIDPOD", vidpod),
        sec("02", "What I make", make),
        sec("03", "Shows", shows),
        sec("04", "How it goes", how),
        sec("05", "Get in touch", talk, cls="wk-talk", sid="talk"),
    ])

    graph = [
        jsonld.website(ctx), jsonld.person(ctx), jsonld.vidpod(ctx),
        jsonld.web_page(ctx, PATH, d["metaTitle"], d["metaDescription"], ctx.id_url("vidpod")),
        {"@type": "Service", "@id": ctx.abs(PATH) + "#service", "name": "Video and podcast production",
         "serviceType": ["Video production", "Podcast production"],
         "description": "Brand films, founder stories, case studies, testimonials, explainers, social content and animation, plus podcast recording, editing and launch.",
         "provider": [{"@id": ctx.id_url("person")}, {"@id": ctx.id_url("vidpod")}],
         "areaServed": {"@type": "City", "name": "Melbourne"},
         "url": ctx.abs(PATH), "sameAs": vp["url"] if vp else s["vidpod"]["url"]},
        jsonld.breadcrumb(ctx, trail),
    ]
    ctx.add_page(PATH, d["metaTitle"], d["metaDescription"], content,
                 og_image="tommy-camera-harbour", og_alt="Tommy Jackett smiling beside a cinema camera on a harbour shoot",
                 jsonld=graph, body_class="p-work", lastmod="2026-10-20")
