# Changelog

All notable changes to the MEL agent-team framework are recorded here.

Format: Keep a Changelog. Versioning: SemVer.

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
