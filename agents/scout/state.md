# State: scout

| Field | Value |
|-------|-------|
| Role docs last read | `team/roles/_base/scout.md`, `team/roles/scout.md` |
| Last run (UTC) | never |
| Current assignments | none |
| Open items | — |
| Known issues | — |
| Next planned actions | Complete instantiation; await first scheduled run |

## duties

Machine-readable block for `scripts/wake_check.py`. Update `last_done` (UTC ISO-8601) when a duty completes. Wake interval ≠ duty cadence.

```yaml
duties:
  - name: signal-scan
    cadence_hours: 168
    last_done: null
```
