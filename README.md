# tommyjackett-website

Personal site for Tommy Jackett. A small dependency-free Python script turns `data/*.json` and `src/` into a finished static site in `public/`. GitHub Pages publishes `public/` only.

Staging: https://tommyjackett.github.io/tommyjackett-website/ (noindex, robots blocked). Domain: tommyjackett.com (DNS not switched; do not touch until Tommy says go).
Project state, brief and copy deck live in the Brain: `Brain/Tommy/Tommy Jackett Website/` (BUILD-BRIEF.md, copy-deck.md, seo-geo-spec.md).

## How to add a story or a note

1. Open `data/stories.json` (a story) or `data/notes.json` (a note) and copy the last entry. Change every field. Slugs are the URL: `slug: "obike"` becomes `/stories/obike/`.
2. Run `python3 scripts/build.py`. Read the output: errors stop the build, warnings are things to look at.
3. Look at it: `python3 -m http.server 8801 --directory <folder that contains a tommyjackett-website symlink to public>` or build with `--base-path ""` and serve `public/` directly.
4. Ship: stage explicit paths (`public/`, `data/`, whatever you changed, never `git add -A`), commit, then `scripts/push-live.sh`.

New photo: put webp variants in `src/img/` named `<id>-<width>.webp` (640, 1280, 1920) and add an entry to `data/images.json`.
New page type: add a module in `scripts/pages/` (see below). New styles: `src/css/pages/<name>.css` (bundled after `site.css`, one file out). New behaviour: `src/js/pages/<name>.js` (bundled after `site.js`).

Full steps for a note, including headings, quotes, photos and video embeds, are in `NOTES-HOWTO.md`.

## Build commands

```
python3 scripts/build.py                 staging: BASE_PATH /tommyjackett-website, noindex on every page, robots Disallow all
python3 scripts/build.py --root          go-live: root domain, indexing on, robots Allow + Sitemap, sitemap.xml, llms.txt, CNAME tommyjackett.com
python3 scripts/build.py --machine       staging that also writes sitemap.xml and llms.txt (to test them)
python3 scripts/build.py --state after   force the after-launch wording (default: decided by the clock, launch is 22 Oct 2026 8pm ET)
python3 scripts/build.py --base-path "" --out /tmp/x     any target; --out accepts an absolute path
python3 scripts/check_links.py           checks every external link in public/ (run after a build, needs the network)
```

The build refuses (exit 1) when: a title or description is duplicated, a page has no h1 or more than one, an image has no alt, an internal link or image is dead, an em dash appears anywhere in output or source, the word "Cracks" appears, a staging page lacks noindex, a root page has noindex, or a root build still contains a `[[gap]]`. Pages not built yet (nav targets, stories, notes) show as warnings only.

Go-live in one command: `python3 scripts/build.py --root`, commit `public/`, push. Then set the custom domain in repo Settings, Pages. Full DNS steps are in the Brain's `seo-geo-spec.md` section 8 and `MORNING-REPORT.md`.

## Layout of the repo

```
data/            site.json stories.json notes.json links.json images.json videos.json form.json
src/layout.html  the page shell ({{head}} {{header}} {{content}} {{closer}} {{footer}})
src/css/site.css all shared styles (tokens at the top). src/css/pages/*.css are appended.
src/js/site.js   menu, reveal, header, form enhancement. src/js/pages/*.js are appended.
src/fonts src/img src/icons    copied as is
scripts/build.py               the build
scripts/lib/core.py            Ctx: data, URLs, images, text helpers
scripts/lib/components.py      header, footer, buttons, video embed, contact form, page render
scripts/lib/jsonld.py          Person, WebSite, Organization, Movie, VideoObject, Article, FAQPage, BreadcrumbList, CollectionPage, ProfilePage, ContactPage
scripts/lib/machine.py         robots, sitemap, llms.txt, feed
scripts/pages/*.py             one module per page group; each defines build(ctx)
public/          the output. Committed. This is what GitHub Pages serves.
```

## Writing a page module (for builders of film, stories, work, notes, about, contact)

Create `scripts/pages/<name>.py` with `def build(ctx):` and call `ctx.add_page(path, title, description, content_html, **options)`. Modules run in alphabetical order. `home.py` is the reference. Imports at the top of a page module: `from lib import components as C, jsonld` and `from lib.core import esc, fmt_date`.

