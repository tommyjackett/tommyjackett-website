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
