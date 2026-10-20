/* tommyjackett.com. Menu, header, soft reveals, click-to-play videos, contact form. */
(function () {
  "use strict";
  var doc = document, body = doc.body;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* menu */
  var btn = doc.querySelector(".menu-btn"), menu = doc.getElementById("menu");
  if (btn && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      body.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
    };
    btn.addEventListener("click", function () { setMenu(!menu.classList.contains("open")); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu.classList.contains("open")) { setMenu(false); btn.focus(); } });
    window.matchMedia("(min-width: 900px)").addEventListener("change", function (e) { if (e.matches) setMenu(false); });
  }

  /* header goes solid once you scroll */
  var hd = doc.getElementById("hd");
  if (hd) {
    var onScroll = function () { hd.classList.toggle("solid", window.scrollY > 40); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* hero parallax: the photo and the cutout move together, the name moves a touch against them. Transform only. */
  var hero = doc.querySelector(".hero");
  if (hero && !reduced) {
    var ticking = false;
    var par = function () {
      ticking = false;
      var y = Math.min(window.scrollY, window.innerHeight);
      hero.style.setProperty("--py", (y * 0.07).toFixed(1));
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; window.requestAnimationFrame(par); } }, { passive: true });
  }

  /* soft fades */
  var items = [].slice.call(doc.querySelectorAll(".rv, .tl li"));
  if (items.length) {
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
      items.forEach(function (el) { io.observe(el); });
    }
  }

  /* launch wording: the HTML carries the before text; switch at the launch moment */
  [].slice.call(doc.querySelectorAll("[data-launch]")).forEach(function (el) {
    var at = Date.parse(el.getAttribute("data-launch"));
    if (at && Date.now() >= at) { el.textContent = el.getAttribute("data-after"); }
  });

  /* click to play. The link goes to YouTube if scripts are off. */
  [].slice.call(doc.querySelectorAll("a.vid-play[data-yt]")).forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var box = a.parentNode, f = doc.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + a.getAttribute("data-yt") + "?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3&playsinline=1&color=white";
      f.title = a.getAttribute("data-title") || "Video";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.setAttribute("allowfullscreen", "");
      f.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      box.replaceChild(f, a);
      f.focus();
    });
  });

  /* contact form */
  var form = doc.querySelector("form[data-form]");
  if (form) {
    var msg = form.querySelector(".form-msg");
    var show = function (t) { msg.textContent = t; msg.hidden = false; };
    if (/[?&]sent=1/.test(location.search)) { show(form.getAttribute("data-ok")); }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var hp = form.querySelector('[name="website_url"]');
      if (hp && hp.value) { show(form.getAttribute("data-ok")); return; }
      var bad = [].slice.call(form.querySelectorAll("[required]")).filter(function (f) { return !f.value.trim(); })[0];
      if (bad) { show("Add your " + bad.getAttribute("data-label") + " and try again."); bad.focus(); return; }
      var em = form.querySelector('[type="email"]');
      if (em && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em.value)) { show("That email doesn't look right."); em.focus(); return; }
      if (form.getAttribute("data-live") !== "1") { show(form.getAttribute("data-notlive")); return; }
      show("Sending.");
      var data = {}; new FormData(form).forEach(function (v, k) { data[k] = v; });
      fetch(form.getAttribute("data-endpoint"), { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json(); })
        .then(function (j) { if (j && j.success) { form.reset(); show(form.getAttribute("data-ok")); } else { throw new Error("no"); } })
        .catch(function () { show(form.getAttribute("data-err")); });
    });
  }
})();

