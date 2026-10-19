/* tommyjackett.com. Nav toggle, scroll reveal, solid header after the hero, optional form enhancement. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, body = doc.body;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Menu */
  var btn = doc.querySelector(".menu-btn"), menu = doc.getElementById("menu");
  if (btn && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      body.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
      menu.setAttribute("aria-hidden", open ? "false" : "true");
    };
    menu.setAttribute("aria-hidden", "true");
    btn.addEventListener("click", function () { setMenu(!menu.classList.contains("open")); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu.classList.contains("open")) { setMenu(false); btn.focus(); } });
    window.matchMedia("(min-width: 900px)").addEventListener("change", function (e) { if (e.matches) setMenu(false); });
  }

  /* Header turns solid once the hero has gone (home) or straight away (inner pages). */
  var header = doc.querySelector(".site-header"), hero = doc.querySelector("[data-hero]");
  if (header) {
    if (hero && "IntersectionObserver" in window) {
      var hio = new IntersectionObserver(function (en) {
        header.classList.toggle("is-solid", !en[0].isIntersecting);
      }, { rootMargin: "-70px 0px 0px 0px", threshold: 0 });
      hio.observe(hero);
    } else {
      header.classList.add("is-solid");
    }
  }

  /* Reveal */
  var items = [].slice.call(doc.querySelectorAll(".reveal"));
  if (items.length) {
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      items.forEach(function (el) { io.observe(el); });
    }
  }

  /* Contact form: post as JSON, show the message inline, fall back to mailto. Works without JS as a plain post. */
  var form = doc.querySelector("form[data-enhance]");
  if (form && window.fetch) {
    var msg = form.querySelector(".form-msg");
    form.addEventListener("submit", function (e) {
      var hp = form.querySelector('[name="website_url"]');
      if (hp && hp.value) { e.preventDefault(); show(form.getAttribute("data-ok")); return; }
      e.preventDefault();
      var missing = [].slice.call(form.querySelectorAll("[required]")).filter(function (f) { return !f.value.trim(); })[0];
      if (missing) { show("Add your " + (missing.getAttribute("data-label") || missing.name) + " and try again."); missing.focus(); return; }
      var em = form.querySelector('[type="email"]');
      if (em && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em.value)) { show("That email doesn't look right. Check it and try again."); em.focus(); return; }
      show("Sending.");
      var data = {}; new FormData(form).forEach(function (v, k) { data[k] = v; });
      fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json(); })
        .then(function (j) { if (j && j.success) { form.reset(); show(form.getAttribute("data-ok")); } else { throw new Error("fail"); } })
        .catch(function () { show(form.getAttribute("data-err")); var fb = doc.querySelector("[data-mailto-fallback]"); if (fb) fb.hidden = false; });
    });
    function show(t) { if (msg) { msg.textContent = t; msg.hidden = false; } }
  }
})();

/* Contact and Work pages: the mailto form, the sent banner, and a prefilled email fallback for the live form. */
(function () {
  "use strict";
  var doc = document;

  function body(f) {
    var g = function (n) { var e = f.elements[n]; return e ? e.value.trim() : ""; };
    var lines = [];
    if (g("name")) lines.push("Name: " + g("name"));
    if (g("email")) lines.push("Email: " + g("email"));
    if (g("company")) lines.push("Company or project: " + g("company"));
    if (g("project_type")) lines.push("About: " + g("project_type"));
    var msg = g("body") || g("message");
    return lines.join("\n") + (msg ? "\n\n" + msg : "");
  }

  /* The form that opens the visitor's email app (used until the live form key is set). */
  var compose = doc.querySelector("form[data-compose]");
  if (compose) {
    var cmsg = compose.querySelector(".form-msg"), cfb = compose.querySelector("[data-compose-fallback]");
    compose.addEventListener("submit", function (e) {
      e.preventDefault();
      var to = compose.getAttribute("action").replace(/^mailto:/, "");
      var subject = compose.elements.subject ? compose.elements.subject.value : "New enquiry";
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body(compose));
      if (cmsg) { cmsg.textContent = "Your email app should open with the message ready to send."; cmsg.hidden = false; }
      if (cfb) { window.setTimeout(function () { cfb.hidden = false; }, 1500); }
    });
  }

  /* The live form: keep the mailto fallback link filled in with what has been typed. */
  var live = doc.querySelector("form[data-enhance]");
  if (live) {
    var link = live.querySelector("[data-mailto-fallback] a");
    var fill = function () {
      if (!link) return;
      var to = link.getAttribute("href").replace(/^mailto:/, "").split("?")[0];
      link.setAttribute("href", "mailto:" + to + "?subject=" + encodeURIComponent("New enquiry from tommyjackett.com") + "&body=" + encodeURIComponent(body(live)));
    };
    live.addEventListener("input", fill);
    live.addEventListener("change", fill);
  }

  /* Back from a plain form post (no JS path redirects to ?sent=1#sent). */
  var sent = doc.getElementById("sent");
  if (sent && /[?&]sent=1/.test(window.location.search)) {
    sent.classList.add("on");
    try { sent.focus({ preventScroll: false }); } catch (err) { /* ignore */ }
  }
})();

/* Film and stories pages: click-to-play video. The link inside .vf goes to YouTube without JS;
   with JS the youtube-nocookie iframe is created only on click, so the page stays fast. */
(function () {
  "use strict";
  var doc = document, warmed = false;
  function warm() {
    if (warmed) return; warmed = true;
    ["https://www.youtube-nocookie.com", "https://i.ytimg.com"].forEach(function (h) {
      var l = doc.createElement("link"); l.rel = "preconnect"; l.href = h; doc.head.appendChild(l);
    });
  }
  function play(box) {
    var f = doc.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + box.getAttribute("data-yt") +
      "?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3&playsinline=1&color=white";
    f.title = box.getAttribute("data-title") + ", a video by Tommy Jackett";
    f.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
    f.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
    f.setAttribute("allowfullscreen", "");
    box.classList.add("is-playing");
    box.innerHTML = "";
    box.appendChild(f);
    f.focus();
  }
  doc.addEventListener("pointerover", function (e) { if (e.target.closest && e.target.closest(".vf")) warm(); }, { passive: true });
  doc.addEventListener("touchstart", function (e) { if (e.target.closest && e.target.closest(".vf")) warm(); }, { passive: true });
  doc.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".vf-link");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
    e.preventDefault();
    play(a.parentNode);
  });
})();
