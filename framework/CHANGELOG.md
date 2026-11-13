# Changelog

All notable changes to the MEL agent-team framework are recorded here.

Format: Keep a Changelog. Versioning: SemVer.

## [0.4.0] — 2026-11-13

### Added

- `scripts/wake_check.py` — cheap wake gate (WORK/NOOP) before heavy doc reads; protected like other gate scripts.
- Machine-readable `duties:` block in every `agents/*/state.md` (`name`, `cadence_hours`, `last_done`).
- `team/task-registry.md` — role → scheduled task name/id, wake interval, status (for on-demand dispatch).
- Dispatch protocol in `framework/prompts/mel-lead-chat.md` (board message + fire task; verify on main).
- `framework/tests/test_wake_check.py` — WORK/NOOP, `to: all`, closed messages, duties due/not-due, Lead stuck-branch, key-order-independent duties, combined-role board slugs.

### Changed

- All `framework/prompts/*.md` bootstraps: step 0 = wake check; NOOP stops immediately (no commit, no run-log).
- `team/process.md`: NOOP silent exit; wake interval vs duty cadence table; wake_check ownership.
- INSTANTIATE / onboarding / OPERATING_GUIDE: disable all Connectors on scheduled tasks; tight Cloud environment; record tasks in registry.
- DESIGN.md: wake gate + dispatch + connector security.
- `wake_check` duty parser accepts any YAML key order on list items; combined-role board recipients resolved from `team/roles/README.md` mapping.

## [0.3.0] — 2026-11-12

### Added

- `framework/prompts/STARTER_PROMPT.md` — copy-paste entry for a fresh Claude chat with GitHub connector.
- Actor labels **[Admin]** / **[Owner]** / **[Lead-chat]** across INSTANTIATE, onboarding-lead, and `team/SETUP_STATUS.md`.
- First-run test checklist (Run now → `claude/*` → Merge green → commit on `main` → Pages; what to do if red).
- Documented required manual Settings: Actions workflow permissions; Pages = GitHub Actions; tasks Active only after test.
- `scripts/merge_push_result.py` + regression tests for push-race handling.

### Changed

- `merge-agent-branches.yml`: wrap `git push origin HEAD:main`; on failure fetch/reset to `origin/main`, mark branch failed-retryable, continue the sweep (no whole-loop abort under `set -e`).
- Onboarding docs: chat/API tasks cannot bind Repository / cannot push; do not rely on “Allow unrestricted branch pushes” (not found in UI).

## [0.2.0] — 2026-11-12

### Changed

- Run protocol: agents sync with `git fetch origin main` + rebase/ff-only, then `git push -u origin HEAD` on `claude/*` only.
- Instantiation rewritten as an onboarding Lead chat script.
- OPERATING_GUIDE / DESIGN updated for spike findings and merge workflow.

### Added

- `merge-agent-trigger.yml` + `merge-agent-branches.yml` (trusted-main gate, sweep, Pages dispatch).
- `scripts/check_protected_paths.py` (+ tests).
- `team/SETUP_STATUS.md`, `framework/prompts/onboarding-lead.md`.
- Lead duty for stuck `claude/*` branches; DESIGN “Platform findings from the first spike”.

## [0.1.0] — 2026-11-11

### Added

- Initial public GitHub **template** for MEL agent teams (root = instance skeleton; `framework/` for meta docs/prompts/tests).
