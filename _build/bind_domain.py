#!/usr/bin/env python3
"""Bind custom domains to a Cloudflare Pages project.

Wrangler has no CLI command for Pages custom domains, so this calls the
Cloudflare API directly using the OAuth token stored by `wrangler login`.

Usage:
    python _build/bind_domain.py [domain ...]

Defaults to confusedlife.online and www.confusedlife.online.
"""

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ACCOUNT_ID = "b662defacdf7b1d37cfb8c8b86f6cd00"
PROJECT = "confusedlife"
API = "https://api.cloudflare.com/client/v4"

# wrangler stores credentials here on Windows
CONFIG = Path.home() / "AppData" / "Roaming" / "xdg.config" / ".wrangler" / "config" / "default.toml"


def load_token() -> str:
    if not CONFIG.exists():
        sys.exit(f"wrangler config not found at {CONFIG}\nRun: npx wrangler@latest login")
    text = CONFIG.read_text(encoding="utf-8")
    match = re.search(r'^\s*oauth_token\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not match:
        sys.exit("No oauth_token in wrangler config — run `npx wrangler@latest login` first.")
    return match.group(1)


def request(method: str, path: str, token: str, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return json.loads(body) if body.strip().startswith("{") else {"success": False, "errors": [{"message": body}]}


def main():
    domains = sys.argv[1:] or ["confusedlife.online", "www.confusedlife.online"]
    token = load_token()

    for domain in domains:
        print(f"\n→ adding {domain} …")
        result = request(
            "POST",
            f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/domains",
            token,
            {"name": domain},
        )
        if result.get("success"):
            info = result.get("result", {})
            print(f"  ✓ {info.get('name', domain)}  status={info.get('status', '?')}"
                  f"  verification={info.get('validation_data', {}).get('status', 'n/a')}")
        else:
            errs = result.get("errors") or []
            for e in errs:
                print(f"  ✗ [{e.get('code')}] {e.get('message')}")

    print("\nCurrent domains:")
    listed = request("GET", f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/domains", token)
    for d in listed.get("result", []):
        print(f"  • {d.get('name')}  ({d.get('status')})")


if __name__ == "__main__":
    main()
