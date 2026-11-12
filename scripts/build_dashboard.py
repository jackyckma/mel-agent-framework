#!/usr/bin/env python3
"""Build docs/data/*.json from data/processed/ for the static dashboard.

Offline-safe: always ensures docs/data/dashboard.json exists (may be empty
series) so Pages renders without network.

Freshness uses collection time (`input_fresh_at` from transform / fetch_status),
not transform clock time, so reprocessing cached snapshots cannot look fresh.
The browser also recomputes staleness on load (see docs/dashboard.js).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_summary(processed: Path) -> dict[str, Any]:
    path = processed / "summary.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"updated_at": None, "input_fresh_at": None, "row_count": 0, "sources": []}


def load_fetch_status(root: Path) -> dict[str, Any]:
    path = root / "data" / "fetch_status.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def build_series(processed: Path) -> list[dict[str, Any]]:
    """Simple series: row counts per source file."""
    series = []
    if not processed.exists():
        return series
    for path in sorted(processed.glob("*.json")):
        if path.name == "summary.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        count = len(data) if isinstance(data, list) else 1
        series.append({"label": path.stem, "value": count})
    return series


def resolve_input_fresh_at(summary: dict[str, Any], fetch_status: dict[str, Any]) -> str | None:
    if summary.get("input_fresh_at"):
        return summary["input_fresh_at"]
    # Fall back: oldest last_success among sources named in the summary.
    # Do NOT use transform clock (`updated_at`) — that would fake freshness.
    times: list[str] = []
    sources = fetch_status.get("sources") or {}
    wanted = summary.get("sources") or list(sources.keys())
    for sid in wanted:
        entry = sources.get(sid) or {}
        if entry.get("last_success"):
            times.append(entry["last_success"])
    if times:
        return min(times)
    return None


def is_stale(stamp: str | None, stale_hours: float) -> bool:
    if not stamp:
        return True
    try:
        then = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - then.astimezone(timezone.utc)).total_seconds() / 3600.0
        return age_h > stale_hours
    except (TypeError, ValueError):
        return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build dashboard JSON under docs/data/")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=48.0,
        help="Mark dashboard stale if input freshness older than this many hours",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    processed = root / "data" / "processed"
    out_dir = root / "docs" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = load_summary(processed)
    fetch_status = load_fetch_status(root)
    series = build_series(processed)
    input_fresh_at = resolve_input_fresh_at(summary, fetch_status)
    row_count = int(summary.get("row_count") or 0)
    # last_updated reflects observation freshness, not transform/build clock.
    # Empty / never-collected instances stay null + stale (honest "no data yet").
    if input_fresh_at:
        last_updated = input_fresh_at
        built_at = utc_now()
        stale = is_stale(input_fresh_at, args.stale_hours)
    else:
        last_updated = None
        built_at = None if row_count == 0 else utc_now()
        stale = True

    dashboard = {
        "title": "MEL dashboard",
        "last_updated": last_updated,
        "built_at": built_at,
        "input_fresh_at": input_fresh_at,
        "stale": stale,
        "stale_after_hours": args.stale_hours,
        "summary": {
            "row_count": row_count,
            "sources": summary.get("sources", []),
        },
        "sections": [
            {
                "id": "overview",
                "title": "Overview",
                "body": "Placeholder section — Curator configures titles and copy per instance.",
            }
        ],
        "charts": [
            {
                "id": "rows-by-source",
                "title": "Processed rows by source",
                "type": "bar",
                "labels": [s["label"] for s in series],
                "values": [s["value"] for s in series],
            }
        ],
    }

    out_path = out_dir / "dashboard.json"
    out_path.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
