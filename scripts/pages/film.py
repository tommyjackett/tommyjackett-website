"""The film page: /in-guns-we-trust/. Tommy's first-person side of the film. Copy from copy-deck.md section 2.

Rules held here: film images carry no filter, overlay or text, a credit sits under every film image,
the content note sits beside every watch button, both time zones wherever the date is given.
Styles: src/css/pages/film-stories.css (the .fp-* classes).
"""
from lib import components as C
from lib import jsonld
from lib.core import esc

QUOTE_NEUTRAL = "I feel like, from where we're from, we're not thinking about guns, so I feel like I'm neutral at this moment."
QUOTE_ARMOURER = ("My gun experience is that I watch a lot of movies, so I know what I see, but I don't know physically, "
                  "because I don't have access to them like that.")

# Stills in mosaic order. The hosts frame (UCLA) is the image in "My part", so the set here is the other five plus
# the Santa Monica Pier, which has no person or firearm in it. Each id maps to a layout slot (.fp-still--<slot>).
STILLS = [
    ("igwt-road-into-colorado", "road"),
    ("igwt-tommy-supermarket-trolley", "trolley"),
    ("igwt-barbecue-texas", "barbecue"),
    ("igwt-watching-planes-lax", "planes"),
    ("igwt-santa-monica-pier-sunset", "pier"),
    ("igwt-tommy-josh-under-flag", "flag"),
]


def faq_items(ctx):
    s = ctx.site
    when = ("from Thursday 22 October 2026 at 8pm ET (Friday 23 October, 11am AEDT)" if not ctx.is_live
            else "since Thursday 22 October 2026 at 8pm ET (Friday 23 October, 11am AEDT)")
    return [
        ("Who is Tommy Jackett?", s["entityStatement"]),
        ("When and where can I watch In Guns We Trust?",
         f"It's free on YouTube, worldwide, on the official channel @InGunsWeTrustFilm, {when}. "
         "There's no paywall and no registration, and YouTube may ask some viewers to sign in to confirm their age. "
         "It isn't on Netflix, Prime or Stan. We wanted as many people as possible to see it, so it's free."),
        ("What was Tommy Jackett's part in the film?",
         "I'm featured in it alongside Josh Janssen, and I'm credited as co-host and story by. "
         "On screen I'm one of the two Australians asking the questions."),
        ("Who directed and made it?",
         "Josh Janssen directed it. He's a Melbourne documentary filmmaker and the founder of Full Stack Films. "
         "It was produced by Jess Lucas and Breana Phillips for 2A Film Pty Ltd, Full Stack Films and Rethink Films, "
         "and it runs for 76 minutes."),
        ("Is it for or against guns?",
         "Neither. Josh and I set ourselves one rule: no side, no agenda, just conversations. "
         "Gun owners, survivors, a sheriff, researchers and families each speak for themselves. "
         "The aim isn't to change anyone's mind. It's to show that people who disagree can still sit down, "
         "ask honest questions and hear each other."),
        ("Why two Australians?",
         "We came as outsiders, from a country where guns rarely come up in daily life. "
         "Most of what Australians hear about guns in America arrives through news of mass shootings. "
         "Those stories are real, and the film doesn't look away from them, "
         "but they leave out most of the people who live with guns every day."),
        ("Is it suitable for students or children?",
         "The film includes gunfire and conversations about mass shootings, suicide and loss. "
         "It's made for adults and older teenagers watching with support. "
         "Educators should preview it first and consider their group's needs."),
        ("Can I host a screening?",
         "Yes, and we'd love you to. Anyone can host a free screening at home, on campus, at a library or in a community group. "
         "The discussion guide is free to print. Email screenings@ingunswetrustfilm.com, "
         "or see the resources page on the film's site."),
    ]


def watch_block(ctx, site_link=True):
    f = ctx.site["film"]
    more = C.link_go(ctx, "Visit the film's site", "link:film-site") if site_link else ""
    return (f'<div class="btn-row">{C.btn(ctx, "Watch on YouTube", "film:watch")}{more}</div>'
            f'<p class="small fp-note">{esc(f["contentNote"])} {esc(f["supportInline"].replace("13 11 14", "13\u00a011\u00a014"))}</p>')


