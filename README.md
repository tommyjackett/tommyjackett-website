# tommyjackett-website

Personal site for Tommy Jackett: an original-content creator's home. One dependency-free Python script (`scripts/build.py`) turns `data/*.json` and `src/` into a finished static site in `public/`. GitHub Pages publishes `public/` only.

Staging: https://tommyjackett.github.io/tommyjackett-website/ (noindex, robots blocked). Domain: tommyjackett.com (DNS not switched; do not touch until Tommy says go).
Brief and research live in the Brain: `Brain/Tommy/Tommy Jackett Website/` (BUILD-BRIEF.md has the rules, REVISION 4 first).

## Pages

`/` home, `/in-guns-we-trust/` (nav: Doco), `/stories/` and one page per story, `/about/`, `/work/`, `/contact/`, `/404.html`. No Notes, no feed. Nav order: Doco, Stories, About, Work, Contact.

## Where the words and facts live

| File | What is in it |
|---|---|
| `data/pages.json` | Copy for home, doco, about (bio and timeline), work, contact, 404 |
| `data/stories.json` | Every story: title, lede, status, videos, dated thread, next story |
| `data/site.json` | Entity statement (word for word), film facts and launch time, nav, footer links |
| `data/links.json` | Every external link with a `verified` flag. Unverified links are never printed |
| `data/images.json` | Photo ids, alt text, focal points, credits. Files are `src/img/<file>-<width>.webp` |
| `data/form.json` | Web3Forms access key and the form's messages |

## Add or change a story

1. Open `data/stories.json`, copy a story, change every field. The slug is the URL.
2. `videos` is the list of YouTube videos (id, title, date, thumb image id). The first one is the main player at the top; the others play inside the thread.
3. `thread` is the dated list of updates. An entry with `"date": null` and `"label": "Next"` is the "what happens next" line.
4. `heroPhoto` (optional, an image id of Tommy's own photo) makes the page lead with that photograph, tucked under the name, with the first video below it. Without it the first video is the hero. `titleSize` (optional) sets the title size. `homeTile` (optional) is the photo used on the home page and the stories index. `strip` (DJ Bodhi only) is the three thumbnails in the home strip. `tileStatus` (optional) is the small label under a home tile.
5. Add the story's `next` slug so the next-story link works. Run `python3 scripts/build.py`.

## Making In Guns We Trust (behind the scenes) and how to add more

The story lives in `data/stories.json` (slug `making-in-guns-we-trust`, status "Ongoing"). To add photos:

1. Pick the photo, convert it (HEIC: `sips -s format jpeg in.HEIC --out x.jpg`), resize to 960 and 480 px on the long edge and save as `src/img/<name>-960.webp` and `src/img/<name>-480.webp` (keep each under about 250 KB; `cwebp -q 70`).
2. Add an entry to `data/images.json`: `id`, `file` (same as the name), `widths` `[480, 960]`, `width`, `height`, `alt` (what the photo shows), `caption` (plain, only what it shows), `credit`.
3. In the story's `thread`, add an entry with `date`, a short plain `text`, and `photos`: a list of image ids. Run `python3 scripts/build.py`.

Two unused trip photos are already in `data/images.json` if wanted (none left over now; add new ones the same way). The doco page links to the story and shows three of the photos.

## Doco wording before and after release

`data/site.json` film.whenShort, whenFull and lead each have a `before` and an `after`. The site switches itself at `2026-10-23T00:00:00Z`. `python3 scripts/build.py --state after` bakes the after text in. The Watch button URL is the single field `film.watchUrl` (currently the film's YouTube channel; paste the watch URL there on release day).

## Build commands

```
python3 scripts/build.py                  staging: sub-path, noindex on every page, robots Disallow all
python3 scripts/build.py --machine        staging that also writes sitemap.xml and llms.txt
python3 scripts/build.py --root           go-live: root domain, indexing on, sitemap.xml, llms.txt, CNAME tommyjackett.com
python3 scripts/build.py --state after    bake in the after-launch wording
python3 scripts/build.py --base-path "" --site-url http://localhost:8841 --out /tmp/x     any target
python3 scripts/check_links.py            checks every external link in public/ (needs the network)
```

The build stops with an error if: a title or description is duplicated, a page does not have exactly one h1, an image has no alt, an internal link or image is dead, an em dash appears anywhere in output or source, a mailto link appears outside the film's own addresses on the film page, a phone number, a Tommy X link, "Notes" or "Cracks" appears, a staging page lacks noindex, or a root page has noindex.

## Contact form (Web3Forms) and go-live

`data/form.json` holds `PASTE_WEB3FORMS_KEY_HERE`. Until a real key is in `accessKey`:

- the form shows on staging, and a send answers with a friendly "my contact form isn't switched on yet" (never a fake success);
- `python3 scripts/build.py --root` refuses to run.

To switch it on: make a NEW Web3Forms form for tommyjackett.com (not VIDPOD's), paste its access key into `data/form.json`, rebuild. Then `python3 scripts/build.py --root`, commit `public/`, push, and set the custom domain in the repo's Pages settings.

## Launch wording (before and after 22 Oct 2026, 8pm ET)

The HTML always carries the before text ("Free on YouTube. Friday 23 October, 11am AEDT (Thursday 22 October, 8pm ET)."), with both texts in `data-before` and `data-after` attributes. A few lines in `src/js/site.js` swap in the after text at the launch moment (`launchISO` in `data/site.json`), so the site flips by itself with no rebuild or redeploy. `--state after` bakes the after text into the HTML if you would rather ship that on release day.

The Ranch Part 1 title on YouTube is under test (the channel list and the watch page differed on 19 Oct). Re-check it with oEmbed on go-live day and update `data/stories.json`.

## Rules baked in

- Entity statement is word for word from `data/site.json` everywhere (JSON-LD included).
- No email address, no phone number, no Tommy X link anywhere. The film's own press and screenings addresses appear on the film page only.
- Film stills and key art are never filtered, overlaid or lettered over. The key art swaps to the portrait poster on phones, untouched.
- Big type overlaps Tommy's own photos and his own published thumbnails, never the film's images.
- Never an em dash.

## Layout of the repo

```
data/             the JSON files above
src/css/site.css  all styles
src/js/site.js    menu, header, soft fades, launch wording switch, click-to-play videos, form
src/fonts         Anton, Inter, Instrument Serif (self-hosted woff2, OFL)
src/img           webp photos (<file>-<width>.webp) plus 1200x630 social jpgs
scripts/build.py  the build
public/           the output; committed; this is what Pages serves
```

Ship: stage explicit paths (never `git add -A`), commit, then `scripts/push-live.sh`.
