import { loadPosts, savePosts } from "../_lib.js";

const KINDS = ["alone", "clarity", "hug"];

export async function onRequestPost({ request, env }) {
  const { postId, kind } = await request.json().catch(() => ({}));
  if (!KINDS.includes(kind)) return Response.json({ ok: false }, { status: 400 });
  const posts = await loadPosts(env);
  const p = posts.find((x) => x.id === postId);
  if (!p) return Response.json({ ok: false, error: "not found" }, { status: 404 });
  p.reactions[kind] = (p.reactions[kind] || 0) + 1;
  await savePosts(env, posts);
  return Response.json({ ok: true, reactions: p.reactions });
}
