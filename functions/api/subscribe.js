import { isEmail, saveLead } from "../_lib.js";

export async function onRequestPost({ request, env }) {
  const { email } = await request.json().catch(() => ({}));
  if (!email || !isEmail(email)) return Response.json({ ok: false }, { status: 400 });
  await saveLead(env, email.trim());
  return Response.json({ ok: true });
}
