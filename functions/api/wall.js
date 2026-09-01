import { loadPosts } from "../_lib.js";

export async function onRequestGet({ env }) {
  const posts = await loadPosts(env);
  return Response.json({ posts });
}
