/* ConfusedLife.online — Clarity Quiz
   A reflective self-check, not a diagnostic instrument.
   Everything runs locally in the browser: no network calls, no data stored. */
(function () {
  "use strict";

  var DIMENSIONS = [
    { key: "direction", label: "Direction" },
    { key: "values",    label: "Values" },
    { key: "energy",    label: "Energy" },
    { key: "connection",label: "Connection" }
  ];

  /* score: 0 = most stuck, 3 = most grounded */
  var QUESTIONS = [
    {
      dim: "direction",
      text: "When you picture your life five years from now, what comes up first?",
      options: [
        { label: "Nothing much — it's blank, or it just stresses me out", score: 0 },
        { label: "A vague shape, but I couldn't describe it to anyone", score: 1 },
        { label: "A few things I'd like, though I'm unsure how to get there", score: 2 },
        { label: "A reasonably clear picture I'm actively moving toward", score: 3 }
      ]
    },
    {
      dim: "direction",
      text: "How often does a week go by where you're mostly just going through the motions?",
      options: [
        { label: "Almost every week", score: 0 },
        { label: "Most weeks, honestly", score: 1 },
        { label: "Sometimes — but I also have weeks that feel real", score: 2 },
        { label: "Rarely; my days usually feel like they're going somewhere", score: 3 }
      ]
    },
    {
      dim: "direction",
      text: "If someone asked \"what are you working toward right now?\" — how easy is it to answer?",
      options: [
        { label: "I'd have to make something up", score: 0 },
        { label: "Hard. I'd give a vague answer and change the subject", score: 1 },
        { label: "I could say something, though it feels incomplete", score: 2 },
        { label: "Easy — it might be messy, but I know what it is", score: 3 }
      ]
    },

    {
      dim: "values",
      text: "Could you name the three things that matter most to you right now?",
      options: [
        { label: "No — I genuinely don't know anymore", score: 0 },
        { label: "Maybe one, and even that feels borrowed from someone else", score: 1 },
        { label: "Yes, roughly, though I haven't thought about it in a while", score: 2 },
        { label: "Yes, and I've tested them against real decisions", score: 3 }
      ]
    },
    {
      dim: "values",
      text: "How well do your daily choices match what you say you care about?",
      options: [
        { label: "They mostly contradict each other", score: 0 },
        { label: "There's a gap I try not to look at too closely", score: 1 },
        { label: "Some alignment, some drift", score: 2 },
        { label: "Fairly aligned — not perfectly, but honestly", score: 3 }
      ]
    },
    {
      dim: "values",
      text: "When did you last make a decision you felt genuinely proud of?",
      options: [
        { label: "I can't remember", score: 0 },
        { label: "It's been a long time", score: 1 },
        { label: "Within the past few months", score: 2 },
        { label: "Recently, and I'd make the same call again", score: 3 }
      ]
    },

    {
      dim: "energy",
      text: "Roughly how much of your week goes to things that feel meaningful rather than merely necessary?",
      options: [
        { label: "Almost none — it's all obligation", score: 0 },
        { label: "A small slice, and it's the first thing I cut", score: 1 },
        { label: "Some — I protect it when I can", score: 2 },
        { label: "A decent amount; I've made room for it", score: 3 }
      ]
    },
    {
      dim: "energy",
      text: "When something genuinely interests you, what usually happens?",
      options: [
        { label: "I talk myself out of it before I start", score: 0 },
        { label: "I think about it a lot and rarely act", score: 1 },
        { label: "Sometimes I follow it, sometimes I let it go", score: 2 },
        { label: "I usually follow it, even if only in a small way", score: 3 }
      ]
    },
    {
      dim: "energy",
      text: "How has your baseline energy been — sleep, appetite, motivation?",
      options: [
        { label: "Depleted most days, and it's been going on a while", score: 0 },
        { label: "Low more often than not", score: 1 },
        { label: "Up and down", score: 2 },
        { label: "Mostly steady", score: 3 }
      ]
    },

    {
      dim: "connection",
      text: "Is there someone you could call today to talk about how you're actually doing?",
      options: [
        { label: "No one comes to mind", score: 0 },
        { label: "Maybe, but I wouldn't — it'd feel like a burden", score: 1 },
        { label: "One or two people, though I rarely take them up on it", score: 2 },
        { label: "Yes, and I'd actually pick up the phone", score: 3 }
      ]
    },
    {
      dim: "connection",
      text: "Do you feel like the people around you really know you?",
      options: [
        { label: "No — I feel invisible or like I'm performing", score: 0 },
        { label: "Not really. I keep most of it to myself", score: 1 },
        { label: "Partly — some people, some parts of me", score: 2 },
        { label: "Yes, with at least a few people", score: 3 }
      ]
    },
    {
      dim: "connection",
      text: "How much of your thinking time goes to comparing your life with other people's?",
      options: [
        { label: "Most of it, and it always makes me feel behind", score: 0 },
        { label: "A lot more than I'd like to admit", score: 1 },
        { label: "Some, but I can usually catch myself", score: 2 },
        { label: "Occasionally — it doesn't run the show", score: 3 }
      ]
    }
  ];

  var PROFILES = [
    {
      max: 14,
      name: "Deep Fog",
      tone: "clay",
      headline: "You're in the thick of it — and that's more common than it feels right now.",
      body: "A score in this range usually means the confusion isn't about one decision. It's that the things which normally orient you — direction, values, energy, connection — have all gone quiet at once. That's exhausting, and it's also why the usual advice (\"just pick a goal!\") feels insulting right now.\n\nThe most useful next step is not a five-year plan. It's stabilising the floor: sleep, food, movement, and one honest conversation. Clarity tends to return after the basics are steady, not before.",
      steps: [
        "Start with your body, not your purpose. Sleep and movement shift mood faster than insight does.",
        "Tell one person something true. It doesn't have to be eloquent — \"I've been struggling lately\" is enough.",
        "Lower the bar for what counts as progress. Making your bed is not a metaphor; it's just today's win."
      ],
      read: [
        { href: "/guides/feeling-lost-in-life/", label: "Feeling Lost in Life: A Practical Guide" },
        { href: "/guides/signs-you-are-feeling-lost/", label: "15 Signs You're Feeling Lost (and what to do about them)" },
        { href: "/guides/why-am-i-so-confused-about-life/", label: "Why You Feel So Confused About Life" }
      ]
    },
    {
      max: 22,
      name: "The Drift",
      tone: "amber",
      headline: "You're functioning, but on autopilot — and you can feel the gap.",
      body: "This is the most under-discussed state there is. From the outside you look fine: you show up, you get things done. But you're not really in your own life, and the days have a flat, borrowed quality.\n\nDrift usually isn't a crisis — it's a signal that something you once chose has quietly become something you merely inherited. The fix isn't to burn it all down. It's to find one small place where your actual preference still has a vote, and act on it this week.",
      steps: [
        "Pick one area — work, a relationship, your weekends — and ask: did I choose this, or did I drift into it?",
        "Reintroduce one thing you used to enjoy before it became productive. Do it badly, on purpose.",
        "Notice which parts of your week you'd keep if nobody were watching. That's data."
      ],
      read: [
        { href: "/guides/feeling-lost-in-life/", label: "Feeling Lost in Life: A Practical Guide" },
        { href: "/guides/i-dont-know-what-to-do-with-my-life/", label: "\"I Don't Know What to Do With My Life\"" },
        { href: "/guides/how-to-find-your-purpose/", label: "How to Find Your Purpose (Without Auditing Your Soul)" }
      ]
    },
    {
      max: 29,
      name: "The Crossroads",
      tone: "teal",
      headline: "You have options — that's exactly why it feels hard.",
      body: "This range is uncomfortable in a different way. You're not lost; you're over-choice. You can see several plausible futures and can't yet tell which one is yours, so you stall — waiting for a certainty that decisions like this rarely offer in advance.\n\nHere's the reframe that helps most: almost none of these paths is permanent. The goal isn't to pick the perfect road. It's to pick the one you'd regret not trying, and treat the first year as research.",
      steps: [
        "Run a 30-day experiment on one option instead of deciding it forever.",
        "Ask \"what would I regret not trying?\" rather than \"what's the right answer?\"",
        "Set a decision deadline. Indefinite deliberation is itself a choice, and it's the tiring one."
      ],
      read: [
        { href: "/guides/i-dont-know-what-to-do-with-my-life/", label: "\"I Don't Know What to Do With My Life\"" },
        { href: "/guides/how-to-find-your-purpose/", label: "How to Find Your Purpose (Without Auditing Your Soul)" },
        { href: "/guides/quarter-life-crisis/", label: "Quarter-Life Crisis: What It Is and How to Move Through It" }
      ]
    },
    {
      max: 36,
      name: "Steady Ground",
      tone: "teal",
      headline: "You're more grounded than the search that brought you here suggests.",
      body: "A high score doesn't mean life is sorted — it means the foundations are holding. If you landed here, you may not be lost so much as restless, or simply at a point where an old version of your life no longer fits a newer version of you.\n\nThat's not a problem to solve. It's a transition to move through, usually by editing rather than rebuilding. Protect what's working, and change one thing at a time so you can actually tell what helped.",
      steps: [
        "Protect the routines that are working before you add anything new.",
        "Change one variable at a time — otherwise you won't know what actually made the difference.",
        "Consider whether you're actually confused, or just bored. They need different responses."
      ],
      read: [
        { href: "/guides/how-to-find-your-purpose/", label: "How to Find Your Purpose (Without Auditing Your Soul)" },
        { href: "/guides/feeling-lost-in-life/", label: "Feeling Lost in Life: A Practical Guide" },
        { href: "/quotes/confused-about-life/", label: "Quotes for When Life Feels Confusing" }
      ]
    }
  ];

  var TONE_COLORS = {
    clay:  { fg: "var(--clay)",  wash: "var(--clay-wash)",  fill: "var(--clay)" },
    amber: { fg: "var(--amber)", wash: "var(--amber-wash)", fill: "var(--amber)" },
    teal:  { fg: "var(--teal)",  wash: "var(--teal-wash)",  fill: "var(--teal)" }
  };

  var LETTERS = ["A", "B", "C", "D"];
  var MAX_SCORE = QUESTIONS.length * 3; // 36

  var state = { index: 0, answers: new Array(QUESTIONS.length).fill(null) };

  var el = {};

  function qs(sel) { return document.querySelector(sel); }

  function esc(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ---------- Render one question ---------- */
  function renderQuestion() {
    var q = QUESTIONS[state.index];
    var answered = state.answers[state.index];

    el.qNum.textContent = "Question " + (state.index + 1) + " of " + QUESTIONS.length;
    el.fill.style.width = ((state.index) / QUESTIONS.length) * 100 + "%";
    el.q.textContent = q.text;

    var html = '<fieldset style="border:0;margin:0;padding:0"><legend class="visually-hidden">' + esc(q.text) + "</legend><div class=\"quiz-options\">";
    q.options.forEach(function (opt, i) {
      var selected = answered === i ? " is-selected" : "";
      var checked = answered === i ? " checked" : "";
      html +=
        '<label class="quiz-option' + selected + '">' +
          '<input type="radio" name="q' + state.index + '" value="' + i + '" class="visually-hidden"' + checked + ">" +
          '<span class="quiz-key" aria-hidden="true">' + LETTERS[i] + "</span>" +
          "<span>" + esc(opt.label) + "</span>" +
        "</label>";
    });
    html += "</div></fieldset>";

    el.body.innerHTML = html;

    var inputs = el.body.querySelectorAll("input[type='radio']");
    Array.prototype.forEach.call(inputs, function (input) {
      input.addEventListener("change", function () {
        state.answers[state.index] = parseInt(input.value, 10);
        Array.prototype.forEach.call(el.body.querySelectorAll(".quiz-option"), function (lbl, i) {
          lbl.classList.toggle("is-selected", i === state.answers[state.index]);
        });
        el.next.disabled = false;
      });
    });

    el.next.disabled = answered === null;
    el.next.textContent = state.index === QUESTIONS.length - 1 ? "See my results" : "Next";
    el.back.disabled = state.index === 0;
  }

  /* ---------- Scoring ---------- */
  function score() {
    var total = 0;
    var dims = {};
    DIMENSIONS.forEach(function (d) { dims[d.key] = { sum: 0, max: 0 }; });

    QUESTIONS.forEach(function (q, i) {
      var s = state.answers[i] || 0;
      total += s;
      dims[q.dim].sum += s;
      dims[q.dim].max += 3;
    });

    var profile = PROFILES.find(function (p) { return total <= p.max; }) || PROFILES[PROFILES.length - 1];
    return { total: total, dims: dims, profile: profile };
  }

  /* ---------- Render results ---------- */
  function renderResult() {
    var r = score();
    var tone = TONE_COLORS[r.profile.tone] || TONE_COLORS.teal;
    var pct = Math.round((r.total / MAX_SCORE) * 100);

    el.fill.style.width = "100%";
    el.qNum.textContent = "Your result";
    el.q.textContent = "Where you are right now";

    var dimRows = DIMENSIONS.map(function (d) {
      var item = r.dims[d.key];
      var dPct = Math.round((item.sum / item.max) * 100);
      var barColor = dPct <= 33 ? "var(--clay)" : dPct <= 66 ? "var(--amber)" : "var(--teal)";
      return (
        '<div class="dim-row">' +
          '<span class="dim-label">' + esc(d.label) + "</span>" +
          '<span class="dim-bar"><span class="dim-fill" style="width:' + dPct + "%;background:" + barColor + '"></span></span>' +
          '<span class="dim-val">' + item.sum + "/" + item.max + "</span>" +
        "</div>"
      );
    }).join("");

    var steps = r.profile.steps.map(function (s) {
      return "<li>" + esc(s) + "</li>";
    }).join("");

    var reads = r.profile.read.map(function (l) {
      return '<li><a href="' + esc(l.href) + '">' + esc(l.label) + "</a></li>";
    }).join("");

    el.body.innerHTML =
      '<div class="quiz-result">' +
        '<span class="result-badge" style="background:' + tone.wash + ";color:" + tone.fg + '">' + esc(r.profile.name) + "</span>" +
        '<div class="result-score"><strong>' + r.total + "</strong><span>of " + MAX_SCORE + " &middot; " + pct + "% grounded</span></div>" +
        '<div class="result-meter"><div class="result-meter-fill" style="width:' + pct + "%;background:" + tone.fill + '"></div></div>' +
        '<h3 style="font-size:1.3rem;margin-bottom:.6rem">' + esc(r.profile.headline) + "</h3>" +
        r.profile.body.split("\n\n").map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("") +
        '<h4 style="margin-top:1.75rem">Where your answers clustered</h4>' +
        '<div class="result-dims">' + dimRows + "</div>" +
        '<div class="callout callout-note" style="margin-top:1.5rem">' +
          '<p class="callout-title">Three things to try this week</p>' +
          "<ol>" + steps + "</ol>" +
        "</div>" +
        "<h4>Read next</h4><ul>" + reads + "</ul>" +
        '<p class="text-small text-soft" style="margin-top:1.75rem;padding-top:1.25rem;border-top:1px solid var(--line)">' +
          "This quiz is a reflective tool, not a diagnosis. It hasn't been validated clinically, and a low score isn't a verdict &mdash; it's a snapshot of a week, and weeks change. " +
          'If you\'re struggling, please read our <a href="/disclaimer/">disclaimer</a> or talk to a qualified professional.' +
        "</p>" +
      "</div>";

    el.back.disabled = false;
    el.back.textContent = "Back";
    el.next.textContent = "Share result";
    el.next.disabled = false;
    el.next.dataset.mode = "share";
  }

  function shareResult() {
    var r = score();
    var text = "I scored " + r.total + "/" + MAX_SCORE + " on the Clarity Quiz (" + r.profile.name + "). " + location.origin + "/tools/clarity-quiz/";
    if (navigator.share) {
      navigator.share({ title: "Clarity Quiz — confusedlife.online", text: text }).catch(function () {});
    } else if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () {
        el.next.textContent = "Copied";
        window.setTimeout(function () { el.next.textContent = "Share result"; }, 1800);
      });
    } else {
      window.open("https://twitter.com/intent/tweet?text=" + encodeURIComponent(text), "_blank", "noopener");
    }
  }

  function restart() {
    state.index = 0;
    state.answers = new Array(QUESTIONS.length).fill(null);
    el.next.dataset.mode = "next";
    renderQuestion();
    if (el.shell) el.shell.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function init() {
    var shell = qs("[data-quiz]");
    if (!shell) return;
    el.shell = shell;
    el.qNum = shell.querySelector("[data-quiz-progress]");
    el.fill = shell.querySelector(".quiz-fill");
    el.q = shell.querySelector("[data-quiz-question]");
    el.body = shell.querySelector("[data-quiz-body]");
    el.back = shell.querySelector("[data-quiz-back]");
    el.next = shell.querySelector("[data-quiz-next]");
    if (!el.q || !el.body || !el.next || !el.back) return;

    el.next.addEventListener("click", function () {
      if (el.next.dataset.mode === "share") { shareResult(); return; }
      if (state.index < QUESTIONS.length - 1) {
        state.index += 1;
        renderQuestion();
      } else {
        renderResult();
      }
    });

    el.back.addEventListener("click", function () {
      if (el.next.dataset.mode === "share") { restart(); return; }
      if (state.index > 0) {
        state.index -= 1;
        renderQuestion();
      }
    });

    renderQuestion();
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(init);
})();
