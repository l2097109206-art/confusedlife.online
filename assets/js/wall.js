// The Clarity Wall — front-end interactivity
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  const state = { step: 1, category: null, stuck: null, duration: null, anonymous: true, email: "" };

  // ---------- Wizard navigation ----------
  const steps = $$(".wstep");
  const progBar = $("#progBar");
  const stepLabel = $("#stepLabel");
  const backBtn = $("#backBtn");
  const nextBtn = $("#nextBtn");
  const submitBtn = $("#submitBtn");
  const formMsg = $("#formMsg");

  function showStep(n) {
    state.step = n;
    steps.forEach((el) => (el.hidden = Number(el.dataset.step) !== n));
    progBar.style.width = (n / 4) * 100 + "%";
    stepLabel.textContent = `Step ${n} of 4`;
    backBtn.hidden = n === 1;
    nextBtn.hidden = n === 4;
    submitBtn.hidden = n !== 4;
    validate();
  }

  function validate() {
    let ok = false;
    if (state.step === 1) ok = !!state.category;
    else if (state.step === 2) ok = words($("#storyInput").value) >= 12;
    else if (state.step === 3) ok = !!state.stuck && !!state.duration;
    else if (state.step === 4) ok = !($("#optEmail").checked && !isEmail($("#emailInput").value));
    nextBtn.disabled = !ok;
    submitBtn.disabled = !ok;
  }

  function words(s) { return s.trim().split(/\s+/).filter(Boolean).length; }
  function isEmail(s) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s.trim()); }

  // Step 1 — category
  $$("#catGrid .cat-card").forEach((b) => {
    b.addEventListener("click", () => {
      state.category = b.dataset.cat;
      $$("#catGrid .cat-card").forEach((x) => x.setAttribute("aria-pressed", x === b));
      validate();
    });
  });

  // Step 2 — word count
  const story = $("#storyInput");
  story.addEventListener("input", () => {
    const w = words(story.value);
    $("#wc").textContent = w;
    $("#wcHint").textContent = w < 100 ? "keep going" : w > 500 ? "plenty — trim if you like" : "great range";
    validate();
  });

  // Step 3 — scale + duration
  $$("#stuckScale button").forEach((b) => {
    b.addEventListener("click", () => {
      state.stuck = b.dataset.val;
      $$("#stuckScale button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      validate();
    });
  });
  $$("#durRow button").forEach((b) => {
    b.addEventListener("click", () => {
      state.duration = b.dataset.dur;
      $$("#durRow button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      validate();
    });
  });

  // Step 4 — options
  $("#optAnon").addEventListener("change", (e) => (state.anonymous = e.target.checked));
  $("#optEmail").addEventListener("change", (e) => ($("#emailField").hidden = !e.target.checked));
  $("#emailInput").addEventListener("input", () => { state.email = $("#emailInput").value; validate(); });

  backBtn.addEventListener("click", () => showStep(state.step - 1));
  nextBtn.addEventListener("click", () => showStep(state.step + 1));

  // ---------- Submit ----------
  submitBtn.addEventListener("click", async () => {
    submitBtn.disabled = true;
    formMsg.textContent = "Generating your reflection…";
    formMsg.className = "form-msg";
    const payload = {
      category: state.category,
      text: story.value,
      stuck: state.stuck,
      duration: state.duration,
      anonymous: $("#optAnon").checked,
      email: $("#optEmail").checked ? $("#emailInput").value.trim() : null,
    };
    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.crisis) { openCrisis(); resetWizard(); return; }
      if (!data.ok) {
        formMsg.textContent = data.error || "Something went wrong. Please try again.";
        formMsg.className = "form-msg err";
        submitBtn.disabled = false;
        return;
      }
      if (data.post) prependPost(data.post);
      renderReport(data.report);
      $("#wizard").hidden = true;
      $("#reportView").hidden = false;
      $("#reportView").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (e) {
      formMsg.textContent = "Couldn't reach the server. Please try again in a moment.";
      formMsg.className = "form-msg err";
      submitBtn.disabled = false;
    }
  });

  function resetWizard() {
    state.step = 1; state.category = null; state.stuck = null; state.duration = null;
    story.value = ""; $("#wc").textContent = "0";
    $$("#catGrid .cat-card").forEach((x) => x.setAttribute("aria-pressed", "false"));
    $$("#stuckScale button").forEach((x) => x.setAttribute("aria-pressed", "false"));
    $$("#durRow button").forEach((x) => x.setAttribute("aria-pressed", "false"));
    $("#optAnon").checked = true; $("#optEmail").checked = false; $("#emailField").hidden = true;
    $("#emailInput").value = "";
    $("#wizard").hidden = false; $("#reportView").hidden = true;
    showStep(1);
  }
  $("#againBtn").addEventListener("click", resetWizard);

  // ---------- Report render ----------
  function renderReport(r) {
    $("#repRoot p").textContent = r.rootCause || "";
    $("#repMind p").textContent = r.mindset || "";
    const ol = $("#repAct ol"); ol.innerHTML = "";
    (r.actions || []).forEach((a) => { const li = document.createElement("li"); li.textContent = a; ol.appendChild(li); });
    const ul = $("#repRes ul"); ul.innerHTML = "";
    (r.resources || []).forEach((x) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = x.url; a.textContent = x.title; a.target = "_blank"; a.rel = "noopener";
      li.appendChild(a); ul.appendChild(li);
    });
    window.__reportQuote = pickQuote(r);
  }
  function pickQuote(r) {
    const s = (r.rootCause || "").split(/(?<=[.!?])\s/)[0] || "You're not broken — you're between chapters.";
    return s.length > 140 ? s.slice(0, 137) + "…" : s;
  }

  // ---------- Feed ----------
  const feedGrid = $("#feedGrid");
  const REACT = { alone: "🤝 You're not alone", clarity: "💡 Sending clarity", hug: "❤️ Hug" };

  async function loadFeed() {
    try {
      const res = await fetch("/api/wall");
      const data = await res.json();
      feedGrid.innerHTML = "";
      if (!data.posts || !data.posts.length) {
        feedGrid.innerHTML = '<p class="muted">The wall is quiet — be the first to share.</p>';
        return;
      }
      data.posts.slice(0, 24).forEach((p) => feedGrid.appendChild(postEl(p)));
    } catch {
      feedGrid.innerHTML = '<p class="muted">Couldn\'t load the wall right now.</p>';
    }
  }

  function postEl(p) {
    const card = document.createElement("article");
    card.className = "post-card";
    card.innerHTML = `
      <span class="post-tag">${p.tag}</span>
      <p class="post-text">${escapeHtml(p.text)}</p>
      <div class="post-meta"><span>${p.author}</span><span>· stuck ${p.stuck}/5</span><span>· ${relTime(p.ts)}</span></div>
      <div class="reactions">
        ${Object.keys(REACT).map((k) => `<button class="react-btn" data-kind="${k}">${REACT[k]} <span class="n">${p.reactions?.[k] || 0}</span></button>`).join("")}
      </div>
      <button class="comments-toggle">${p.comments?.length ? p.comments.length + " replies" : "Reply / support"}</button>
      <div class="comments" hidden></div>`;
    const reactions = $(".reactions", card);
    reactions.addEventListener("click", async (e) => {
      const btn = e.target.closest(".react-btn"); if (!btn) return;
      const kind = btn.dataset.kind; btn.querySelector(".n").textContent = (p.reactions[kind] = (p.reactions[kind] || 0) + 1);
      try {
        const res = await fetch("/api/react", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ postId: p.id, kind }) });
        const d = await res.json(); if (d.ok) btn.querySelector(".n").textContent = d.reactions[kind];
      } catch {}
    });
    const toggle = $(".comments-toggle", card);
    const box = $(".comments", card);
    toggle.addEventListener("click", () => {
      box.hidden = !box.hidden;
      if (!box.hidden && !box.dataset.built) { buildComments(p, box); box.dataset.built = "1"; }
    });
    return card;
  }

  function buildComments(p, box) {
    (p.comments || []).forEach((c) => box.appendChild(commentEl(c)));
    const form = document.createElement("form");
    form.className = "comment-form";
    form.innerHTML = `
      <textarea placeholder="What would you tell them?"></textarea>
      <select>${["Been there, solved it", "Currently in the same boat", "Just here to listen"].map((t) => `<option>${t}</option>`).join("")}</select>
      <div class="row"><button type="submit" class="btn btn-primary">Post reply</button></div>`;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const ta = $("textarea", form); const text = ta.value.trim(); if (!text) return;
      const tag = $("select", form).value;
      try {
        const res = await fetch("/api/comment", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ postId: p.id, text, tag }) });
        const d = await res.json();
        if (d.ok) { box.innerHTML = ""; (d.comments || []).forEach((c) => box.appendChild(commentEl(c))); box.appendChild(form); }
        else if (d.blocked) { ta.value = ""; ta.placeholder = "That reply couldn't be posted. Keep it kind."; }
      } catch {}
    });
    box.appendChild(form);
  }

  function commentEl(c) {
    const d = document.createElement("div");
    d.className = "comment";
    d.innerHTML = `<span class="ctag">${escapeHtml(c.tag)}</span><div>${escapeHtml(c.text)}</div>`;
    return d;
  }

  function prependPost(p) {
    feedGrid.querySelector(".muted")?.remove();
    feedGrid.prepend(postEl(p));
  }

  function relTime(ts) {
    const s = Math.floor((Date.now() - ts) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return Math.floor(s / 60) + "m ago";
    if (s < 86400) return Math.floor(s / 3600) + "h ago";
    return Math.floor(s / 86400) + "d ago";
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---------- Crisis modal ----------
  const crisisModal = $("#crisisModal");
  $("#crisisClose").addEventListener("click", () => (crisisModal.hidden = true));
  function openCrisis() { crisisModal.hidden = false; }

  // ---------- Share card ----------
  const shareModal = $("#shareModal");
  $("#shareCardBtn").addEventListener("click", () => { drawCard(window.__reportQuote || "You're not broken — you're between chapters."); shareModal.hidden = false; });
  $("#shareClose").addEventListener("click", () => (shareModal.hidden = true));
  $("#dlCard").addEventListener("click", (e) => {
    e.preventDefault();
    const a = e.currentTarget; a.href = $("#shareCanvas").toDataURL("image/png");
    const ev = new MouseEvent("click", { bubbles: true, cancelable: true, view: window });
    a.dispatchEvent(ev);
  });
  function drawCard(quote) {
    const c = $("#shareCanvas"); const x = c.getContext("2d");
    const W = c.width, H = c.height;
    x.fillStyle = "#0E6B5C"; x.fillRect(0, 0, W, H);
    x.fillStyle = "#F4EFE6"; x.fillRect(70, 70, W - 140, H - 140);
    x.fillStyle = "#0E6B5C"; x.beginPath(); x.arc(130, 130, 14, 0, 7); x.fill();
    x.fillStyle = "#1f2a28"; x.font = "600 30px Georgia, 'Times New Roman', serif";
    x.fillText("confusedlife.online", 165, 140);
    x.fillStyle = "#1f2a28"; x.font = "italic 300 62px Georgia, 'Times New Roman', serif";
    wrapText(x, "“" + quote + "”", 110, 360, W - 220, 78);
    x.fillStyle = "#0E6B5C"; x.font = "600 28px Georgia, serif";
    x.fillText("A little clarity for when life stops making sense.", 110, H - 130);
  }
  function wrapText(ctx, text, x, y, maxW, lh) {
    const words = text.split(" "); let line = ""; let yy = y;
    for (const w of words) {
      const test = line + w + " ";
      if (ctx.measureText(test).width > maxW && line) { ctx.fillText(line.trim(), x, yy); line = w + " "; yy += lh; }
      else line = test;
    }
    ctx.fillText(line.trim(), x, yy);
  }

  showStep(1);
  loadFeed();
})();
