"""JSON-LD helpers. Each returns a plain dict for use inside an @graph. Pages pass a list to ctx.add_page(jsonld=[...]).

All URLs and @id values are generated from ctx.site_url, so staging and production never disagree.
"""
import json


def pid(ctx):
    return {"@id": ctx.id_url("person")}


def person(ctx):
    s = ctx.site
    d = {
        "@type": "Person",
        "@id": ctx.id_url("person"),
        "name": s["name"],
        "url": ctx.abs("/"),
        "image": ctx.img_abs(s["images"]["person"], 1920),
        "description": s["entityStatement"],
        "jobTitle": s["jobTitle"],
        "nationality": {"@type": "Country", "name": "Australia"},
        "homeLocation": {"@type": "Place", "name": f"{s['location']}, Australia"},
        "worksFor": {"@id": ctx.id_url("vidpod")},
        "knowsAbout": s["knowsAbout"],
        "subjectOf": {"@id": ctx.abs(s["film"]["sitePath"]) + "#film"},
        "sameAs": ctx.same_as(),
    }
    return d


def vidpod(ctx):
    v = ctx.site["vidpod"]
    return {"@type": "Organization", "@id": ctx.id_url("vidpod"), "name": v["name"], "url": v["url"], "sameAs": v["sameAs"]}


def website(ctx):
    s = ctx.site
    return {
        "@type": "WebSite", "@id": ctx.id_url("website"), "url": ctx.abs("/"), "name": s["name"],
        "alternateName": ["Tommy Jackett Video", "tommyjackett.com"], "inLanguage": s["locale"], "publisher": pid(ctx),
    }


def movie(ctx):
    f = ctx.site["film"]
    jj = {"@type": "Person", "name": f["director"]["name"], "url": f["director"]["url"]}
    return {
        "@type": "Movie",
        "@id": ctx.abs(f["sitePath"]) + "#film",
        "name": f["title"],
        "alternateName": f"{f['title']} ({f['year']})",
        "url": ctx.abs(f["sitePath"]),
        "description": f["oneLiner"],
        "image": ctx.img_abs(ctx.site["images"]["ogFilm"], 1920),
        "genre": "Documentary",
        "inLanguage": "en",
        "duration": f["runtimeISO"],
        "datePublished": f["launchISO"],
        "dateCreated": str(f["year"]),
        "director": jj,
        "actor": [pid(ctx), jj],
        "creator": [pid(ctx)],
        "productionCompany": [{"@type": "Organization", "name": n} for n in f["productionCompanies"]],
        "sameAs": [ctx.links_all[i]["url"] for i in ("film-site", "film-imdb", "film-youtube")],
        "potentialAction": {
            "@type": "WatchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": ctx.watch_url,
                       "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]},
            "expectsAcceptanceOf": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                                    "availabilityStarts": f["launchISO"],
                                    "eligibleRegion": {"@type": "Place", "name": "Worldwide"}},
        },
    }


def video_object(ctx, v, page_path, slug=None):
    """v is an entry from a story's `videos` list. Thumbnail falls back to YouTube's own if no local thumb."""
    thumb = ctx.img_abs(v["thumb"], 1280) if v.get("thumb") else f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"
    d = {
        "@type": "VideoObject",
        "@id": ctx.abs(page_path) + "#video-" + (slug or v["id"]),
        "name": v["title"],
        "description": v["description"],
        "thumbnailUrl": [thumb],
        "uploadDate": v["uploadDate"],
        "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}",
        "contentUrl": f"https://www.youtube.com/watch?v={v['id']}",
        "publisher": pid(ctx),
        "inLanguage": "en",
    }
    if v.get("duration"):
        d["duration"] = v["duration"]
    return d


def article(ctx, page_path, headline, description, image_abs, published_iso, modified_iso):
    u = ctx.abs(page_path)
    return {
        "@type": "Article", "@id": u + "#article", "headline": headline[:110], "description": description,
        "image": [image_abs], "datePublished": published_iso, "dateModified": modified_iso,
        "author": pid(ctx), "publisher": pid(ctx), "mainEntityOfPage": u, "inLanguage": ctx.site["locale"],
    }


def faq(ctx, qa):
    """qa: list of (question, answer) as plain text."""
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}


def breadcrumb(ctx, trail):
    """trail: [(name, path_or_None), ...] after the root. The root 'Tommy Jackett' is added for you.
    The last item should have path None."""
    items = [("Tommy Jackett", "/")] + list(trail)
    out = []
    for i, (name, path) in enumerate(items, 1):
        it = {"@type": "ListItem", "position": i, "name": name}
        if path:
            it["item"] = ctx.abs(path)
        out.append(it)
    return {"@type": "BreadcrumbList", "itemListElement": out}


def collection_page(ctx, name, path, description, part_paths):
    return {"@type": "CollectionPage", "name": name, "url": ctx.abs(path), "description": description,
            "isPartOf": {"@id": ctx.id_url("website")},
            "hasPart": [{"@type": "WebPage", "url": ctx.abs(p)} for p in part_paths]}


def profile_page(ctx, path, created, modified):
    return {"@type": "ProfilePage", "url": ctx.abs(path), "dateCreated": created, "dateModified": modified,
            "mainEntity": pid(ctx)}


def contact_page(ctx, path, name):
    return {"@type": "ContactPage", "name": name, "url": ctx.abs(path), "mainEntity": pid(ctx)}


def web_page(ctx, path, name, description, about_id=None):
    d = {"@type": "WebPage", "@id": ctx.abs(path) + "#webpage", "url": ctx.abs(path), "name": name,
         "description": description, "isPartOf": {"@id": ctx.id_url("website")}, "inLanguage": ctx.site["locale"]}
    if about_id:
        d["about"] = {"@id": about_id}
    return d


def script(graph):
    """Render a list of dicts as one <script type=application/ld+json> with an @graph."""
    payload = {"@context": "https://schema.org", "@graph": graph}
    txt = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{txt}</script>'
