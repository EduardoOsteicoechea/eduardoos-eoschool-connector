#!/usr/bin/env python3
"""Eduardo OS eoschool thin connector — API key + docs + generic authenticated requests.

Agents must call `docs` first and craft further calls from the live catalog
(routes + payloadSchema.homescool). Generate HTML only with skill/eoschool guidelines.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parent


def load_env() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def cfg() -> dict[str, str]:
    load_env()
    base = os.environ.get("EDUARDOOS_BASE_URL", "https://eduardoos.com").rstrip("/")
    return {
        "base": base,
        "key": os.environ.get("EDUARDOOS_API_KEY", "").strip(),
    }


def require_key() -> dict[str, str]:
    c = cfg()
    if not c["key"]:
        print("Missing EDUARDOOS_API_KEY in .env (required)", file=sys.stderr)
        sys.exit(2)
    return c


def request(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    auth: bool = True,
) -> Any:
    c = cfg()
    if auth:
        c = require_key()
    url = c["base"] + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method.upper())
    req.add_header("X-Correlation-ID", str(uuid4()))
    if auth:
        req.add_header("Authorization", f"Bearer {c['key']}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        retry = e.headers.get("Retry-After")
        msg = f"HTTP {e.code}: {detail}"
        if e.code == 429 and retry:
            msg += f" (Retry-After: {retry})"
        print(msg, file=sys.stderr)
        sys.exit(1)


def print_view(data: dict[str, Any]) -> None:
    view = data.get("viewUrl")
    if view:
        print(f"Ver material: {view}")


def cmd_docs(_: argparse.Namespace) -> None:
    out = request("GET", "/api/v1/docs", auth=False)
    dest = ROOT / "docs.catalog.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {dest}")
    schema = out.get("payloadSchema") or {}
    print(json.dumps({
        "version": out.get("version"),
        "title": out.get("title"),
        "agentGuidance": out.get("agentGuidance"),
        "routeCount": len(out.get("routes") or []),
        "hasHomescoolSchema": bool(isinstance(schema, dict) and schema.get("homescool")),
    }, indent=2, ensure_ascii=False))


def cmd_request(args: argparse.Namespace) -> None:
    method = args.method.upper()
    path = args.path
    body: dict[str, Any] | None = None
    if args.file:
        body = json.loads(Path(args.file).read_text(encoding="utf-8"))
    auth = path not in ("/api/v1/docs",) and not path.rstrip("/").endswith("/api/v1/docs")
    out = request(method, path, body, auth=auth)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if isinstance(out, dict):
        print_view(out)


def cmd_access(_: argparse.Namespace) -> None:
    out = request("GET", "/api/v1/homescool/access")
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_list(args: argparse.Namespace) -> None:
    path = "/api/v1/homescool/materials"
    if args.cycle:
        path += f"?cycle={args.cycle}"
    out = request("GET", path)
    for m in out.get("materials") or []:
        print(f"{m.get('id')}\tciclo{m.get('cycle')}\tS{m.get('week')}\t{m.get('subject')}\t{m.get('title')}")
    print(json.dumps({"count": len(out.get("materials") or [])}, indent=2))


def cmd_post(args: argparse.Namespace) -> None:
    raw = json.loads(Path(args.file).read_text(encoding="utf-8"))
    if "confirmOverwrite" not in raw:
        raw = {"confirmOverwrite": True, "material": raw}
    out = request("POST", "/api/v1/homescool/materials", raw)
    print(json.dumps({"id": (out.get("material") or {}).get("id"), "title": (out.get("material") or {}).get("title")}, indent=2))
    print_view(out)


def main() -> None:
    p = argparse.ArgumentParser(description="Eduardo OS eoschool thin connector (API key + docs + request)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("docs", help="GET /api/v1/docs (no key) — fetch first").set_defaults(func=cmd_docs)

    req = sub.add_parser("request", help="Generic METHOD path [--file json]")
    req.add_argument("method", help="HTTP method, e.g. GET or POST")
    req.add_argument("path", help="Absolute API path")
    req.add_argument("--file", help="JSON body file (POST)")
    req.set_defaults(func=cmd_request)

    sub.add_parser("access").set_defaults(func=cmd_access)
    lst = sub.add_parser("list")
    lst.add_argument("--cycle", type=int, choices=[1, 2, 3])
    lst.set_defaults(func=cmd_list)
    post = sub.add_parser("post")
    post.add_argument("--file", required=True, help="JSON with confirmOverwrite + material, or bare material object")
    post.set_defaults(func=cmd_post)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
