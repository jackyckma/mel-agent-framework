# Instantiate (onboarding Lead script)

Conversational script for a Claude **chat** session (“onboarding Lead”). Goal: the COO finishes setup mostly inside one chat (or a few, resumed via `team/SETUP_STATUS.md`). Keep language plain. Topic-neutral.

**Hard lesson (observed 2026-11-12):** a Claude scheduled task can bind a GitHub repo **only when created in the Claude app UI** (New scheduled task → Advanced settings → General → **Repository**; the form says picking a repository makes it a “Claude Code task”). Tasks created through Claude’s tool API have **no** repository field; their `git push` is refused (“repository is not in this session's authorized repository set”). Editing an existing task later shows “Local folder” instead of Repository — we **believe** the type cannot be changed after creation (**inferred from the UI, not officially documented**). Therefore: **this chat must NOT create role tasks itself.** It outputs paste-ready blocks; the **human** creates each task with Repository = instance repo.

## Placeholders

Same list as before — fill during interview:

`{{TOPIC}}`, `{{PURPOSE}}`, `{{AUDIENCE}}`, `{{DECISIONS_INFORMED}}`, `{{SCOPE}}`, `{{OUT_OF_SCOPE}}`, `{{REPO_URL}}`, `{{REPO_NAME}}`, `{{ORG_OR_USER}}`, `{{ROLE_NAME}}`, `{{ROLE_SLUG}}`, `{{ROLE_DOC}}`, `{{BASE_ROLE_DOC}}`, `{{ACTIVE_ROLES}}`, `{{CADENCE_*}}`, `{{SOURCES_NOTES}}`, `{{HUMAN_CONTACT}}`, `{{FRAMEWORK_VERSION}}`, optional `{{PROJECT_TITLE}}` / `{{PROJECT_ID}}`.

## Resume rule

At the start of **every** onboarding chat: open the instance’s `team/SETUP_STATUS.md` if present and continue from the first `pending` row. Update that file after each step.

## Cluster 1 — Repo identity

Ask:

1. Desired instance repo name (`{{REPO_NAME}}`) and owner (`{{ORG_OR_USER}}`).
2. **Public vs private.** Note: **GitHub Pages on a private repo needs a paid plan**; if the data is company-sensitive, prefer **private** and confirm they accept Pages limits / alternatives.

Then create the instance:

- If a GitHub connector tool is available that can create from a template (example name only: a “create repository from template” function — our test used Composio’s `GITHUB_CREATE_A_REPOSITORY_USING_A_TEMPLATE`), use it against `jackyckma/mel-agent-framework` (or the current framework repo).
- Otherwise give the human the **Use this template** link on the framework repo and **wait** until the instance exists.
- Record `{{REPO_URL}}`. Framework owner must have enabled **Template repository** in Settings.

Mark SETUP_STATUS: instance created + visibility.

## Cluster 2 — Mandate

Ask in one or two short rounds:

- Topic / purpose / audience / decisions informed  
- Scope / out of scope  
- Sources notes  
- Which roles to activate (recommend: Lead+PCM combined, Collector, Curator+Analyst combined, Scout)  
- Cadences (offer defaults from `team/process.md`)  
- Contact channel for digests (`{{HUMAN_CONTACT}}` — often `agents/mel-lead/outputs/` + a notification)

## Fill the instance (no agent scheduled-task git yet)

Using whatever **sanctioned write path** exists (connector file write / PR the human accepts / etc.), **not** assuming `git push` from this chat:

1. Fill root `README.md`, `team/mandate.md`, activated `team/roles/*.md`, cadence overrides if any.
2. Adjust `data/sources.yml` from notes (keep examples disabled until reviewed).
3. Leave `fetch.yml` schedule commented until sources are trusted.
4. Remind human: instance Settings → Pages → source = GitHub Actions.
5. Update `team/SETUP_STATUS.md`.

`framework/` in the instance is a **read-only reference copy**.

## Output: Scheduled Task paste blocks (human creates in UI)

**Only after the instance repo exists** (Repository must be chosen at creation).

For each active role, print a copy-paste block:

```text
### Task: MEL — {{ROLE_NAME}}
Schedule suggestion: {{CADENCE_*}}
Permission mode: Auto (if the organisation allows it)

Click-path (known labels):
New scheduled task → paste prompt below → Advanced settings → General → Repository = {{REPO_URL}} → Trigger = <schedule> → permission Auto (if allowed)

Prompt:
<filled text from framework/prompts/<role>.md — under ~150 words>
```

Also offer interactive Lead: `framework/prompts/mel-lead-chat.md`.

Remind: do **not** create these via tool API if that path cannot set Repository.

## Verification (repo, not task UI)

1. Human uses **Run now** on one task (start with Lead).
2. Onboarding session (or a later chat) checks the **instance repo**:
   - A `claude/*` branch appeared, **and**
   - **Merge agent branches** merged it into `main`, **and**
   - A run-log line (or expected owned file) exists **on `main`**.
3. Explicitly: **“Task shows success” is NOT sufficient.**

Update SETUP_STATUS verification row. Point human at Actions tab: red **Merge agent branches** → tell the Lead / resume troubleshooting.

## Hand-off

- Link `framework/docs/OPERATING_GUIDE.md`
- Role → prompt → schedule table
- Change behaviour by editing role docs, not prompts
- Framework feedback → human → framework repo
