import { loadPosts, savePosts, cleanText, moderate } from "../_lib.js";

const TAGS = ["Been there, solved it", "Currently in the same boat", "Just here to listen"];

export async function onRequestPost({ request, env }) {
  const { postId, text, tag } = await request.json().catch(() => ({}));
  const clean = cleanText(text, 500);
  if (clean.length < 2) return Response.json({ ok: false }, { status: 400 });
  const safeTag = TAGS.includes(tag) ? tag : TAGS[1];

  const mod = await moderate(env, clean);
  if (mod.flagged) return Response.json({ ok: false, blocked: true });

  const posts = await loadPosts(env);
  const p = posts.find((x) => x.id === postId);
  if (!p) return Response.json({ ok: false, error: "not found" }, { status: 404 });
  p.comments.push({ text: clean, tag: safeTag, ts: Date.now() });
  await savePosts(env, posts);
  return Response.json({ ok: true, comments: p.comments });
}
