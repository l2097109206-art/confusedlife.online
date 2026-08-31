/* ConfusedLife.online — global behaviour
   No dependencies, no frameworks. Progressive enhancement only. */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("primary-nav");
    if (!toggle || !nav) return;

    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.dataset.open = String(open);
    };
    setOpen(false);

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    // Close on link tap, on Escape, and on resize back to desktop
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) setOpen(false);
    });
  }

  /* ---------- Reading progress bar ---------- */
  function initProgress() {
    var bar = document.querySelector(".progress-bar");
    if (!bar) return;
    var target = document.querySelector(".article-body") || document.body;
    var raf = null;

    var update = function () {
      raf = null;
      var doc = document.documentElement;
      var start = target.offsetTop;
      var span = target.offsetHeight - window.innerHeight;
      if (span <= 0) {
        // Short page: reflect raw document scroll instead
        var docSpan = doc.scrollHeight - window.innerHeight;
        bar.style.width = docSpan > 0 ? (window.scrollY / docSpan) * 100 + "%" : "0%";
        return;
      }
      var pct = ((window.scrollY - start) / span) * 100;
      bar.style.width = Math.max(0, Math.min(100, pct)) + "%";
    };

    window.addEventListener("scroll", function () {
      if (raf === null) raf = window.requestAnimationFrame(update);
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  }

  /* ---------- Table of contents: active section highlight ---------- */
  function initToc() {
    var toc = document.querySelector(".toc");
    if (!toc) return;
    var links = Array.prototype.slice.call(toc.querySelectorAll("a[href^='#']"));
    if (!links.length) return;

    var byId = {};
    var sections = [];
    links.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      var el = document.getElementById(id);
      if (el) {
        byId[id] = link;
        sections.push(el);
      }
    });
    if (!sections.length) return;

    var visible = new Set();
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target.id);
        else visible.delete(entry.target.id);
      });
      var current = null;
      for (var i = 0; i < sections.length; i++) {
        if (visible.has(sections[i].id)) { current = sections[i].id; break; }
      }
      links.forEach(function (l) { l.classList.remove("is-active"); });
      if (current && byId[current]) byId[current].classList.add("is-active");
    }, { rootMargin: "-15% 0px -70% 0px", threshold: 0 });

    sections.forEach(function (s) { observer.observe(s); });

    // Smooth scroll that respects the sticky header
    links.forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = decodeURIComponent(link.getAttribute("href").slice(1));
        var el = document.getElementById(id);
        if (!el) return;
        e.preventDefault();
        var top = el.getBoundingClientRect().top + window.scrollY - 90;
        window.scrollTo({ top: top, behavior: "smooth" });
        history.replaceState(null, "", "#" + id);
      });
    });
  }

  /* ---------- Quote cards: copy + share ---------- */
  function initQuotes() {
    var cards = document.querySelectorAll(".quote-card");
    if (!cards.length) return;

    var flash = function (btn, ok) {
      var original = btn.dataset.label || "";
      btn.classList.add("is-done");
      btn.innerHTML = ok
        ? '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>'
        : '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
      window.setTimeout(function () {
        btn.classList.remove("is-done");
        btn.innerHTML = original;
      }, 1800);
    };

    cards.forEach(function (card) {
      var textEl = card.querySelector(".quote-text");
      var authorEl = card.querySelector(".quote-author");
      if (!textEl) return;

      var full = '"' + textEl.textContent.trim() + '"';
      if (authorEl && authorEl.textContent.trim()) full += " — " + authorEl.textContent.trim();

      var copyBtn = card.querySelector("[data-action='copy']");
      if (copyBtn) {
        copyBtn.dataset.label = copyBtn.innerHTML;
        copyBtn.setAttribute("aria-label", "Copy quote to clipboard");
        copyBtn.addEventListener("click", function () {
          var done = function (ok) { flash(copyBtn, ok); };
          if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(full + "\n\n— confusedlife.online").then(function () { done(true); }, function () { done(false); });
          } else {
            // http fallback for local preview
            var ta = document.createElement("textarea");
            ta.value = full;
            ta.style.position = "fixed";
            ta.style.opacity = "0";
            document.body.appendChild(ta);
            ta.select();
            var ok = false;
            try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
            document.body.removeChild(ta);
            done(ok);
          }
        });
      }

      var shareBtn = card.querySelector("[data-action='share']");
      if (shareBtn) {
        shareBtn.dataset.label = shareBtn.innerHTML;
        shareBtn.setAttribute("aria-label", "Share this quote");
        shareBtn.addEventListener("click", function () {
          var url = location.origin + "/quotes/";
          if (navigator.share) {
            navigator.share({ title: "Confused about life", text: full, url: url }).catch(function () {});
          } else if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(full + "\n" + url).then(function () { flash(shareBtn, true); }, function () { flash(shareBtn, false); });
          } else {
            window.open("https://twitter.com/intent/tweet?text=" + encodeURIComponent(full), "_blank", "noopener");
          }
        });
      }
    });
  }

  /* ---------- Footer year ---------- */
  function initYear() {
    var el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  /* ---------- Newsletter: graceful no-backend handling ---------- */
  function initSignup() {
    var form = document.querySelector("[data-signup]");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector("input[type='email']");
      var note = form.parentNode.querySelector(".form-note");
      if (!input || !input.value) return;
      if (note) {
        note.textContent = "Thanks — we've noted your interest. We'll email you when new guides go live.";
        note.style.color = "var(--teal)";
      }
      input.value = "";
      input.blur();
    });
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    initNav();
    initProgress();
    initToc();
    initQuotes();
    initYear();
    initSignup();
  });
})();
