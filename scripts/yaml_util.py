"""Minimal YAML subset loader for sources.yml (stdlib only).

Supports a document shaped like:

    sources:
      - id: foo
        name: "Bar"
        url: "https://..."
        format: json
        enabled: false
        example: true
        notes: "..."

Does not implement full YAML. Prefer this over adding a PyYAML dependency
so agent runs and Actions stay simple. For richer config, switch the
instance to JSON and point fetch.py at it (same schema as a list under
key \"sources\").
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_sources_config(path: Path) -> dict[str, Any]:
    """Load sources list from .yml/.yaml (subset) or .json."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
    elif suffix in {".yml", ".yaml"}:
        data = load_simple_sources_yaml(text)
    else:
        raise ValueError(f"Unsupported sources config type: {path}")
    if not isinstance(data, dict) or "sources" not in data:
        raise ValueError(f"{path} must contain a top-level 'sources' list")
    if not isinstance(data["sources"], list):
        raise ValueError("'sources' must be a list")
    return data


def load_simple_sources_yaml(text: str) -> dict[str, Any]:
    """Parse the restricted sources.yml shape used by this framework."""
    lines = text.splitlines()
    sources: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_sources = False

    for raw in lines:
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^sources:\s*$", line):
            in_sources = True
            continue
        if not in_sources:
            continue
        m_item = re.match(r"^\s*-\s+id:\s*(.+)$", line)
        if m_item:
            if current:
                sources.append(current)
            current = {"id": _scalar(m_item.group(1))}
            continue
        m_key = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m_key and current is not None:
            key, val = m_key.group(1), m_key.group(2)
            if key == "id":
                current["id"] = _scalar(val)
            else:
                current[key] = _scalar(val)
            continue
        # Ignore unexpected lines inside sources block rather than failing hard.
    if current:
        sources.append(current)
    return {"sources": sources}


def _scalar(raw: str) -> Any:
    s = raw.strip()
    if s in {"true", "True"}:
        return True
    if s in {"false", "False"}:
        return False
    if s in {"null", "Null", "~", ""}:
        return None
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s
