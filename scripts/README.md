# Scripts

Python 3, **standard library preferred**. Root `requirements.txt` lists pytest for framework tests only.

| Script | Job |
|--------|-----|
| `fetch.py` | Read `data/sources.yml`, fetch enabled HTTP JSON/CSV sources, write `data/raw/<id>/`, update `data/fetch_status.json` (usually run by Actions) |
| `transform.py` | Example raw → `data/processed/`; customise `customise_row()` per instance |
| `build_dashboard.py` | Build `docs/data/dashboard.json` from processed data (uses collection freshness) |
| `validate_repo.py` | Structure + board frontmatter/slug checks (offline) |
| `yaml_util.py` | Minimal YAML subset loader for `sources.yml` (avoids PyYAML) |

## Sources config

`data/sources.yml` uses a **restricted YAML subset**. Same schema can live in JSON — pass `--config` to `fetch.py`.

## Run locally

From the **repo root**:

```bash
python scripts/validate_repo.py
python scripts/transform.py
python scripts/build_dashboard.py
# network optional:
python scripts/fetch.py
```

Fetch does **not** hard-fail offline unless you pass `--strict`. Prefer the scheduled Action for mechanical HTTP; agents review results.
