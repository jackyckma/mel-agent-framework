# Task registry

Map each agent role to its Claude.ai scheduled task. The interactive Lead chat
uses this table for on-demand dispatch (board message + fire the role's task).

Fill during onboarding: after each scheduled task is created, record its **name**.
When scheduled-task tools are available in chat, look up the task **id** and paste
it here. Status is Owner-maintained (`active` / `paused` / `missing`).

| Role slug | Scheduled task name | Task id (optional) | Wake interval | Status |
|-----------|---------------------|--------------------|---------------|--------|
| mel-lead | _(fill after create)_ | | 3h (suggested) | missing |
| scout | _(fill after create)_ | | 6–12h (suggested) | missing |
| data-collector | _(fill after create)_ | | 6–12h (suggested) | missing |
| data-curator | _(fill after create)_ | | 6–12h (suggested) | missing |
| dashboard-analyst | _(fill after create)_ | | 6–12h (suggested) | missing |
| narrative-designer | _(fill after create)_ | | 6–12h (suggested) | missing |
| project-change-manager | _(fill after create)_ | | 6–12h (suggested) | missing |

## Notes

- **Wake interval** ≠ **duty cadence**. Wake interval is how often the scheduled
  task fires; duty cadence lives in `agents/<slug>/state.md` under `duties:`.
- A fired task still runs `scripts/wake_check.py` first. If there is no open board
  message and no duty due, it exits **NOOP** (no commit, no run-log).
- Do not invent task ids. Prefer leaving the id blank until tools or the UI
  confirm it.