`ctx.add_page` options: `og_image` (an image id, or a filename in `src/img` ending .jpg/.png), `og_alt`, `og_type` (`website`, `article`, `video.movie`), `jsonld` (list of dicts, rendered as one `@graph`), `body_class`, `lastmod` (YYYY-MM-DD, goes in sitemap), `preload` (image ids), `article` (`{"published": iso, "modified": iso}` for article:* meta), `no_closer` (skip the "Watch the film / Get in touch" strip), `noindex`.
Paths are folder URLs: `"/stories/obike/"` writes `public/stories/obike/index.html`.

Helpers on `ctx`: `ctx.url("/x/")` (adds BASE_PATH, use for every internal link), `ctx.abs("/x/")` (absolute canonical URL), `ctx.img(id, sizes=..., cls=..., priority=False, alt=None, focal=True)` (srcset img with width, height, alt, focal point), `ctx.img_abs(id, 1280)`, `ctx.credit(id)`, `ctx.md(text)` (inline: `[label](target)`, `**bold**`, `[[gap]]`; also curly quotes), `ctx.plain(text)`, `ctx.a(link_id)` (anchor for a verified link, empty string if the link is held), `ctx.link(id)`, `ctx.links_in(group)`, `ctx.film_when("short"|"full")` (launch wording, flips on the launch date), `ctx.watch_url`, `ctx.is_live`, `ctx.note(n)` (a note with the after-launch swap applied), `ctx.story(slug)`, `ctx.story_href(story)`, `ctx.stories`, `ctx.notes` (newest first), `ctx.videos`, `ctx.production`.
Link targets accepted wherever a target is allowed (`ctx.resolve`): a path (`/work/`), a full URL, `film:watch` (the watch URL), `link:<id>` (a url from links.json).
Components in `lib/components.py`: `btn(ctx, label, target, kind="primary"|"ghost")`, `link_go(ctx, label, target)`, `mark("01", "Label")` (the section marker), `breadcrumbs_html(ctx, trail)` plus `jsonld.breadcrumb(ctx, trail)` (trail is `[("Stories", "/stories/"), ("Title", None)]`), `video_embed(ctx, video)` (YouTube nocookie, standard no-branding parameters, lazy), `contact_form(ctx)` (the Web3Forms form, or the email-only state while `formAccessKey` is empty), `film_notice(ctx)`.
CSS classes ready to use: `.wrap`, `.sec`, `.band`, `.display` (Anton uppercase; `h1.display`, `h2.display`), `.lead`, `.small`, `.measure`, `.mark`, `.btn`, `.btn--ghost`, `.btn-row`, `.link`, `.link-go`, `.reveal` (add `style="--d:.1s"` to stagger), `.page-head`, `.page-lede`, `.crumbs`, `.byline`, `.prose`, `.video` (16:9 box), `.figure` (figure plus figcaption), `.linklist`, `.rows`, `.faq` (details and summary), `.form`, `.field`. Body text is Inter. Use Anton only for the name and big headlines. Page content starts below the fixed header: give the first section `class="page-head wrap"` or add top padding of `calc(var(--header-h) + var(--s-5))`.
Rules every page follows: one h1, no heading plus subheading stacks, no pills or icon cards, no gradients, no filter or overlay or text on film images, credit under every film image (`ctx.credit(id)`), content note beside every watch button on the film page, both time zones wherever the date is given.

## Data schemas

All files are plain JSON, UTF-8, no comments. No em dashes anywhere.

### data/site.json (one object)

| Key | Meaning |
|---|---|
| `name` `locale` `ogLocale` `location` `jobTitle` `email` | Name, `en-AU`, `en_AU`, `Melbourne`, job title line, public email (`tommy@tommyjackett.com`, Tommy to confirm). |
| `formAccessKey` | Tommy's own Web3Forms key. Empty means the contact form is replaced by the email-only message. |
| `urls.production` / `urls.staging` / `urls.stagingBasePath` | Site URL for each mode and the staging sub-path. Everything absolute (canonical, og:url, sitemap, JSON-LD `@id`) is built from these. |
| `entityStatement` `entityStatementShort` | The two strings used word for word everywhere (JSON-LD, FAQ, llms.txt). Never retype them in a page: read them from here. |
| `images.person` `images.ogHome` `images.ogFilm` | Image ids for the Person markup portrait and the default share images. |
| `film.*` | `title year runtimeMinutes runtimeISO director{name,url} productionCompanies[] launchISO launchDisplayAEDT watchUrl watchUrlIsChannel sitePath filmSite oneLiner contentNote support supportInline timeNote creditLine`, and `whenShort` / `whenFull` each with `before` and `after` strings. `launchISO` is the instant the wording flips. Update `watchUrl` to the watch URL once the film is uploaded. |
| `nav[]` | Top bar: `{label, path}`. |
| `footer` | `line1 line2 map[{label,path}] socialIds[] copyright`. `socialIds` are ids from links.json; unverified ones are skipped automatically. |
| `vidpod` | `{name, url, storyUrl, sameAs[]}` for the Organization markup. |
| `knowsAbout[]` | For Person markup. |
| `home` `notFound` | Title and description for the home page and the 404 title. |

