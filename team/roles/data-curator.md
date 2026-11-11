# Instance role: Data Curator & Dashboard Producer

Follow `team/roles/_base/data-curator.md`, plus:

## Activation

- [ ] Active  
- [ ] Combined with Dashboard Analyst (if yes, also follow `_base/dashboard-analyst.md`; slug `data-curator`)

## Domain specifics

| Slot | Value |
|------|-------|
| Cadence | {{CADENCE_CURATOR}} |
| Metrics & transforms | _fill — customise `scripts/transform.py` hook_ |
| Dashboard sections | _fill_ |
| Stale-after threshold | _default: 2× collector cadence_ |
