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
