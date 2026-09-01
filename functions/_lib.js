// Shared helpers for The Clarity Wall (Cloudflare Pages Functions)
// No build step — these run as ES modules on Cloudflare's edge.

export const CATEGORIES = {
  career:      { label: "Career",             tag: "#CareerCrossroads" },
  relationship: { label: "Relationship",       tag: "#RelationshipFog" },
  burnout:     { label: "Mind & Burnout",      tag: "#BurnoutBrain" },
  identity:    { label: "Identity / Direction", tag: "#QuarterLifeCrisis" },
};

// Self-harm / crisis terms. If matched we NEVER generate a report — we show crisis resources instead.
const CRISIS_TERMS = [
  "kill myself", "suicide", "end my life", "ending my life", "don't want to live",
  "dont want to live", "want to die", "want to be dead", "hurt myself", "self harm",
  "self-harm", "cut myself", "cutting myself", "ending it all", "better off dead",
  "no reason to live", "can't go on", "cant go on", "take my life", "end it all",
];

export function detectCrisis(text = "") {
  const t = " " + String(text).toLowerCase() + " ";
  return CRISIS_TERMS.some((term) => t.includes(term));
}

export function cleanText(s, max = 600) {
  return String(s || "").trim().replace(/\s+/g, " ").slice(0, max);
}

export function isValidCategory(c) {
  return Object.prototype.hasOwnProperty.call(CATEGORIES, c);
}

export function isEmail(s) {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(s || "").trim());
}

export function newId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

// ---- KV storage (graceful: works without binding, just won't persist) ----
const POSTS_KEY = "wall_posts";
const LEADS_KEY = "leads";

export async function loadPosts(env) {
  if (!env?.WALL) return [];
  try {
    const raw = await env.WALL.get(POSTS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function savePosts(env, posts) {
  if (!env?.WALL) return false;
  try {
    await env.WALL.put(POSTS_KEY, JSON.stringify(posts.slice(0, 300)));
    return true;
  } catch {
    return false;
  }
}

export async function saveLead(env, email) {
  if (!env?.WALL) return false;
  try {
    const raw = (await env.WALL.get(LEADS_KEY)) || "[]";
    const leads = JSON.parse(raw);
    if (!leads.find((l) => l.email === email)) leads.push({ email, ts: Date.now() });
    await env.WALL.put(LEADS_KEY, JSON.stringify(leads.slice(-2000)));
    return true;
  } catch {
    return false;
  }
}

// ---- Mock Reflection Report (used when no OPENAI_API_KEY is set) ----
export function mockReport({ category, stuck, duration, text }) {
  const cat = CATEGORIES[category]?.label || "Life";
  const dur = duration || "a while";
  const rootCause =
    `From what you shared, the confusion reads less like a personal failing and more like a gap ` +
    `between the life you've been expected to build and the one you actually want. At a stuck-level ` +
    `of ${stuck}/5, with ${dur} of this weighing on you, the most likely driver is decision paralysis ` +
    `fed by too many options and too little external structure — not a lack of ability or worth.`;
  const mindset =
    `Use the Stoic Dichotomy of Control. Split everything on your mind into two columns: ` +
    `"things I control" (my next small step, who I talk to, what I stop agreeing to) and ` +
    `"things I don't" (other people's approval, the economy, how fast clarity arrives). ` +
    `Most of the weight sits in the second column — and naming that is what lightens it.`;
  const actions = [
    `Make the single smallest avoided decision within 48 hours — even if it's reversible. Momentum beats certainty.`,
    `Do a 20-minute values audit: list 5 moments this year you felt most like yourself. The pattern between them is your compass, not the job title.`,
    `Tell one trusted person "I'm figuring some things out" this week. Saying it out loud breaks the isolation that makes confusion feel like a flaw.`,
  ];
  const resources = [
    { title: "Feeling Lost in Life — the full guide", url: "https://confusedlife.online/guides/feeling-lost-in-life/" },
    { title: "Why Am I So Confused About Life?", url: "https://confusedlife.online/guides/why-am-i-so-confused-about-life/" },
    { title: "The Clarity Quiz (2-minute self-check)", url: "https://confusedlife.online/tools/clarity-quiz/" },
  ];
  return { rootCause, mindset, actions, resources, generatedBy: "template" };
}

// ---- Real AI report (used when OPENAI_API_KEY is present) ----
export async function aiReport(env, input) {
  const sys =
    `You are a thoughtful, non-clinical reflection coach for a website about feeling lost in life. ` +
    `You NEVER diagnose and NEVER give medical, psychological or clinical advice. Given a person's ` +
    `category, stuck level, how long they've felt this way, and a short description, return ONLY valid ` +
    `JSON with this exact shape:\n` +
    `{"rootCause":"...","mindset":"...","actions":["...","...","..."],"resources":[{"title":"...","url":"..."}]}\n` +
    `Rules: rootCause <= 90 words, name the likely deeper cause. mindset <= 80 words, teach ONE classic ` +
    `model (Eisenhower Matrix, First Principles, Stoic Dichotomy of Control, or Values Audit). actions = ` +
    `exactly 3 concrete micro-actions doable in 48h. resources = exactly 3 internal links from ` +
    `confusedlife.online (use /guides/feeling-lost-in-life/, /guides/why-am-i-so-confused-about-life/, ` +
    `/tools/clarity-quiz/). Tone: warm, plain-English, no toxic positivity.`;
  const user =
    `Category: ${input.category}\nStuck level (1-5): ${input.stuck}\nDuration: ${input.duration}\n` +
    `What's weighing on them: ${input.text}`;
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${env.OPENAI_API_KEY}` },
    body: JSON.stringify({
      model: env.OPENAI_MODEL || "gpt-4o-mini",
      messages: [
        { role: "system", content: sys },
        { role: "user", content: user },
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
    }),
  });
  if (!r.ok) throw new Error("openai " + r.status);
  const j = await r.json();
  const parsed = JSON.parse(j.choices[0].message.content);
  return { ...parsed, generatedBy: "ai" };
}

// ---- Moderation (OpenAI Moderation API; skipped if no key) ----
export async function moderate(env, text) {
  if (!env?.OPENAI_API_KEY) return { flagged: false };
  try {
    const r = await fetch("https://api.openai.com/v1/moderations", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${env.OPENAI_API_KEY}` },
      body: JSON.stringify({ input: text }),
    });
    if (!r.ok) return { flagged: false };
    const j = await r.json();
    const f = j.results?.[0];
    return { flagged: !!f?.flagged, categories: f?.category_scores || {} };
  } catch {
    return { flagged: false };
  }
}
