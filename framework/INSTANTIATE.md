# Instantiate (onboarding Lead script)

Conversational script for a Claude **chat** (“onboarding Lead” / **[Lead-chat]**). Goal: the **[Owner]** finishes setup mostly inside one chat (resume via `team/SETUP_STATUS.md`). Topic-neutral. Plain English.

**Actors** (label every step):

| Tag | Who |
|-----|-----|
| **[Admin]** | Helper who prepares accounts / org access (e.g. Jacky). |
| **[Owner]** | Person who will run the MEL team (e.g. the COO). |
| **[Lead-chat]** | This Claude chat acting as MEL Lead. |

Humans usually start from `framework/prompts/STARTER_PROMPT.md` (paste into a new chat with GitHub connector).

## Hard rules (observed; do not skip)

- **[Owner]** creates each Claude Scheduled Task **in the Claude app UI**. Chat/API-created tasks have **no Repository** field; their `git push` is refused (“repository is not in this session's authorized repository set”). Editing later may show “Local folder” instead of Repository — we **believe** type cannot change after creation (**inferred from UI, not official docs**).
- A UI option **“Allow unrestricted branch pushes” was NOT found** — do not rely on it. The write path is: task → `claude/*` → **Merge agent branches** → `main`.
- Success = commits / artefacts on **`main`**, never task-list “success” alone.

## Placeholders

`{{TOPIC}}`, `{{PURPOSE}}`, `{{AUDIENCE}}`, `{{DECISIONS_INFORMED}}`, `{{SCOPE}}`, `{{OUT_OF_SCOPE}}`, `{{REPO_URL}}`, `{{REPO_NAME}}`, `{{ORG_OR_USER}}`, `{{ROLE_NAME}}`, `{{ROLE_SLUG}}`, `{{ROLE_DOC}}`, `{{BASE_ROLE_DOC}}`, `{{ACTIVE_ROLES}}`, `{{CADENCE_*}}`, `{{SOURCES_NOTES}}`, `{{HUMAN_CONTACT}}`, `{{FRAMEWORK_VERSION}}`, optional project slots.

## Resume

**[Lead-chat]** at every session start: open instance `team/SETUP_STATUS.md` if present; continue from first `pending` row; update after each step.

## Cluster 1 — Repo identity

**[Lead-chat]** asks **[Owner]** (minimum):

1. Instance repo name (`{{REPO_NAME}}`) and GitHub owner (`{{ORG_OR_USER}}`).
2. Topic (short).
3. Public vs private — note: **private Pages needs a paid plan**; company data → prefer private.

**[Lead-chat]** creates the instance from template `jackyckma/mel-agent-framework` under the owner’s account (connector “create repository from template” if available). Else **[Lead-chat]** gives **[Owner]** the **Use this template** link and waits.

**[Admin]** beforehand: framework repo has **Template repository** enabled; **[Owner]** GitHub + Claude can access the new repo.

Mark SETUP_STATUS: instance created + visibility.

## Cluster 2 — Mandate & roles

**[Lead-chat]** asks **[Owner]** (short rounds): purpose, audience, decisions informed, scope / out of scope, sources notes, which roles to activate (recommend Lead+PCM, Collector, Curator+Analyst, Scout), cadences, `{{HUMAN_CONTACT}}`.

## Fill the instance

**[Lead-chat]** fills via sanctioned connector write (not assuming chat git push): `README.md`, `team/mandate.md`, activated `team/roles/*.md`, `data/sources.yml` (examples stay disabled until reviewed). Leave `fetch.yml` schedule commented until sources trusted. Update `SETUP_STATUS.md`.

## Manual instance Settings (**[Owner]** or **[Admin]**)

Do these in the **instance** GitHub repo (not the framework):

1. **Settings → Actions → General → Workflow permissions** = **Read and write permissions** / allow workflows to read **repository contents** as required so merge/Pages jobs can run (set explicitly; default may be read-only).
2. **Settings → Pages → Source** = **GitHub Actions**.

Update SETUP_STATUS rows for Actions permissions + Pages.

## Scheduled Task paste blocks (**[Lead-chat]** outputs; **[Owner]** creates)

Only after the instance exists (Repository must be chosen at **creation**).

For each active role, **[Lead-chat]** prints:

```text
### Task: MEL — {{ROLE_NAME}}
Schedule suggestion: {{CADENCE_*}}
Permission mode: Auto (if the organisation allows it)

Click-path:
New scheduled task → paste prompt → Advanced settings → General → Repository = {{REPO_URL}}
→ Trigger = <schedule> → permission Auto (if allowed)

Prompt:
<filled framework/prompts/<role>.md>
```

Also offer `framework/prompts/mel-lead-chat.md` for day-to-day chat.

**[Owner]**: create each task in the UI as above. Keep the task **inactive / not Active** until the first-run test below passes; then set **Active**.

## First-run test checklist

**[Owner]** + **[Lead-chat]** verify together:

1. **[Owner]** creates **one** task first (Lead), Repository = instance, permission Auto, paste the Lead bootstrap (or a **minimal test prompt** that only appends a line to `agents/mel-lead/runs/` and follows the git push protocol).
2. **[Owner]** clicks **Run now** (task still not relied on as “Active” until this passes).
3. Expect, in order:
   - a `claude/*` branch appears on the instance repo;
   - Actions: **Trigger merge agent branch** then **Merge agent branches** are **green**;
   - the test commit / run-log line is on **`main`**;
   - **Pages** deploy ran or was dispatched (check Actions / site).
4. If **red**:
   - Open the failed Action log; common causes: Workflow permissions still read-only; Pages source not Actions; protected-path / validate failure; merge conflict; push race (re-run merge / push again after fetch).
   - Tell **[Lead-chat]** / board `blocker`; do **not** mark setup verified.
   - Fix, then **Run now** again until `main` shows the commit.
5. Only then **[Owner]** sets the task **Active**, creates the remaining role tasks the same way, and repeats a light check as needed.

Explicitly: **task UI “success” is NOT enough.**

## Hand-off

- **[Lead-chat]** points **[Owner]** to `framework/docs/OPERATING_GUIDE.md`
- Role → prompt → schedule table
- Change behaviour by editing role docs, not prompts
- Framework feedback → **[Owner]** / **[Admin]** → framework repo