### data/stories.json (array, newest first by `order`)

| Key | Meaning |
|---|---|
| `slug` | URL part: `/stories/<slug>/`. |
| `href` | Optional override for a story that lives elsewhere (the film entry uses `/in-guns-we-trust/`). |
| `isFilm` | True for the film entry. Skip it when you build story pages. |
| `title` | H1 on the story page. `listTitle` is the short name used in lists. |
| `year` | String, shown in lists. |
| `order` | Position on the stories index (1 first). `homeOrder` is the position on the home page, null if it is not there. |
| `image` | Image id for the list or page, or null. |
| `indexLine` `homeLine` | One-liners for the stories index and the home page (data-string markup allowed). `readLabel` is the link label. |
| `metaTitle` `metaDescription` | Unique title and description. |
| `published` `updated` | YYYY-MM-DD, for Article markup and the visible dates. |
| `body[]` | Paragraphs as data strings. `[[NEEDS TOMMY: ...]]` marks a gap: highlighted on staging, fails a root build. |
| `videos[]` | `{id, title, label, duration (ISO 8601 or null), uploadDate, thumb (image id or null), short (bool), description}`. `title` is the exact YouTube title. If `thumb` is null the markup falls back to YouTube's own thumbnail URL. |
| `press[]` | `{outlet, url, date, about}`, verified only. `pressLine` is the plain-text sentence to print. |
| `watch[]` | `{label, url}` links under the video. |
| `needsTommy[]` | Questions for Tommy, never rendered. |
| `status` | `live` or `hold` (hold: do not build a page). |

### data/notes.json (array, any order, the build sorts newest first)

| Key | Meaning |
|---|---|
| `slug` | `/notes/<slug>/`. |
| `title` `summary` | Title and the first sentence shown in lists and the feed. |
| `date` `updated` | YYYY-MM-DD. `updated` is null until a real edit. The build works out the +10:00 or +11:00 Melbourne offset. |
| `image` `socialImage` `imageAlt` | Image id, optional social jpg filename in `src/img`, alt for the share card. |
| `metaTitle` `metaDescription` | Unique. |
| `body[]` | Paragraphs, data-string markup allowed. |
| `buttons[]` | `{label, url, primary}`; `url` accepts `film:watch`, `link:<id>`, a path or a URL. |
| `afterLaunch` | Optional. `{title, metaTitle, summary, bodyReplace[[from, to], ...]}` applied by `ctx.note(n)` once the film is live. |
| `needsTommy[]` | Never rendered. |

### data/links.json (array)

`{id, label, url, group, verified, sameAs, note}`. `group` is one of `tommy`, `film`, `people`, `vidpod`, `dts`, `press`, `social`. Only `verified: true` links ever reach a page (`ctx.link`, `ctx.a`, `ctx.links_in`). `sameAs: true` puts the URL in the Person markup. Held back for now: `tj-linkedin`, `film-facebook`, `film-x` (unverified).

### data/images.json (array)

`{id, file, widths[], width, height, alt, caption, captionTitle?, place?, credit, kind, filmAsset, focal, mood, bestFor[], social?, sourcePath}`. Files are `src/img/<file>-<width>.webp`; `width` and `height` are the largest variant. `focal` is a CSS object-position used when an image is cropped. `kind` is `keyArt`, `poster`, `titleTreatment`, `filmStill`, `saltFlats`, `portrait`, `press` or `videoThumb`. `filmAsset: true` means no filter, overlay, text or recolour, ever, and the credit must be shown. `social` names a 1200 by 630 jpg used for share cards. The `videoThumb` entries are the maxres YouTube thumbnails of Tommy's own videos, fetched 19 Oct 2026, used for story pages and the older-videos strip.

### data/videos.json (array)

The older videos strip on the home page: `{id (YouTube id), title (exact YouTube title), line (his one-liner), year, thumb (image id)}`.

### data/form.json

Notes on the contact form service (Web3Forms), fields and honeypots. `components.contact_form(ctx)` implements it.

## Fonts

Anton (name and big headlines) and Inter (everything else), self-hosted woff2 in `src/fonts/`, SIL OFL. No third-party requests at runtime. Anton is narrow: "JACKETT" is 3.10 em wide and "TOMMY" 2.82 em, which is how the hero sizes the name to the screen.
