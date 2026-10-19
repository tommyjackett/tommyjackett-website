"""Helpers shared by the work, about, contact and notes pages (not a page itself: the build skips files starting with _)."""
import json
import os

from lib import components as C
from lib.core import ROOT, esc


def load(name):
    with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def label(n, text, extra=""):
    """A section label that is a real h2, set small like the home page markers."""
    return (f'<h2 class="mark reveal"><span class="mark-n">{esc(n)}</span><span class="mark-t">{esc(text)}</span></h2>')


OPTIONS = ["Video or podcast production", "Hosting a screening of In Guns We Trust", "Press or interview", "Speaking or a collab", "Just saying hi"]


def sent_banner(text):
    """Shown when the page is opened at #sent (the form redirects back with ?sent=1#sent) or by contact.js."""
    return f'<p class="ct-sent" id="sent" role="status" tabindex="-1">{esc(text)}</p>'


def form(ctx, redirect_path):
    """The Web3Forms form when site.formAccessKey is set, otherwise a form that opens the visitor's email app.

    Both look the same. The second sends nothing anywhere: it builds a mailto link from the fields (contact.js)."""
    s = ctx.site
    email = s["email"]
    if s.get("formAccessKey"):
        html = C.contact_form(ctx, redirect_path)
        return html.replace("?sent=1\"", "?sent=1#sent\"")
    mailto = f'<a href="mailto:{esc(email)}">{esc(email)}</a>'
    options = "".join(f"<option>{esc(o)}</option>" for o in OPTIONS)
    return f'''<form class="form" method="get" action="mailto:{esc(email)}" data-compose>
  <input type="hidden" name="subject" value="New enquiry from tommyjackett.com">
  <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required data-label="name"></div>
  <div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" autocomplete="email" required data-label="email"></div>
  <div class="field"><label for="f-co">Company or project <span class="opt">(optional)</span></label><input id="f-co" name="company" type="text" autocomplete="organization"></div>
  <div class="field"><label for="f-type">What is it about?</label><select id="f-type" name="project_type">{options}</select></div>
  <div class="field"><label for="f-msg">What are you working on?</label><textarea id="f-msg" name="body" required data-label="message"></textarea><p class="hint">A few lines is plenty.</p></div>
  <div><button class="btn" type="submit">Send it</button>
    <p class="small ct-fine">This opens your email app with your message ready to send. I only use your details to reply to you.</p></div>
  <p class="form-msg" role="status" aria-live="polite" hidden></p>
  <p class="small" data-compose-fallback hidden>If nothing opened, email me directly: {mailto}</p>
</form>'''
