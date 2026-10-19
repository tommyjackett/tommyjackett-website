# Adding a note

A note is one entry in `data/notes.json`. Add it, run the build, check it, ship it.

1. Open `data/notes.json` and copy the last entry. Change every field.
   - `slug` becomes the URL: `"my-first-note"` is `/notes/my-first-note/`. Lowercase, hyphens, never change it after publishing.
   - `date` is `YYYY-MM-DD`. `updated` stays `null` until you really edit it. Newest note goes first on the Notes page and in the feed automatically.
   - `title` and `summary` show in lists and the RSS feed. `summary` is the first sentence or two.
   - `metaTitle` (under 60 characters) and `metaDescription` (under 155) must be unique on the site.
   - `image` is an id from `data/images.json` (or `null`). `imageAlt` describes the share card. `socialImage` is an optional 1200 by 630 jpg in `src/img/`.
   - `buttons` are optional: `{"label": "Watch on YouTube", "url": "film:watch", "primary": true}`. `url` takes `film:watch`, `link:<id>`, a path like `/work/`, or a full URL.
   - `needsTommy` is never shown. Use it for questions to check before go-live.
2. Write the body as a list of strings, one per paragraph. Inside a string: `[label](/work/)` for a link, `**bold**`. Extra shapes, by starting the string with:
   - `## A heading` for a heading
   - `> A quote` for a pull quote
   - `- an item` for a bullet list (consecutive lines make one list)
   - `image:salt-flats-tommy-chair | Caption here` for a photo (film images get their credit added)
   - `video:e5zuDN_oNRE | Exact YouTube title` for a YouTube embed (the feed gets a plain link)
3. Build: `python3 scripts/build.py`. Errors stop the build (duplicate title, em dash, dead link). Warnings are worth reading.
4. Look at it: build with `--base-path "" --out /some/folder`, then `python3 -m http.server 8801 --directory /some/folder`, and open `/notes/<slug>/`.
5. Ship: stage explicit paths (`public/`, `data/notes.json`), commit, `scripts/push-live.sh`.

The page, the Notes index, the RSS feed (`/feed.xml`), `sitemap.xml`, `llms.txt`, Article JSON-LD and the breadcrumbs all update from that one entry.

Film launch wording: add an `afterLaunch` block (see the launch note) and the build swaps the text over on its own once the film is live.
