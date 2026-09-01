#!/usr/bin/env python3
"""Bind custom domains to a Cloudflare Pages project and provision their DNS.

Wrangler has no CLI command for Pages custom domains, and the OAuth token it
stores only carries `zone:read` — so it can bind a domain but cannot create the
CNAME records the domain needs to validate. Supply a token with DNS:Edit
(e.g. via CLOUDFLARE_API_TOKEN) and this script does both halves.

Usage:
    CLOUDFLARE_API_TOKEN=<token> python _build/bind_domain.py
    python _build/bind_domain.py --skip-dns          # bind only
    python _build/bind_domain.py example.com         # specific domains
"""

import argparse
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
PAGES_TARGET = "confusedlife.pages.dev"
API = "https://api.cloudflare.com/client/v4"

WRANGLER_CONFIG = (
    Path.home() / "AppData" / "Roaming" / "xdg.config" / ".wrangler" / "config" / "default.toml"
)


def load_tokens():
    """Return (api_token, oauth_token). Either may be None."""
    api = os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_API_TOKEN")
    oauth = None
    if WRANGLER_CONFIG.exists():
        m = re.search(
            r'^\s*oauth_token\s*=\s*["\']([^"\']+)["\']',
            WRANGLER_CONFIG.read_text(encoding="utf-8"),
            re.M,
        )
        oauth = m.group(1) if m else None
    if not api and not oauth:
        sys.exit(
            "No credentials found.\n"
            "  export CLOUDFLARE_API_TOKEN=<token with Zone:DNS:Edit>\n"
            "  or run: npx wrangler@latest login"
        )
    return api, oauth


def call(method, path, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return (
            json.loads(body)
            if body.strip().startswith("{")
            else {"success": False, "errors": [{"code": e.code, "message": body[:200]}]}
        )


def errs(result):
    return "; ".join(f"[{e.get('code')}] {e.get('message')}" for e in result.get("errors", []))


def bind(domains, token):
    for domain in domains:
        res = call(
            "POST",
            f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/domains",
            token,
            {"name": domain},
        )
        if res.get("success"):
            print(f"  bound   {domain}")
        elif any(e.get("code") == 1047 for e in res.get("errors", [])):
            print(f"  already  {domain} (already bound)")
        else:
            print(f"  FAILED   {domain}: {errs(res)}")


def zone_id(domain, token):
    """Find the zone id for the registrable domain (handles www. prefixes)."""
    parts = domain.split(".")
    for candidate in (".".join(parts[i:]) for i in range(len(parts) - 1)):
        res = call("GET", f"/zones?name={candidate}", token)
        if res.get("success") and res["result"]:
            return res["result"][0]["id"], res["result"][0]["name"]
    return None, None


def provision_dns(domains, token, zone):
    zid, zname = zone
    print(f"\nDNS records in zone {zname}:")
    existing = call("GET", f"/zones/{zid}/dns_records?per_page=100", token)
    if not existing.get("success"):
        print(f"  cannot list records: {errs(existing)}")
        return
    have = {(r["type"], r["name"].lower()) for r in existing.get("result", [])}

    for domain in domains:
        if ("CNAME", domain.lower()) in have:
            print(f"  exists   CNAME {domain} -> {PAGES_TARGET}")
            continue
        res = call(
            "POST",
            f"/zones/{zid}/dns_records",
            token,
            {
                "type": "CNAME",
                "name": domain,
                "content": PAGES_TARGET,
                "proxied": True,
                "ttl": 1,  # auto
            },
        )
        if res.get("success"):
            print(f"  created  CNAME {domain} -> {PAGES_TARGET}  (proxied)")
        else:
            print(f"  FAILED   {domain}: {errs(res)}")


def status(token):
    res = call("GET", f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT}/domains", token)
    print("\nPages domains:")
    for d in res.get("result", []):
        v = d.get("validation_data") or {}
        print(f"  {d['name']:28} {d.get('status'):12} cert={v.get('status', 'n/a')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domains", nargs="*",
                    default=["confusedlife.online", "www.confusedlife.online"])
    ap.add_argument("--skip-dns", action="store_true", help="bind domains only")
    args = ap.parse_args()

    api, oauth = load_tokens()
    # DNS writes need the API token; binding works with either.
    dns_token = api or oauth
    bind_token = oauth or api

    print(f"Binding {', '.join(args.domains)} to '{PROJECT}' …")
    bind(args.domains, bind_token)

    if not args.skip_dns:
        zone = zone_id(args.domains[0], dns_token)
        if not zone[0]:
            print("\nZone not found — is the domain in this Cloudflare account?")
        else:
            provision_dns(args.domains, dns_token, zone)

    status(bind_token)


if __name__ == "__main__":
    main()
