# Operating guide (for the human operator)

You are the COO-side owner of a MEL agent team. You talk to **one** agent: the **MEL Lead**. Everything else happens in the GitHub repo.

## How to talk to the Lead

- Give goals, priorities, audience, and “what decision this informs.”
- Prefer short written instructions the Lead can turn into board tasks.
- Ask for a digest: what moved, what is blocked, what needs you.
- Do not try to brief every agent yourself — the Lead dispatches.

Use whatever channel you and the Lead agreed at setup (`{{HUMAN_CONTACT}}` in the instance).

## How to change a role

1. Open the instance repo.
2. Edit the role document under `team/roles/` (and only ask for `_base/` changes via a framework sync).
3. Save/commit (or ask the Lead to apply your wording).
4. On the agent’s **next** run it re-reads the doc — behaviour updates without changing the Scheduled Task prompt.

## How to pause or resume an agent

- **Pause:** stop or disable that role’s Claude Scheduled Task ([create/manage a scheduled task in Claude — use the product’s current controls]). Optionally leave a board message `type: info` that the role is paused.
- **Resume:** turn the schedule back on. The agent should `git pull` and read `state.md` + open board messages.

Do not delete role docs just to pause; keep history.

## How to read the board

- Path: `team/board/`
- One file per message. Filename and frontmatter show from → to, type, status, priority.
- Open items need action. `needs-human` means the Lead is waiting on you.
- Done items may be moved to `team/board/archive/YYYY-MM/` by the Lead.

## When something looks stuck

1. Check the board for `blocker` or stale `in-progress` messages.
2. Check `agents/<role>/state.md` and the latest file under `agents/<role>/runs/`.
3. Check GitHub Actions run history if fetch/dashboard jobs exist (`docs/GITHUB_ACTIONS_PRIMER.md`).
4. Tell the Lead what you see; ask for a recovery plan (retry, skip source, escalate).

Silent skips are not allowed by process — absence of a board note on a known failure is itself a problem; tell the Lead.

## Creating a Scheduled Task from a bootstrap prompt

1. Open the prompt text produced at instantiation (from `prompts/<role>.md` with placeholders filled).
2. [Create a scheduled task in Claude and paste the prompt].
3. Set the cadence from the instantiation table.
4. Point it at the instance repo access your organisation already uses for Claude↔GitHub (follow your company’s setup; do not invent UI steps here).

Keep prompts thin. If you need new behaviour, edit the repo docs.

## What never to put in the repo

API keys, passwords, private personal data, confidential attachments. If unsure, ask the Lead to keep it out of git and summarise instead.

## Approving outward work

Final reports and company-wide or public text stay **draft** with `needs-human` until you say yes through the Lead. The Lead is the only agent that should message you.
