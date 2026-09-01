import {
  CATEGORIES, detectCrisis, cleanText, isValidCategory, isEmail,
  loadPosts, savePosts, newId, mockReport, aiReport, moderate, saveLead,
} from "../_lib.js";

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ ok: false, error: "bad json" }, { status: 400 });
  }

  const { category, text, stuck, duration, anonymous, email } = body;
  if (!isValidCategory(category)) {
    return Response.json({ ok: false, error: "invalid category" }, { status: 400 });
  }
  const clean = cleanText(text, 1200);
  if (clean.length < 20) {
    return Response.json({ ok: false, error: "too short" }, { status: 400 });
  }

  // 1) Crisis always wins — never generate a report for self-harm content.
  if (detectCrisis(clean)) {
    return Response.json({ ok: true, crisis: true });
  }

  // 2) Moderation (skipped when no API key)
  const mod = await moderate(env, clean);
  if (mod.flagged) {
    return Response.json({
      ok: false,
      blocked: true,
      error: "This post couldn't be published. If you're in distress, please reach out to a crisis line.",
    });
  }

  // 3) Persist the post
  const id = newId();
  const post = {
    id,
    category,
    tag: CATEGORIES[category].tag,
    text: clean.slice(0, 600),
    author: anonymous ? "Anonymous" : "A visitor",
    stuck: Number(stuck) || 3,
    duration: duration || "unspecified",
    ts: Date.now(),
    reactions: { alone: 0, clarity: 0, hug: 0 },
    comments: [],
  };
  const posts = await loadPosts(env);
  posts.unshift(post);
  await savePosts(env, posts);

  // 4) Collect email lead (the growth engine)
  if (email && isEmail(email)) {
    await saveLead(env, email.trim());
  }

  // 5) Generate the Reflection Report (real if key, else template)
  let report = null;
  try {
    report = env?.OPENAI_API_KEY
      ? await aiReport(env, { category, text: clean, stuck, duration })
      : mockReport({ category, stuck, duration, text: clean });
  } catch {
    report = mockReport({ category, stuck, duration, text: clean });
  }

  return Response.json({ ok: true, post, report });
}
