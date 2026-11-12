#!/usr/bin/env python3
"""Example transform: data/raw -> data/processed.

Generic starter. Offline-safe: if there is no raw input, writes/keeps an
empty summary and exits 0.

---------------------------------------------------------------------------
CUSTOMISE PER INSTANCE (hook)
---------------------------------------------------------------------------
Edit `customise_row()` and/or `transform_source()` below for your mandate's
schemas. Keep outputs plain CSV or JSON under data/processed/.
---------------------------------------------------------------------------

Usage:
  python scripts/transform.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def derive_input_fresh_at(root: Path, source_ids: list[str]) -> str | None:
    """Oldest successful collection time among contributing sources.

    Re-running transform on cached raw snapshots must not look "fresh". Prefer
    `data/fetch_status.json` last_success values; fall back to raw file mtimes.
    """
    times: list[datetime] = []
    status_path = root / "data" / "fetch_status.json"
    status_sources: dict[str, Any] = {}
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            status_sources = status.get("sources") or {}
        except json.JSONDecodeError:
            status_sources = {}

    ids = source_ids or list(status_sources.keys())
    for sid in ids:
        entry = status_sources.get(sid) or {}
        parsed = _parse_iso(entry["last_success"]) if entry.get("last_success") else None
        if parsed:
            times.append(parsed)
            continue
        source_dir = root / "data" / "raw" / sid
        if not source_dir.is_dir():
            continue
        candidates = list(source_dir.glob("latest.*")) + list(source_dir.glob("*"))
        files = [p for p in candidates if p.is_file()]
        if not files:
            continue
        newest = max(files, key=lambda p: p.stat().st_mtime)
        times.append(datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc))

    if not times:
        return None
    oldest = min(times)
    return oldest.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def customise_row(source_id: str, row: dict[str, Any]) -> dict[str, Any] | None:
    """CUSTOMISE PER INSTANCE: map a raw record to a processed row, or None to drop.

    Default: keep a shallow JSON object as a single 'payload' column plus source id.
    """
    return {
        "source_id": source_id,
        "payload": json.dumps(row, ensure_ascii=False) if not isinstance(row, str) else row,
    }


def load_latest_raw(source_dir: Path) -> tuple[str, Any] | None:
    for name in ("latest.json", "latest.csv"):
        path = source_dir / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if name.endswith(".json"):
                return "json", json.loads(text)
            return "csv", text
    # Fall back to newest timestamped file
    files = sorted(source_dir.glob("*.json")) + sorted(source_dir.glob("*.csv"))
    if not files:
        return None
    path = files[-1]
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return "json", json.loads(text)
    return "csv", text


def iter_records(fmt: str, payload: Any) -> list[Any]:
    if fmt == "json":
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("data", "results", "items", "records"):
                if isinstance(payload.get(key), list):
                    return payload[key]
            return [payload]
        return [{"value": payload}]
    # csv
    reader = csv.DictReader(payload.splitlines())
    return list(reader)


def world_bank_rows(payload: Any) -> list[Any] | None:
    """Detect World Bank API shape: [meta, [rows...]]."""
    if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[1], list):
        return payload[1]
    return None


def transform_source(source_id: str, source_dir: Path) -> list[dict[str, Any]]:
    loaded = load_latest_raw(source_dir)
    if not loaded:
        return []
    fmt, payload = loaded
    wb = world_bank_rows(payload) if fmt == "json" else None
    if wb is not None:
        records = wb
    else:
        records = iter_records(fmt, payload)
    out: list[dict[str, Any]] = []
    for rec in records:
        if isinstance(rec, dict):
            row = customise_row(source_id, rec)
        else:
            row = customise_row(source_id, {"value": rec})
        if row:
            out.append(row)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transform raw snapshots to data/processed/")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    root = args.root.resolve()
    raw_root = root / "data" / "raw"
    processed = root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    if raw_root.exists():
        for source_dir in sorted(p for p in raw_root.iterdir() if p.is_dir()):
            rows = transform_source(source_dir.name, source_dir)
            all_rows.extend(rows)
            out_json = processed / f"{source_dir.name}.json"
            out_json.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    source_ids = sorted({r.get("source_id") for r in all_rows if r.get("source_id")})
    summary = {
        "updated_at": utc_now(),  # when this transform ran (not evidence of fresh inputs)
        "input_fresh_at": derive_input_fresh_at(root, source_ids),
        "row_count": len(all_rows),
        "sources": source_ids,
    }
    (processed / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Also a flat CSV of payloads for spreadsheet-friendly instances
    csv_path = processed / "all_rows.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source_id", "payload"])
        writer.writeheader()
        for row in all_rows:
            writer.writerow({"source_id": row.get("source_id", ""), "payload": row.get("payload", "")})

    print(f"Wrote {len(all_rows)} rows -> {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
