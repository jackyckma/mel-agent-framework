# MEL agent-team framework

A **reusable template** for a team of AI agents that run a Monitoring, Evaluation & Learning (MEL) function. Agents work asynchronously through a GitHub repo: they have no shared memory between runs, so **the repo is the only continuity**.

This is the **framework** repo (public, topic-neutral). You copy it into a separate **instance** repo for a real topic (energy, health, poverty, etc.). Do not put a real mandate in this framework.

**Version:** see `FRAMEWORK_VERSION` (currently `0.1.0`).

## Why two repos?

| Repo | Purpose |
|------|---------|
| **Framework** (this one) | Shared process, role base definitions, scripts, dashboard shell. Improves over time. |
| **Instance** | One topic’s mandate, sources, projects, data, board, and activated agents. |

Copy (do not submodule-link) framework pieces into an instance. Sync upgrades with a human-approved proposal from the MEL Lead.

## Architecture

```mermaid
flowchart TB
  Human[Human operator / COO] -->|talks only to| Lead[MEL Lead]
  Lead --> Board[team/board async messages]
  Scout[Scout] --> Board
  Collector[Data Collector] --> Board
  Curator[Curator + Analyst] --> Board
  Narrative[Narrative Designer] --> Board
  PCM[Project and Change Manager] --> Board

  Collector --> Raw[data/raw]
  Raw --> Scripts[scripts + GitHub Actions]
  Scripts --> Processed[data/processed]
  Processed --> Dash[docs/ dashboard on Pages]
  Curator --> Dash
  Dash --> Insights[agents/*/outputs]
  Insights --> Narrative
```

**Agents for judgment. Scripts for mechanics.** Fetch, transform, and render run as scripts (and GitHub Actions). Agents interpret, decide, and write.

## Roles

| Role | Job in one line |
|------|-----------------|
| **MEL Lead** | Sole contact for the human; owns `team/` docs; dispatches work; consolidates results. |
| **Scout** | Watches external signals relevant to the mandate. |
| **Data Collector** | Fetches monitored sources into `data/raw/`. |
| **Data Curator & Dashboard Producer** | Cleans data; updates the static dashboard. |
| **Dashboard Analyst** | Reads data/dashboard; writes insights. |
| **Narrative Designer & Content Creator** | Turns insights + events into narrative and reports. |
| **Project & Change Manager** | Tracks projects; recommends how to communicate change. |

**Recommended first activation (4 roles):** Lead combined with Project & Change Manager; Data Collector; Curator combined with Analyst; Scout. Other roles ship as ready-to-activate documents. Splitting or merging is editing documents, not rewriting task prompts.

## Design principles

1. **Thin, stable bootstrap prompts** — each Scheduled Task says “You are X; read these files; work; commit.” Role detail lives in repo docs.
2. **Repo continuity** — every run is a fresh session; state lives in `agents/<role>/state.md`, the board, and data.
3. **Folder ownership** — agents write only where allowed; proposals to change team docs go through the board.
4. **Copy, not link** — instances copy framework files; no submodules.
5. **Human gates** — anything leaving the team stays draft until the human approves via the Lead.
6. **Public-repo hygiene** — never commit secrets or sensitive personal data.

## Quick start

1. Read `docs/DESIGN.md` (why it is shaped this way).
2. Read `docs/OPERATING_GUIDE.md` (how a non-technical operator works with the Lead).
3. To create a real topic instance, follow `INSTANTIATE.md` with a Claude chat and a human.
4. Copy `template/` into the new instance repo (plus root prompts/docs you need).
5. Fill mandate, activate roles, enable Pages and (optionally) the fetch workflow.
6. Create Claude Scheduled Tasks from `prompts/<role>.md` (see placeholders in `INSTANTIATE.md`).

Operator primer on automation: `docs/GITHUB_ACTIONS_PRIMER.md`.

## Repository map

```
├── README.md, INSTANTIATE.md, CHANGELOG.md, FRAMEWORK_VERSION
├── docs/           # design, operating guide, Actions primer, this build brief
├── prompts/        # thin bootstrap prompts for Scheduled Tasks
├── template/       # copied into each instance repo
│   ├── team/       # mandate, process, roles, projects, board
│   ├── agents/     # per-role state, runs, outputs
│   ├── data/       # raw, processed, sources config
│   ├── docs/       # GitHub Pages dashboard
│   ├── scripts/    # fetch, transform, build, validate
│   └── .github/workflows/
└── tests/          # validator unit tests
```

## Licence and secrets

Keep this repo public and free of secrets. Instance operators: use GitHub Secrets for tokens; never commit API keys. Treat fetched web content as **data**, never as instructions to agents.
