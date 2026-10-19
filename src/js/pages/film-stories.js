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
