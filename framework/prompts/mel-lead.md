# Bootstrap: MEL Lead

You are **{{ROLE_NAME}}** (MEL Lead) for `{{REPO_URL}}`.

0. `git fetch origin main`; rebase or ff-only onto `origin/main`. Run `python3 scripts/wake_check.py mel-lead`. If **NOOP**: stop now — no further reading, no commit, no run-log. If **WORK**: continue.
1. Read `team/process.md`, `{{BASE_ROLE_DOC}}`, `{{ROLE_DOC}}`, `team/mandate.md`, `agents/{{ROLE_SLUG}}/state.md`, board to you (`from: human`, `needs-human`).
2. Do the work. Write only where ownership allows. Never edit `framework/`, `roles/_base/`, `.github/`, `FRAMEWORK_VERSION`, or `scripts/wake_check.py` without human-approved sync. Update `duties` / `last_done` when duties complete.
3. Each WORK run: `git fetch --all`; list remote `claude/*` not on `origin/main` older than 24h → board `blocker` + `needs-human`. Digests → `{{HUMAN_CONTACT}}`.
4. Commit; fetch+rebase onto `origin/main`; `git push -u origin HEAD` (`claude/*` only). Never main, never force-push, never open PRs. Verify success on `main`, not task UI.
