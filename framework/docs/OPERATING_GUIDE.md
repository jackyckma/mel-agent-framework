# Operating guide (for the human operator)

You are the COO-side owner of a MEL agent team. You talk to **one** agent: the **MEL Lead**. Everything else happens in the GitHub repo.

## How to talk to the Lead

- Give goals, priorities, audience, and “what decision this informs.”
- Prefer short written instructions the Lead can turn into board tasks.
- Ask for a digest: what moved, what is blocked, what needs you.
- Do not try to brief every agent yourself — the Lead dispatches.

### Human inbox (board)

- Your instructions should end up as board messages with **`from: human`** (usually `to: lead`) under `team/board/`.
- Use an **interactive Lead chat** (`framework/prompts/mel-lead-chat.md`) so the Lead can file those messages and act immediately, **or** wait for the **scheduled** Lead run to pick them up.
- Digests go where `{{HUMAN_CONTACT}}` says — typically a file under `agents/mel-lead/outputs/` plus whatever notification channel you set up outside git.

## How to create a Scheduled Task (Claude UI)

Do this **after** the instance GitHub repo exists. The repository must be chosen **when the task is created**. Prefer starting from `framework/prompts/STARTER_PROMPT.md` so onboarding produces paste blocks for you.

Known click-path (labels observed 2026-11-12):

1. **New scheduled task**
2. Paste the role prompt from onboarding / `framework/prompts/<role>.md` (placeholders filled)
3. **Advanced settings → General → Repository** = your **instance** repo (the form says this makes it a “Claude Code task”)
4. Set **Trigger** / schedule as agreed
5. Permission mode **Auto** if your organisation allows it
6. Keep the task **not Active** until a **Run now** test lands a commit on **`main`** via **Merge agent branches**; then set Active

Do **not** create these via chat/tool API — those tasks have **no Repository** source, so git push is refused. A UI option **“Allow unrestricted branch pushes” was not found**; do not rely on it. If you later open a task’s edit dialog and only see **Local folder** (not Repository), we believe the type cannot be changed after creation (inferred from the UI, not officially documented). Create a **new** task with Repository set instead.

Also set on the instance repo: **Settings → Actions → General → Workflow permissions** = **Read repository contents** (read-only — do **not** grant Read and write; workflows declare their own write scopes), and **Settings → Pages → Source = GitHub Actions**.

## How to change a role

1. Open the instance repo.
2. Edit the role document under `team/roles/` (and only ask for `_base/` or `framework/` changes via a human-approved framework sync).
3. Save/commit (or ask the Lead to apply your wording — interactive Lead only edits `team/` on your explicit ask).
4. On the agent’s **next** run it re-reads the doc — behaviour updates without changing the Scheduled Task prompt.

## How to pause or resume an agent

- **Pause:** stop or disable that role’s Claude Scheduled Task ([use the product’s current controls]). Optionally leave a board message `type: info` that the role is paused.
- **Resume:** turn the schedule back on. The agent syncs from `main` onto its `claude/*` branch and reads `state.md` + open board messages.

Do not delete role docs just to pause; keep history.

## How to read the board

- Path: `team/board/`
- One file per message. Filename and frontmatter show from → to, type, status, priority.
- Open items need action. `needs-human` means the Lead is waiting on you. `from: human` is your inbox into the team.
- Done items may be moved to `team/board/archive/YYYY-MM/` by the Lead.

## When something looks stuck

1. Check the board for `blocker` or stale `in-progress` messages.
2. Check `agents/<role>/state.md` and the latest file under `agents/<role>/runs/` **on the `main` branch**.
3. Check GitHub **Actions**:
   - If you see **red** runs of **Merge agent branches**, tell the Lead — agent work may be sitting on a `claude/*` branch and not landing on `main`.
   - Also check fetch/dashboard jobs (`framework/docs/GITHUB_ACTIONS_PRIMER.md`).
4. Remember: a task list showing “success” is **not** proof that files reached `main`.

Silent skips are not allowed by process — absence of a board note on a known failure is itself a problem; tell the Lead.

## What never to put in the repo

API keys, passwords, private personal data, confidential attachments. If unsure, ask the Lead to keep it out of git and summarise instead. Do not edit `framework/` casually — it is a reference copy from the template.

## Approving outward work

Final reports and company-wide or public text stay **draft** with `needs-human` until you say yes through the Lead. The Lead is the only agent that should message you.
