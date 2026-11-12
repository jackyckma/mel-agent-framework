# Tests (framework CI)

Run from the **repo root** (instance skeleton):

```bash
pip install -r requirements.txt
python -m pytest framework/tests/ -q
```

Also:

```bash
python scripts/validate_repo.py
```

These tests run in GitHub Actions only when `github.repository == 'jackyckma/mel-agent-framework'` so instance repos created from the template are not spammed.
