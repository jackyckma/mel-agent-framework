# Changelog

All notable changes to the MEL agent-team framework are recorded here.

Format: Keep a Changelog. Versioning: SemVer.

## [0.2.0] — 2026-11-12

### Changed

- Run protocol: agents sync with `git fetch origin main` + rebase/ff-only, then `git push -u origin HEAD` on `claude/*` only (never push `main`, never force-push, never open PRs).
- Instantiation rewritten as an onboarding Lead chat script; human creates Scheduled Tasks in the Claude UI with Repository set at creation.
- OPERATING_GUIDE / DESIGN updated for spike findings and merge workflow.

### Added

- `.github/workflows/merge-agent-trigger.yml` — low-privilege dispatch only (`actions: write`).
- `.github/workflows/merge-agent-branches.yml` — privileged gate via `workflow_dispatch` on **main**; validates; protected-path guard; merges/sweeps `claude/*`; dispatches Pages.
- `scripts/check_protected_paths.py` (+ unit tests): blocks `.github/**`, `framework/**`, `FRAMEWORK_VERSION`, `team/roles/_base/**`, gate scripts; rename-aware.
- `team/SETUP_STATUS.md` checklist for multi-chat setup resume.
- `framework/prompts/onboarding-lead.md`.
- Lead duty: escalate remote `claude/*` branches older than 24h not on `main`.
- DESIGN section “Platform findings from the first spike” (2026-11-12).

## [0.1.0] — 2026-11-11

### Added

- Initial public GitHub **template** for MEL agent teams (root = instance skeleton; `framework/` for meta docs/prompts/tests).
- Roles, process, board, scripts, Pages dashboard, validate/fetch workflows, human inbox, Actions-as-mechanical-arm guidance.
