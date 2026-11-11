#!/usr/bin/env python3
"""Fetch enabled sources into data/raw/<source_id>/ and update fetch_status.json.

Offline-safe: if the network fails, records errors and exits 0 by default
so CI/templates do not hard-fail when offline. Use --strict to exit non-zero
when any enabled source fails.

Usage (from instance repo root):
  python scripts/fetch.py
  python scripts/fetch.py --config data/sources.yml
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Allow running as script from repo root
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from yaml_util import load_sources_config  # noqa: E402

DEFAULT_TIMEOUT = 60


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_status(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"updated_at": None, "sources": {}}


def save_status(path: Path, status: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def fetch_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mel-agent-framework-fetch/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — URLs from trusted sources.yml
        return resp.read()


def write_snapshot(raw_root: Path, source_id: str, fmt: str, body: bytes, stamp: str) -> Path:
    dest_dir = raw_root / source_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = "json" if fmt == "json" else "csv" if fmt == "csv" else "txt"
    # Validate payload lightly
    text = body.decode("utf-8", errors="replace")
    if fmt == "json":
        json.loads(text)  # raise if invalid
    elif fmt == "csv":
        list(csv.reader(io.StringIO(text)))
    out = dest_dir / f"{stamp}.{ext}"
    out.write_text(text, encoding="utf-8")
    latest = dest_dir / f"latest.{ext}"
    latest.write_text(text, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch MEL sources into data/raw/")
    parser.add_argument("--root", type=Path, default=Path("."), help="Instance repo root")
    parser.add_argument("--config", type=Path, default=None, help="sources.yml or .json path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any enabled fetch fails")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    config_path = (args.config or (root / "data" / "sources.yml")).resolve()
    status_path = root / "data" / "fetch_status.json"
    raw_root = root / "data" / "raw"

    if not config_path.exists():
        print(f"No sources config at {config_path}; nothing to do.", file=sys.stderr)
        return 0

    data = load_sources_config(config_path)
    status = load_status(status_path)
    status.setdefault("sources", {})
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    any_failed = False

    for src in data["sources"]:
        sid = src.get("id")
        if not sid:
            continue
        entry = status["sources"].setdefault(
            sid, {"last_success": None, "last_error": None, "last_attempt": None}
        )
        if not src.get("enabled", False):
            entry["last_attempt"] = utc_now()
            entry["skipped"] = "disabled"
            continue
        entry.pop("skipped", None)
        entry["last_attempt"] = utc_now()
        url = src.get("url")
        fmt = (src.get("format") or "json").lower()
        try:
            if not url:
                raise ValueError("missing url")
            body = fetch_url(str(url), timeout=args.timeout)
            path = write_snapshot(raw_root, str(sid), fmt, body, stamp)
            entry["last_success"] = utc_now()
            entry["last_error"] = None
            entry["last_path"] = str(path.relative_to(root))
            print(f"OK {sid} -> {entry['last_path']}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as exc:
            any_failed = True
            entry["last_error"] = f"{type(exc).__name__}: {exc}"
            print(f"FAIL {sid}: {entry['last_error']}", file=sys.stderr)

    status["updated_at"] = utc_now()
    save_status(status_path, status)

    if args.strict and any_failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
