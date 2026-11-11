# Scripts

Python 3, **standard library preferred**. `requirements.txt` lists pytest for tests only.

| Script | Job |
|--------|-----|
| `fetch.py` | Read `data/sources.yml`, fetch enabled HTTP JSON/CSV sources, write `data/raw/<id>/`, update `data/fetch_status.json` |
| `transform.py` | Example raw → `data/processed/`; customise `customise_row()` per instance |
| `build_dashboard.py` | Build `docs/data/dashboard.json` from processed data |
| `validate_repo.py` | Structure + board frontmatter checks (offline) |
| `yaml_util.py` | Minimal YAML subset loader for `sources.yml` (avoids PyYAML) |

## Sources config

`data/sources.yml` uses a **restricted YAML subset** (list of sources with simple scalars). Same schema can live in `data/sources.json` if you prefer JSON — pass `--config` to `fetch.py`.

## Run locally

From the **instance root** (contents of `template/`):

```bash
python scripts/validate_repo.py
python scripts/transform.py
python scripts/build_dashboard.py
# network optional:
python scripts/fetch.py
```

Fetch does **not** hard-fail offline unless you pass `--strict`.
