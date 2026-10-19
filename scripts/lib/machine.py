"""Machine files: robots.txt, sitemap.xml, llms.txt, feed.xml, CNAME."""
import os

from . import notes_body
from .core import esc, fmt_date, rfc822, typo


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def robots(ctx):
    if ctx.production:
        return f"User-agent: *\nAllow: /\n\nSitemap: {ctx.abs('/sitemap.xml')}\n"
    return "User-agent: *\nDisallow: /\n"


def sitemap(ctx):
    rows = []
    for p in ctx.pages:
        if p["path"].endswith("404.html") or p.get("in_sitemap") is False or p.get("noindex"):
            continue
        lm = f"<lastmod>{p['lastmod'][:10]}</lastmod>" if p.get("lastmod") else ""
        rows.append(f"  <url><loc>{esc(ctx.abs(p['path']))}</loc>{lm}</url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"


def llms(ctx):
    s, f = ctx.site, ctx.site["film"]
    L = []
    L.append("# Tommy Jackett\n")
    L.append(f"> {s['entityStatement']}\n")
    L.append(
        f"Facts that stay the same: his name is Tommy Jackett. In Guns We Trust is a {f['runtimeMinutes']} minute documentary, free on YouTube worldwide "
        f"from Thursday 22 October 2026 at 8pm US Eastern (Friday 23 October 2026 at 11am Melbourne time, AEDT). Tommy's credits on the film are featuring, "
        f"co-host and story by. The film is directed by Josh Janssen and made by {', '.join(f['productionCompanies'][:-1])} and {f['productionCompanies'][-1]}. "
        f"The film takes no side on guns.\n")
    L.append("## About Tommy")
    L.append(f"- [About Tommy Jackett]({ctx.abs('/about/')}): who he is, in his own words")
    L.append(f"- [Contact]({ctx.abs('/contact/')}): how to reach him for video, podcasts, screenings and press\n")
    L.append("## The film")
    L.append(f"- [In Guns We Trust, Tommy Jackett's page]({ctx.abs(f['sitePath'])}): his part in the film, the stills and the answers to common questions")
    L.append(f"- [In Guns We Trust, official site]({ctx.links_all['film-site']['url']}/): the film's own site, press kit and resources")
    L.append(f"- [Watch on YouTube]({ctx.watch_url}): the film's YouTube channel")
    L.append(f"- [IMDb]({ctx.links_all['film-imdb']['url']})\n")
    L.append("## Stories")
    L.append(f"- [All stories]({ctx.abs('/stories/')}): the videos Tommy has made and how each came together")
    for st in ctx.stories:
        if st.get("isFilm"):
            continue
        L.append(f"- [{st['title']}]({ctx.abs(ctx.story_href(st))}): {ctx.plain(st['indexLine'])}")
    L.append("")
    L.append("## Work with Tommy")
    L.append(f"- [Work]({ctx.abs('/work/')}): video and podcast production through VIDPOD")
    L.append(f"- [VIDPOD]({s['vidpod']['url']})\n")
    L.append("## Notes")
    L.append(f"- [Notes]({ctx.abs('/notes/')}): ideas and behind the scenes")
    for n in ctx.notes:
        n = ctx.note(n)
        L.append(f"- [{n['title']}]({ctx.abs('/notes/' + n['slug'] + '/')}): {ctx.plain(n['summary'])}")
    L.append("")
    L.append("## Elsewhere")
    for l in ctx.links_in("tommy"):
        L.append(f"- [{l['label']}]({l['url']})")
    L.append(f"- [The Daily Talk Show]({ctx.links_all['dts']['url']})\n")
    L.append("## Optional")
    L.append(f"- [RSS feed]({ctx.abs('/feed.xml')})")
    L.append(f"- [Sitemap]({ctx.abs('/sitemap.xml')})\n")
    return "\n".join(L)


def feed(ctx):
    items = []
    for n in ctx.notes:
        n = ctx.note(n)
        url = ctx.abs(f"/notes/{n['slug']}/")
        body = notes_body.render(ctx, n["body"], feed=True)
        # md() resolves internal links with the base path; make them absolute for readers
        body = body.replace('href="' + ctx.base_path + '/', 'href="' + ctx.site_url + '/')
        items.append(
            f"<item><title>{esc(n['title'])}</title><link>{esc(url)}</link><guid isPermaLink=\"true\">{esc(url)}</guid>"
            f"<pubDate>{rfc822(n['date'])}</pubDate><description>{esc(ctx.plain(n['summary']))}</description>"
            f"<content:encoded><![CDATA[{body}]]></content:encoded></item>")
    last = rfc822(ctx.notes[0]["date"]) if ctx.notes else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">\n<channel>\n'
            f"<title>Notes by Tommy Jackett</title><link>{esc(ctx.abs('/notes/'))}</link>"
            "<description>Things I'm working on, trying out and figuring out about video, stories and making films.</description>"
            f"<language>en-au</language><lastBuildDate>{last}</lastBuildDate>"
            f'<atom:link href="{esc(ctx.abs("/feed.xml"))}" rel="self" type="application/rss+xml"/>\n'
            + "\n".join(items) + "\n</channel>\n</rss>\n")
