# State: mel-lead

| Field | Value |
|-------|-------|
| Role docs last read | `team/roles/_base/mel-lead.md`, `team/roles/mel-lead.md` |
| Last run (UTC) | never |
| Current assignments | none |
| Open items | — |
| Known issues | — |
| Next planned actions | Complete instantiation; await first scheduled run |

## duties

Machine-readable block for `scripts/wake_check.py`. Update `last_done` (UTC ISO-8601) when a duty completes. Wake interval ≠ duty cadence.

```yaml
duties:
  - name: daily-digest
    cadence_hours: 24
    last_done: null
  - name: stuck-branch-scan
    cadence_hours: 3
    last_done: null
```
