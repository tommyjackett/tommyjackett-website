"""Contact: the form, the email, the film team and every verified profile. Copy from copy-deck.md section 6, data/contact.json."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cwa  # noqa: E402
from lib import components as C  # noqa: E402
from lib import jsonld  # noqa: E402
from lib.core import esc  # noqa: E402

PATH = "/contact/"


def build(ctx):
    d = _cwa.load("contact")
    s = ctx.site
    email = s["email"]
    trail = [("Contact", None)]
    labels = d.get("labels", {})

    rows = []
    for g in d["groups"]:
        links = "".join(f"<li>{ctx.a(i, labels.get(i))}</li>" for i in g["ids"] if ctx.link(i))
        if links:
            rows.append(f'<div class="ct-row reveal"><h3>{esc(g["label"])}</h3><ul>{links}</ul></div>')

    head = f'''<section class="page-head wrap ct-head">
  {C.breadcrumbs_html(ctx, trail)}
  <h1 class="display ct-h1">{esc(d["h1"])}</h1>
  <p class="page-lede reveal">{esc(d["lead"])}</p>
</section>'''

    main = f'''<section class="wrap ct-main" aria-label="Send me a message">
  <div class="ct-form reveal">
    {_cwa.sent_banner(d["sent"])}
    {_cwa.form(ctx, PATH)}
  </div>
  <aside class="ct-side reveal" style="--d:.1s" aria-label="Other ways to reach me">
    <p class="ct-email">{esc(d["emailLine"])} <a href="mailto:{esc(email)}">{esc(email)}</a></p>
    <p class="ct-film">{ctx.md(d["filmTeam"])}</p>
    <figure class="ct-photo">{ctx.img("tommy-portrait-mono", sizes="(min-width: 900px) 30vw, 70vw")}<figcaption class="small">{esc(ctx.credit("tommy-portrait-mono"))}</figcaption></figure>
  </aside>
</section>'''

    find = f'''<section class="wrap sx ct-find" aria-labelledby="ct-find-h">{_cwa.label("01", "Find me").replace("<h2 ", '<h2 id="ct-find-h" ', 1)}
  <div class="sx-body"><p class="sx-p reveal">{esc(d["findLine"])}</p><div class="ct-rows">{"".join(rows)}</div></div></section>'''

    content = "\n".join([head, main, find])
    graph = [jsonld.website(ctx), jsonld.person(ctx), jsonld.vidpod(ctx), jsonld.contact_page(ctx, PATH, d["metaTitle"]), jsonld.breadcrumb(ctx, trail)]
    ctx.add_page(PATH, d["metaTitle"], d["metaDescription"], content,
                 og_image=s["images"]["ogHome"], og_alt="Tommy Jackett smiling in a black bomber jacket",
                 jsonld=graph, body_class="p-contact", lastmod="2026-10-20")
