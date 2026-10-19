"""Home page: the journey. Copy comes from copy-deck.md section 1; data from data/*.json."""
from lib import components as C
from lib import jsonld
from lib.core import esc, fmt_date


def hero(ctx):
    s = ctx.site
    img = ctx.img("salt-flats-tommy-wide", sizes="(min-width: 1100px) 46vw, 100vw", priority=True)
    return f'''<section class="hero" data-hero aria-label="Introduction">
  <div class="hero-media">{img}</div>
  <h1 class="name"><span class="l"><span class="w" style="--i:0">Tommy</span></span> <span class="l"><span class="w" style="--i:1">Jackett</span></span></h1>
  <div class="hero-copy">
    <p class="hero-lead">Hey, I'm Tommy. I make video and tell stories from Melbourne.</p>
    <p class="hero-act"><a class="btn" href="{esc(ctx.watch_url)}">Watch In Guns We Trust</a></p>
    <p class="hero-when">{esc(ctx.film_when("short"))}</p>
  </div>
</section>'''


def film_section(ctx):
    f = ctx.site["film"]
    poster = ctx.img("igwt-poster", sizes="100vw", focal=False)
    key = ctx.img("igwt-key-art", sizes="(min-width: 1400px) 780px, 58vw", focal=False)
    return f'''<section class="sec" id="film" aria-labelledby="film-h"><div class="wrap">
  {C.mark("01", "On now")}
  <div class="film-grid">
    <figure class="film-art film-art--m reveal">{poster}<figcaption class="small">{esc(ctx.credit("igwt-poster"))}</figcaption></figure>
    <figure class="film-art film-art--d reveal">{key}<figcaption class="small">{esc(ctx.credit("igwt-key-art"))}</figcaption></figure>
    <div class="film-text">
      <h2 class="display reveal" id="film-h">In Guns We Trust</h2>
      <p class="film-p reveal">{ctx.md("In Guns We Trust is a documentary Josh Janssen directed, and I'm in it with him. We're two unarmed Australian mates who didn't have a position on guns, so we crossed America with cameras and listened to the people who do. A Hollywood armourer, a Route 91 survivor, a Texas sheriff, a trauma surgeon. Everyone speaks for themselves. No side, no agenda, just conversations.")}</p>
      <p class="reveal">76 minutes. Free, worldwide, on YouTube.</p>
      <p class="when reveal">{esc(ctx.film_when("short"))}</p>
      <div class="btn-row reveal">{C.btn(ctx, "Watch on YouTube", "film:watch")}{C.btn(ctx, "More about the film", f["sitePath"], "ghost")}</div>
      <p class="small note reveal">{esc(f["contentNote"])} {esc(f["supportInline"])}</p>
    </div>
  </div>
</div></section>'''


def stories_section(ctx):
    rows = []
    items = sorted([x for x in ctx.stories if x.get("homeOrder")], key=lambda x: x["homeOrder"])
    for st in items:
        href = esc(ctx.url(ctx.story_href(st)))
        rows.append(f'''<li class="story reveal"><span class="story-y">{esc(st["year"])}</span>
  <h3 class="story-t">{esc(st["listTitle"])}</h3>
  <p class="story-l">{ctx.md(st["homeLine"])}</p>
  <a class="story-go" href="{href}">{esc(st["readLabel"])}<span class="vh">: {esc(st["listTitle"])}</span></a></li>''')
    return f'''<section class="sec" id="stories" aria-labelledby="stories-h"><div class="wrap">
  {C.mark("02", "Stories")}
  <div class="split">
    <div class="split-side sticky">
      <h2 class="display reveal" id="stories-h">Stories</h2>
      <p class="lead reveal" style="--d:.1s">Most of what I make starts the same way. Something catches my eye, I can't leave it alone, and I go and see for myself.</p>
    </div>
    <div class="split-main">
      <ul class="story-list">{"".join(rows)}</ul>
      <p class="all-link reveal">{C.link_go(ctx, "All stories", "/stories/")}</p>
    </div>
  </div>
</div></section>'''


def work_section(ctx):
    img = ctx.img("tommy-camera-harbour", sizes="(min-width: 900px) 38vw, 100vw", style="")
    return f'''<section class="sec band" id="work" aria-labelledby="work-h"><div class="wrap">
  {C.mark("03", "Work")}
  <div class="work-grid">
    <div class="work-text">
      <h2 class="display reveal" id="work-h">Work with me</h2>
      <p class="lead reveal" style="--d:.1s">I make video and podcasts through <a href="{esc(ctx.site["vidpod"]["url"])}">VIDPOD</a>, a production company in Melbourne. If you've got a project coming up, get in touch.</p>
      <div class="btn-row reveal" style="--d:.2s">{C.btn(ctx, "How I work", "/work/")}{C.btn(ctx, "Go to VIDPOD", "link:vidpod", "ghost")}</div>
    </div>
    <div class="work-img reveal">{img}</div>
  </div>
</div></section>'''


def videos_section(ctx):
    items = []
    for v in ctx.videos:
        thumb = ctx.img(v["thumb"], sizes="(min-width: 900px) 24vw, 76vw", alt="") if v.get("thumb") else ""
        items.append(f'''<li class="vid">{thumb}<p class="vid-l"><a href="https://www.youtube.com/watch?v={esc(v["id"])}">{ctx.md(v["line"])}<span class="vh">. Watch on YouTube.</span></a></p><p class="vid-t">{esc(v["title"])}</p></li>''')
    return f'''<section class="sec" id="older" aria-labelledby="older-h">
  <div class="wrap">{C.mark("04", "Older videos")}<h2 class="display reveal" id="older-h">Older videos</h2></div>
  <ul class="strip reveal" tabindex="0" aria-label="Older videos, scroll sideways">{"".join(items)}</ul>
</section>'''