def head(ctx):
    f = ctx.site["film"]
    trail = [("In Guns We Trust", None)]
    row = []
    for lid, label in (("film-press", "Press kit"), ("film-resources", "Discussion guide"),
                       ("film-resources", "Host a screening"), ("film-imdb", "IMDb"),
                       ("film-instagram", "Instagram"), ("film-tiktok", "TikTok"), ("film-threads", "Threads")):
        a = ctx.a(lid, label)
        if a:
            row.append(f"<li>{a}</li>")
    art = ctx.img("igwt-key-art", sizes="100vw", focal=False, priority=True)
    return f'''<header class="fp-head wrap">
  {C.breadcrumbs_html(ctx, trail)}
  <div class="fp-grid">
    <h1 class="display fp-title">In Guns We Trust</h1>
    <div class="fp-intro">
      <p class="page-lede fp-lede">I'm in a documentary called In Guns We Trust, and you can watch it free.</p>
      <p class="fp-when">{esc(ctx.film_when("full"))} It runs {f["runtimeMinutes"]} minutes. Josh Janssen directed it and I'm in it with him.</p>
      {watch_block(ctx)}
    </div>
  </div>
  <ul class="fp-row" aria-label="The film, elsewhere">{"".join(row)}</ul>
</header>
<figure class="fp-art">
  {art}
  <figcaption class="wrap small">{esc(ctx.credit("igwt-key-art"))}</figcaption>
</figure>'''


def film_section(ctx):
    return f'''<section class="sec" id="film" aria-label="The film"><div class="wrap">
  {C.mark("01", "The film")}
  <div class="fp-two">
    <div class="fp-text">
      <p class="fp-big reveal">Josh and I love America. The food, the films, the bigger-is-better attitude. The one thing we've never understood is the guns. Australia rarely has to think about them, so neither of us had a position. We decided that might be the point.</p>
      <p class="reveal">So we crossed the country with cameras and one rule: no side, no agenda, just conversations. A Hollywood armourer, a Route 91 survivor, a Texas sheriff, a trauma surgeon, and a lot of people in between. More than thirty people speak for themselves in it. Josh and I do the asking.</p>
    </div>
    <div class="fp-quote reveal">
      <p class="fp-quote-in">Here's roughly where I started. Early on I say:</p>
      <blockquote><p>"{esc(QUOTE_NEUTRAL)}"</p></blockquote>
      <p class="fp-quote-out">The film doesn't tell you what to think. It's made to be talked about afterwards.</p>
    </div>
  </div>
</div></section>'''


def part_section(ctx):
    img = ctx.img("igwt-hosts-ucla-law-library", sizes="(min-width: 900px) 52vw, 100vw")
    return f'''<section class="sec band" id="part" aria-label="My part"><div class="wrap">
  {C.mark("02", "My part")}
  <div class="fp-part">
    <div class="fp-text">
      <p class="fp-big reveal">I'm featured in the film with Josh and credited as co-host and story by. On camera I'm the outsider, and I say so.</p>
      <p class="reveal">When I meet the armourer I tell him:</p>
      <blockquote class="fp-q2 reveal"><p>"{esc(QUOTE_ARMOURER)}"</p></blockquote>
      <p class="reveal">It's Josh's first feature and my first long-form film. He directed and I'm in it with him. Each of the people we met speaks for themselves, and we left them to.</p>
      <p class="small fp-credits reveal">Featuring Tommy Jackett and Josh Janssen. Tommy is credited as co-host and story by. Made by 2A Film, Full Stack Films and Rethink Films.</p>
    </div>
    <figure class="figure fp-part-img reveal">{img}
      <figcaption>{esc(ctx.images["igwt-hosts-ucla-law-library"]["caption"])}<span class="fp-credit">{esc(ctx.credit("igwt-hosts-ucla-law-library"))}</span></figcaption></figure>
  </div>
</div></section>'''


def stills_section(ctx):
    figs = []
    for iid, slot in STILLS:
        im = ctx.images[iid]
        sizes = "(min-width: 900px) 60vw, 100vw" if slot in ("road", "flag", "planes") else "(min-width: 900px) 40vw, 100vw"
        figs.append(f'''<figure class="figure fp-still fp-still--{slot} reveal">{ctx.img(iid, sizes=sizes)}
  <figcaption>{esc(im["caption"])}<span class="fp-credit">{esc(im["credit"])}</span></figcaption></figure>''')
    return f'''<section class="sec" id="stills" aria-labelledby="stills-h"><div class="wrap">
  {C.mark("03", "From the film")}
  <h2 class="display fp-h2 reveal" id="stills-h">Stills</h2>
  <div class="fp-mosaic">{"".join(figs)}</div>
  <p class="fp-more reveal">{C.link_go(ctx, "See all 58 stills on the film's site", "link:film-stills")}</p>
</div></section>'''


