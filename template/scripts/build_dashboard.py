#!/usr/bin/env python3
"""Build docs/data/*.json from data/processed/ for the static dashboard.

Offline-safe: always ensures docs/data/dashboard.json exists (may be empty
series) so Pages renders without network.
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
    return {"updated_at": None, "row_count": 0, "sources": []}


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build dashboard JSON under docs/data/")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=48.0,
        help="Mark dashboard stale if processed summary older than this many hours",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    processed = root / "data" / "processed"
    out_dir = root / "docs" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = load_summary(processed)
    series = build_series(processed)
    updated = summary.get("updated_at") or utc_now()
    stale = False
    try:
        # Compare age when timestamp present
        if summary.get("updated_at"):
            ts = summary["updated_at"].replace("Z", "+00:00")
            then = datetime.fromisoformat(ts)
            age_h = (datetime.now(timezone.utc) - then.astimezone(timezone.utc)).total_seconds() / 3600.0
            stale = age_h > args.stale_hours
    except (TypeError, ValueError):
        stale = True

    dashboard = {
        "title": "MEL dashboard",
        "last_updated": updated,
        "stale": stale,
        "stale_after_hours": args.stale_hours,
        "summary": {
            "row_count": summary.get("row_count", 0),
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
