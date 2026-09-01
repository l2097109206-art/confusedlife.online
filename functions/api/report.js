import { isValidCategory, mockReport, aiReport, cleanText } from "../_lib.js";

export async function onRequestPost({ request, env }) {
  const b = await request.json().catch(() => ({}));
  if (!isValidCategory(b.category)) {
    return Response.json({ ok: false, error: "invalid category" }, { status: 400 });
  }
  const text = cleanText(b.text || "", 1200);
  try {
    const report = env?.OPENAI_API_KEY
      ? await aiReport(env, { category: b.category, text, stuck: b.stuck, duration: b.duration })
      : mockReport({ category: b.category, stuck: b.stuck, duration: b.duration, text });
    return Response.json({ ok: true, report });
  } catch {
    return Response.json({
      ok: true,
      report: mockReport({ category: b.category, stuck: b.stuck, duration: b.duration, text }),
    });
  }
}