def links_section(ctx):
    rows = [
        ("film:watch", "Watch on YouTube", "The film's own channel, free."),
        ("link:film-site", "The film's site", "Credits, press kit and the story behind it."),
        ("link:film-press", "Press kit", "Synopsis, credits, poster and key art."),
        ("link:film-resources", "Discussion guide", "Twenty questions for a night in."),
        ("link:film-resources", "Host a screening", "Free, at home, on campus or in a library."),
        ("link:film-stills", "Stills", "58 captioned frames."),
        ("link:film-transcript", "Transcript", "The full text and subtitles."),
        ("link:film-imdb", "IMDb", "In Guns We Trust (2026)."),
    ]
    lis = []
    for target, label, line in rows:
        lis.append(f'<li><a href="{esc(ctx.resolve(target))}"><strong>{esc(label)}</strong><span>{esc(line)}</span></a></li>')
    follow = [ctx.a(i) for i in ("film-instagram", "film-tiktok", "film-facebook", "film-threads", "film-x")]
    follow = [x for x in follow if x]
    follow_txt = ", ".join(follow[:-1]) + " and " + follow[-1] if len(follow) > 1 else "".join(follow)
    mine = ctx.a("tj-imdb", "my IMDb page")
    return f'''<section class="sec band" id="links" aria-labelledby="links-h"><div class="wrap">
  {C.mark("04", "Everything about the film")}
  <div class="fp-links">
    <h2 class="display fp-h2 reveal" id="links-h">The film, elsewhere</h2>
    <div class="fp-links-main">
      <ul class="linklist fp-linklist reveal">{"".join(lis)}</ul>
      <p class="reveal">Follow the film: {follow_txt}.</p>
      <p class="small reveal">Journalists: the press kit and contacts are on the film's site. For interviews, screeners and stills write to <a href="mailto:press@ingunswetrustfilm.com">press@ingunswetrustfilm.com</a>. My own credits are on {mine}.</p>
    </div>
  </div>
</div></section>'''


def faq_section(ctx):
    items = faq_items(ctx)
    det = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in items)
    return f'''<section class="sec" id="questions" aria-labelledby="faq-h"><div class="wrap">
  {C.mark("05", "Questions")}
  <div class="fp-links">
    <h2 class="display fp-h2 reveal" id="faq-h">Questions people ask</h2>
    <div class="faq reveal">{det}</div>
  </div>
</div></section>'''


def close_section(ctx):
    f = ctx.site["film"]
    return f'''<section class="sec fp-close" aria-label="Watch it"><div class="wrap">
  <p class="display fp-close-h reveal">Watch it. Share it. Talk about it.</p>
  <div class="reveal">{watch_block(ctx, site_link=False)}<p class="small fp-note">{esc(f["timeNote"])}</p></div>
</div></section>'''


def build(ctx):
    s = ctx.site
    f = s["film"]
    path = f["sitePath"]
    trail = [("In Guns We Trust", None)]
    content = "\n".join([head(ctx), film_section(ctx), part_section(ctx), stills_section(ctx),
                         links_section(ctx), faq_section(ctx), close_section(ctx)])
    title = "In Guns We Trust (2026): Tommy Jackett on the documentary"
    desc = ("My side of In Guns We Trust, the 76 minute documentary directed by Josh Janssen. "
            "Free on YouTube Thu 22 Oct 8pm ET, Fri 23 Oct 11am AEDT.")
    graph = [
        jsonld.person(ctx),
        jsonld.web_page(ctx, path, title, desc, about_id=ctx.abs(path) + "#film"),
        jsonld.movie(ctx),
        jsonld.faq(ctx, faq_items(ctx)),
        jsonld.breadcrumb(ctx, trail),
    ]
    ctx.add_page(path, title, desc, content, og_image=s["images"]["ogFilm"],
                 og_alt="In Guns We Trust key art with Tommy Jackett and Josh Janssen on a map of the United States",
                 og_type="video.movie", jsonld=graph, preload=["igwt-key-art"], body_class="film-page",
                 lastmod="2026-10-20")