/* Series carousel: cards curve away from the centre as you swipe. Native scroll does the moving. */
(function () {
  var cf = document.querySelector('[data-coverflow]');
  if (!cf) return;
  var cards = [].slice.call(cf.querySelectorAll('.cf-card'));
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ticking = false;
  function update() {
    ticking = false;
    if (reduce) return;
    var box = cf.getBoundingClientRect();
    var mid = box.left + box.width / 2;
    cards.forEach(function (c) {
      var r = c.getBoundingClientRect();
      var d = (r.left + r.width / 2 - mid) / r.width;
      var a = Math.max(-2, Math.min(2, d));
      var abs = Math.abs(a);
      c.style.transform = 'rotateY(' + (-a * 24) + 'deg) translateZ(' + (-abs * 110) + 'px) scale(' + (1 - Math.min(abs, 1.5) * 0.06) + ')';
      c.style.opacity = String(1 - Math.min(abs, 2) * 0.28);
      c.style.zIndex = String(10 - Math.round(abs * 3));
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  cf.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  function step(dir) {
    var w = cards[0] ? cards[0].getBoundingClientRect().width + 20 : 300;
    cf.scrollBy({ left: dir * w, behavior: reduce ? 'auto' : 'smooth' });
  }
  [].forEach.call(document.querySelectorAll('[data-cf]'), function (b) {
    b.addEventListener('click', function () { step(b.getAttribute('data-cf') === 'next' ? 1 : -1); });
  });
  cards.forEach(function (c) { c.addEventListener('focusin', function () { c.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' }); }); });
  update();
})();

/* Series rail: swipe on touch, drag with a mouse, progress line underneath. */
(function () {
  var rail = document.querySelector('[data-rail]');
  if (!rail) return;
  var bar = document.querySelector('[data-rail-bar]');
  function progress() {
    if (!bar) return;
    var max = rail.scrollWidth - rail.clientWidth;
    var vis = rail.clientWidth / rail.scrollWidth;
    bar.style.width = Math.max(12, vis * 100) + '%';
    var p = max > 0 ? rail.scrollLeft / max : 0;
    bar.style.transform = 'translateX(' + (p * (100 / Math.max(.12, vis) - 100)) + '%)';
  }
  rail.addEventListener('scroll', function () { requestAnimationFrame(progress); }, { passive: true });
  window.addEventListener('resize', progress);
  progress();
  var down = false, startX = 0, startL = 0, moved = false;
  rail.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse') return;
    down = true; moved = false; startX = e.clientX; startL = rail.scrollLeft;
  });
  window.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - startX;
    if (Math.abs(dx) > 4) { moved = true; rail.classList.add('drag'); }
    rail.scrollLeft = startL - dx;
  });
  window.addEventListener('pointerup', function () {
    if (!down) return;
    down = false;
    setTimeout(function () { rail.classList.remove('drag'); }, 0);
  });
  rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
  rail.addEventListener('keydown', function (e) {
    var w = rail.querySelector('.rc') ? rail.querySelector('.rc').getBoundingClientRect().width + 24 : 300;
    if (e.key === 'ArrowRight') { rail.scrollBy({ left: w, behavior: 'smooth' }); e.preventDefault(); }
    if (e.key === 'ArrowLeft') { rail.scrollBy({ left: -w, behavior: 'smooth' }); e.preventDefault(); }
  });
})();

/* Series player: pick a series to feature it, press play to watch in a pop-up. */
(function () {
  var dataEl = document.getElementById('series-data');
  var wrap = document.querySelector('[data-series]');
  if (!dataEl || !wrap) return;
  var items = JSON.parse(dataEl.textContent);
  var bySlug = {}; items.forEach(function (s) { bySlug[s.slug] = s; });
  var active = items[0];
  var img = wrap.querySelector('[data-ft-img]'), title = wrap.querySelector('[data-ft-title]'),
      line = wrap.querySelector('[data-ft-line]'), tag = wrap.querySelector('[data-ft-tag]'), playBtn = wrap.querySelector('[data-play]');
  var dlg = document.querySelector('[data-player]'), frame = document.querySelector('[data-frame]');

  function feature(s, focusPlay) {
    active = s;
    img.classList.add('swap');
    setTimeout(function () {
      img.src = s.cover; img.alt = s.alt; title.textContent = s.title; line.textContent = s.line;
      img.parentNode.classList.toggle('ft3-pic--sq', !!s.sq);
      img.onload = function () { img.classList.remove('swap'); };
      setTimeout(function () { img.classList.remove('swap'); }, 400);
    }, 180);
    tag.hidden = s.slug !== items[0].slug;
    playBtn.setAttribute('aria-label', s.ids.length ? 'Play ' + s.title : 'Go to ' + s.title);
    playBtn.classList.toggle('play--go', !s.ids.length);
    playBtn.querySelector('path').setAttribute('d', s.ids.length ? 'M8 5.5v13l11-6.5z' : 'M5 12h12M12 6.5l5.5 5.5-5.5 5.5');
    playBtn.querySelector('path').setAttribute('fill', s.ids.length ? 'currentColor' : 'none');
    playBtn.querySelector('path').setAttribute('stroke', s.ids.length ? 'none' : 'currentColor');
    playBtn.querySelector('path').setAttribute('stroke-width', '2');
    [].forEach.call(wrap.querySelectorAll('[data-pick]'), function (b) { b.parentNode.hidden = b.getAttribute('data-pick') === s.slug; });
    if (focusPlay) playBtn.focus({ preventScroll: true });
  }
  [].forEach.call(wrap.querySelectorAll('[data-pick]'), function (b) {
    b.addEventListener('click', function () {
      feature(bySlug[b.getAttribute('data-pick')], true);
      if (window.matchMedia('(max-width: 899px)').matches) wrap.querySelector('.ft3').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });

  function open() {
    if (!active.ids.length) { if (active.href) location.href = active.href; return; }
    var first = active.ids[0], rest = active.ids.slice(1);
    var src = 'https://www.youtube-nocookie.com/embed/' + first + '?autoplay=1&rel=0&modestbranding=1&playsinline=1' + (rest.length ? '&playlist=' + rest.join(',') : '');
    frame.innerHTML = '<iframe src="' + src + '" title="' + active.title.replace(/"/g, '&quot;') + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
  }
  function close() { frame.innerHTML = ''; if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); playBtn.focus({ preventScroll: true }); }
  playBtn.addEventListener('click', open);
  dlg.querySelector('[data-close]').addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  dlg.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
})();
