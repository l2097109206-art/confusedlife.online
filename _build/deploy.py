"""One-shot deploy for The Clarity Wall.

Creates the KV namespace (using the wrangler OAuth token we already have),
writes wrangler.toml with the real binding id, rebuilds the site, refreshes
_deploy, and publishes to Cloudflare Pages. Run from the repo root:

    python _build/deploy.py
"""
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACC = "b662defacdf7b1d37cfb8c8b86f6cd00"
NODE = r"C:\Users\Yan.Li\.workbuddy\binaries\node\versions\22.22.2"
TOKEN_RE = re.compile(r'oauth_token\s*=\s*["\']([^"\']+)["\']')

CFG = Path.home() / "AppData" / "Roaming" / "xdg.config" / ".wrangler" / "config" / "default.toml"


def api(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + path,
        data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode())


def ensure_kv():
    existing = api("GET", f"/accounts/{ACC}/storage/kv/namespaces").get("result", [])
    for n in existing:
        if n["title"] == "confusedlife-wall":
            print("KV exists:", n["id"])
            return n["id"]
    created = api("POST", f"/accounts/{ACC}/storage/kv/namespaces", {"title": "confusedlife-wall"})
    print("KV created:", created["result"]["id"])
    return created["result"]["id"]


def main():
    global TOKEN
    TOKEN = TOKEN_RE.search(CFG.read_text(encoding="utf-8")).group(1)

    ns_id = ensure_kv()
    (ROOT / "wrangler.toml").write_text(
        f'name = "confusedlife"\n'
        f'compatibility_date = "2024-09-01"\n'
        f'pages_build_output_dir = "./_deploy"\n'
        f"\n"
        f"[[kv_namespaces]]\n"
        f'binding = "WALL"\n'
        f'id = "{ns_id}"\n',
        encoding="utf-8",
    )
    print("wrote wrangler.toml")

    sys.path.insert(0, str(ROOT / "_build"))
    import build
    build.main()

    deploy = ROOT / "_deploy"
    deploy.mkdir(exist_ok=True)
    for p in ["index.html", "404.html", "robots.txt", "sitemap.xml", "_headers"]:
        shutil.copy2(ROOT / p, deploy / p)
    for d in ["assets", "guides", "tools", "quotes", "topics", "about",
              "contact", "disclaimer", "editorial-policy", "privacy-policy", "terms", "wall"]:
        src = ROOT / d
        if src.exists():
            dst = deploy / d
            # dirs_exist_ok=True in-place refresh; avoids rmtree which the
            # Windows sandbox safe-delete shim blocks (recycle bin unavailable).
            shutil.copytree(src, dst, dirs_exist_ok=True)
    print("refreshed _deploy")

    env = dict(os.environ)
    env["PATH"] = NODE + ";" + env.get("PATH", "")
    r = subprocess.run(
        ["npx", "wrangler@latest", "pages", "deploy", "--project-name=confusedlife", "--branch=main"],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )
    print(r.stdout)
    if r.returncode:
        print("STDERR:", r.stderr)
        sys.exit(r.returncode)
    print("DEPLOY OK")


if __name__ == "__main__":
    main()