def dts_section(ctx):
    return f'''<section class="sec band" id="dts" aria-labelledby="dts-h"><div class="wrap">
  {C.mark("05", "Daily Talk Show")}
  <div class="dts-grid">
    <h2 class="display reveal" id="dts-h">The Daily Talk Show</h2>
    <div class="dts-body reveal" style="--d:.1s">
      <p>For three and a half years Josh Janssen and I made a podcast and video talk show every day. More than 1,000 episodes, from January 2018 to May 2021. It's finished now, but all of it's still there. Same Josh.</p>
      <p class="all-link">{C.link_go(ctx, "Visit thedailytalkshow.com", "link:dts")}</p>
      <p class="small">Strong language.</p>
    </div>
  </div>
</div></section>'''


def notes_section(ctx):
    n = ctx.note(ctx.notes[0]) if ctx.notes else None
    latest = ""
    if n:
        latest = f'''<div class="note-latest reveal"><p class="small">Latest</p><h3><a href="{esc(ctx.url("/notes/" + n["slug"] + "/"))}">{esc(n["title"])}<span class="vh">. Read the note.</span></a></h3><p class="small">{esc(fmt_date(n["date"]))}</p></div>'''
    return f'''<section class="sec" id="notes" aria-labelledby="notes-h"><div class="wrap">
  {C.mark("06", "Notes")}
  <div class="split">
    <div class="split-side">
      <h2 class="display reveal" id="notes-h">Notes</h2>
    </div>
    <div class="split-main">
      <p class="lead reveal" style="--d:.1s">Things I'm working on, trying out and figuring out. Rough on purpose.</p>
      <div style="margin-top:var(--s-4)">{latest}</div>
      <p class="all-link reveal">{C.link_go(ctx, "All notes", "/notes/")}</p>
    </div>
  </div>
</div></section>'''


def about_section(ctx):
    img = ctx.img("salt-flats-tommy-portrait", sizes="(min-width: 900px) 40vw, 100vw")
    return f'''<section class="sec band" id="about" aria-labelledby="about-h"><div class="wrap">
  {C.mark("07", "About")}
  <div class="about-grid">
    <div class="about-img reveal">{img}</div>
    <div class="about-text">
      <h2 class="display reveal" id="about-h">About</h2>
      <p class="lead reveal" style="--d:.1s">Hey, I'm Tommy. I live in Melbourne, I make video, and I can't resist a rabbit hole. I've been at it for more than a decade, and plenty of it didn't work. I'm fine with that.</p>
      <p class="reveal" style="--d:.15s">{C.link_go(ctx, "More about me", "/about/")}</p>
    </div>
  </div>
</div></section>'''


def contact_section(ctx):
    email = ctx.site["email"]
    return f'''<section class="sec" id="contact" aria-labelledby="contact-h"><div class="wrap">
  {C.mark("08", "Contact")}
  <h2 class="display contact-h reveal" id="contact-h">Get in touch</h2>
  <div class="contact-grid">
    <div class="contact-main reveal"><p class="lead">Got an idea, a question or a project? Tell me about it.</p>
      <p style="margin-top:var(--s-3)">{C.btn(ctx, "Get in touch", "/contact/")}</p></div>
    <div class="contact-side reveal" style="--d:.1s"><p class="small">Prefer email? Write to me directly. <a href="mailto:{esc(email)}">{esc(email)}</a></p></div>
  </div>
</div></section>'''


def find_section(ctx):
    names = ["tj-youtube", "tj-instagram", "tj-tiktok", "tj-facebook", "tj-x", "tj-imdb"]
    links = "".join(ctx.a(i) for i in names)
    film = [
        ctx.a("film-site", "ingunswetrustfilm.com"),
        ctx.a("film-youtube", "the film’s YouTube channel"),
        ctx.a("film-instagram", "Instagram"),
        ctx.a("film-tiktok", "TikTok"),
        ctx.a("film-threads", "Threads"),
    ]
    film = [x for x in film if x]
    film_txt = ", ".join(film[:-1]) + " and " + film[-1]
    return f'''<section class="sec sec--tight band" id="find" aria-labelledby="find-h"><div class="wrap">
  {C.mark("09", "Find me")}
  <h2 class="display reveal" id="find-h">Find me</h2>
  <p class="reveal" style="margin-top:var(--s-3);max-width:46ch">My channel is on YouTube. The short stuff lives on Instagram and TikTok.</p>
  <div class="find-list reveal">{links}</div>
  <p class="small reveal">The film has its own pages: {film_txt}.</p>
</div></section>'''


def build(ctx):
    s = ctx.site
    content = "\n".join([
        hero(ctx), film_section(ctx), stories_section(ctx), work_section(ctx), videos_section(ctx),
        dts_section(ctx), notes_section(ctx), about_section(ctx), contact_section(ctx), find_section(ctx),
    ])
    graph = [jsonld.website(ctx), jsonld.person(ctx), jsonld.vidpod(ctx)]
    ctx.add_page("/", s["home"]["title"], s["home"]["description"], content,
                 og_image=s["images"]["ogHome"], og_alt="Tommy Jackett smiling in a black bomber jacket",
                 jsonld=graph, preload=["salt-flats-tommy-wide"], preload_sizes="(min-width: 1100px) 46vw, 100vw",
                 lastmod=ctx.notes[0]["date"] if ctx.notes else None)
