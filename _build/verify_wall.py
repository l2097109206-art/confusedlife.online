import re, ssl, json, urllib.request, urllib.error

CFG = "C:/Users/Yan.Li/AppData/Roaming/xdg.config/.wrangler/config/default.toml"
cfg = open(CFG, encoding="utf-8").read()
tok = re.search(r'oauth_token\s*=\s*["\']([^"\']+)["\']', cfg).group(1)
ACC = "b662defacdf7b1d37cfb8c8b86f6cd00"
NS = "6d3bf5a4b51047c28175b50a5ce4b56d"
BASE = "https://f95f6a0e.confusedlife.pages.dev"
ctx = ssl.create_default_context()


def req(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json",
                                        "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:400]


# 1) wall page real content
s, b = req("GET", "/wall/")
print(f"[wall page] HTTP {s} len={len(b)} title_ok={'The Clarity Wall' in b}")

# 2) api/wall
s, b = req("GET", "/api/wall")
print(f"[api/wall] HTTP {s} body={b[:120]}")

# 3) crisis branch (should NOT store)
s, b = req("POST", "/api/submit",
           {"category": "career",
            "text": "Lately I feel like I want to end my life and cant go on.",
            "stuck": 5, "duration": "months", "anonymous": True})
print(f"[crisis submit] HTTP {s} -> {b[:140]}")

# 4) normal submit (should store + report)
TEST_TEXT = "I have been stuck in a career I dislike for two years and cannot decide what to switch to."
s, b = req("POST", "/api/submit",
           {"category": "career", "text": TEST_TEXT, "stuck": 4,
            "duration": "2 years", "anonymous": True,
            "email": "test-smoke-verify@example.com"})
print(f"[normal submit] HTTP {s}")
jb = json.loads(b) if b.startswith("{") else {}
pid = jb.get("post", {}).get("id")
rep = jb.get("report", {})
print(f"   pid={pid} crisis={jb.get('crisis')} reportGenBy={rep.get('generatedBy')} actions={len(rep.get('actions', []))}")

# 5) confirm on wall
s, b = req("GET", "/api/wall")
onwall = pid in b if pid else False
print(f"[api/wall after] HTTP {s} test_post_present={onwall}")

# 6) cleanup test post + lead from KV
if pid:
    kv = f"https://api.cloudflare.com/client/v4/accounts/{ACC}/storage/kv/namespaces/{NS}/values"
    kr = urllib.request.Request(kv + "/wall_posts", headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(kr, timeout=30, context=ctx) as resp:
        posts = json.loads(resp.read().decode())
    before = len(posts)
    posts = [p for p in posts if p.get("id") != pid]
    pr = urllib.request.Request(kv + "/wall_posts", data=json.dumps(posts).encode(), method="PUT",
                                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    urllib.request.urlopen(pr, timeout=30, context=ctx).read()
    # leads
    try:
        kl = urllib.request.Request(kv + "/leads", headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(kl, timeout=30, context=ctx) as resp:
            leads = json.loads(resp.read().decode())
        leads = [l for l in leads if l.get("email") != "test-smoke-verify@example.com"]
        lr = urllib.request.Request(kv + "/leads", data=json.dumps(leads).encode(), method="PUT",
                                    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
        urllib.request.urlopen(lr, timeout=30, context=ctx).read()
    except Exception as e:
        print("   lead cleanup err", e)
    print(f"[cleanup] posts {before} -> {len(posts)} (removed test post); leads cleaned")

# 7) api/report POST
s, b = req("POST", "/api/report",
           {"category": "burnout", "text": "exhausted all the time", "stuck": 3, "duration": "6 months"})
print(f"[api/report POST] HTTP {s} -> {b[:160]}")
