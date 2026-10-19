"""404 page. Plain, in his voice. Noindex, no canonical."""
from lib import components as C


def build(ctx):
    content = f'''<section class="page-head wrap"><h1 class="display">Nothing here.</h1>
  <p class="page-lede">Either I’ve moved things around or that link has a typo. Probably me. The way back is below.</p>
  <div class="btn-row" style="margin-top:var(--s-4)">{C.btn(ctx, "Home", "/")}{C.btn(ctx, "Watch the film", "film:watch", "ghost")}</div></section>
<div style="height:var(--s-5)"></div>'''
    ctx.add_page("/404.html", ctx.site["notFound"]["title"], "", content, noindex=True, canonical=False, in_sitemap=False, no_closer=True)
