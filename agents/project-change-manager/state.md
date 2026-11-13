# State: project-change-manager

| Field | Value |
|-------|-------|
| Role docs last read | `team/roles/_base/project-change-manager.md`, `team/roles/project-change-manager.md` |
| Last run (UTC) | never |
| Current assignments | none |
| Open items | — |
| Known issues | — |
| Next planned actions | Complete instantiation; await first scheduled run |

## duties

Machine-readable block for `scripts/wake_check.py`. Update `last_done` (UTC ISO-8601) when a duty completes. Wake interval ≠ duty cadence.

```yaml
duties:
  - name: project-status-review
    cadence_hours: 24
    last_done: null
```
