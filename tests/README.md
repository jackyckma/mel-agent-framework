# Tests

```bash
pip install -r template/requirements.txt
python -m pytest tests/ -q
# or:
python -m unittest tests.test_validate_repo -v
```

Also:

```bash
python template/scripts/validate_repo.py --root template
```
