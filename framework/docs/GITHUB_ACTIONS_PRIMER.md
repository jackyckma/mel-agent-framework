# GitHub Actions primer (plain English)

## What it is

**GitHub Actions** is an automation robot that runs small jobs on GitHub’s servers when something happens (for example a push) or on a timer. You do not need to leave your laptop on.

## Three concepts

| Word | Meaning |
|------|---------|
| **Trigger** | What starts a run: a push, a pull request, a schedule, or a manual button (`workflow_dispatch`). |
| **Job** | A unit of work on a virtual machine (often “one OS, install tools, run commands”). |
| **Steps** | The ordered commands inside a job (checkout repo, run a script, upload a page). |

Workflow files live in `.github/workflows/*.yml` and are commented in plain English in this framework.

## What this framework uses it for

1. **`validate.yml`** — On push/PR, run `scripts/validate_repo.py` so board filenames and required structure stay healthy.
2. **`pages.yml`** — Deploy the static `docs/` dashboard to **GitHub Pages**.
3. **`fetch.yml`** — Optionally run fetch → transform → build dashboard on a schedule, then commit if files changed. **Disabled (commented) by default** in the template until an instance turns it on.
4. **`merge-agent-branches.yml`** — When an agent pushes a `claude/*` branch, validate it (using **main**’s checker scripts), reject protected-path edits, merge into `main`, delete the branch, and dispatch Pages. If this workflow shows **red** in the Actions tab, tell the MEL Lead — work may not have landed on `main`.

Why Actions? Reliable mechanical work (download, convert, publish, merge) without spending a Claude agent run. Agents still **decide and interpret**; they review script output on the board and in `data/`.

## Cost

For **public** repositories, Actions minutes are free within GitHub’s generous limits. Private repos have a monthly allowance. Check GitHub’s current billing docs if you scale up.

## Where to see runs and failures

In the instance GitHub repo, open the **Actions** tab. Each workflow run shows green (ok) or red (failed). Click a failed run → failed step → log text. Paste that summary to the MEL Lead if you want an agent to interpret it.

## How it relates to Claude agents

```text
Timer / push → GitHub Actions → updates data/ or docs/
                ↑
Claude agents read results, judge quality, write insights, post board messages
```

Agents maintain and review scripts; they should not replace Actions for repetitive HTTP fetch when Actions can do it. If the shell inside an agent run cannot reach arbitrary websites, Actions (or a trusted runner) is the right place for fetching.
