# Instantiate a MEL agent-team instance

Use this guide in a Claude chat with a human operator. The chat interviews the human, fills placeholders in the new instance repo, and outputs bootstrap prompts and schedules. Keep language plain.

## Placeholders (complete list)

Replace every `{{…}}` when creating an instance:

| Placeholder | Meaning |
|-------------|---------|
| `{{TOPIC}}` | Short topic name |
| `{{PURPOSE}}` | Why this MEL team exists |
| `{{AUDIENCE}}` | Who reads the outputs |
| `{{DECISIONS_INFORMED}}` | Decisions the outputs should inform |
| `{{SCOPE}}` | In scope |
| `{{OUT_OF_SCOPE}}` | Explicitly out of scope |
| `{{REPO_URL}}` | Instance GitHub repo URL (HTTPS) |
| `{{REPO_NAME}}` | Instance repo name |
| `{{ORG_OR_USER}}` | GitHub org or user that owns the repo |
| `{{ROLE_NAME}}` | Display name of the role for a bootstrap prompt |
| `{{ROLE_SLUG}}` | Folder slug under `agents/` (e.g. `mel-lead`) |
| `{{ROLE_DOC}}` | Path to instance role doc (e.g. `team/roles/mel-lead.md`) |
| `{{BASE_ROLE_DOC}}` | Path to base role (e.g. `team/roles/_base/mel-lead.md`) |
| `{{ACTIVE_ROLES}}` | List of activated roles for this instance |
| `{{CADENCE_COLLECTOR}}` | Collector schedule |
| `{{CADENCE_CURATOR}}` | Curator schedule |
| `{{CADENCE_ANALYST}}` | Analyst schedule |
| `{{CADENCE_NARRATIVE}}` | Narrative schedule |
| `{{CADENCE_SCOUT}}` | Scout schedule |
| `{{CADENCE_LEAD}}` | Lead digest schedule |
| `{{SOURCES_NOTES}}` | Human notes on initial sources |
| `{{HUMAN_CONTACT}}` | Where digests go (e.g. `agents/mel-lead/outputs/` + notification channel) |
| `{{FRAMEWORK_VERSION}}` | Copied framework version string (matches root `FRAMEWORK_VERSION`) |
| `{{PROJECT_TITLE}}` / `{{PROJECT_ID}}` | Optional project template slots |

## Step 0 — Prerequisites

- Human has a GitHub account and can create a repo from a template.
- Framework owner has enabled **Template repository** on `jackyckma/mel-agent-framework` (manual Settings step).
- Human can [create a scheduled task in Claude and paste the prompt] (UI may change; do not invent button names).
- Framework version: read root `FRAMEWORK_VERSION` from the framework repo.

## Step 1 — Interview the human

Ask, one cluster at a time; confirm answers before writing files:

1. **Topic & purpose** — `{{TOPIC}}`, `{{PURPOSE}}`
2. **Audience & decisions** — `{{AUDIENCE}}`, `{{DECISIONS_INFORMED}}`
3. **Scope** — `{{SCOPE}}`, `{{OUT_OF_SCOPE}}`
4. **Sources** — `{{SOURCES_NOTES}}`
5. **Cadences** — accept defaults or tune (Step 5)
6. **Roles to activate** — recommend four: Lead+PCM combined; Data Collector; Curator+Analyst combined; Scout. Record `{{ACTIVE_ROLES}}`.
7. **Repo** — `{{ORG_OR_USER}}` / `{{REPO_NAME}}` / visibility.
8. **Human contact** — digest destination `{{HUMAN_CONTACT}}` (file path under `agents/mel-lead/outputs/` plus any notification the operator sets up).

## Step 2 — Create the instance repo from this template

1. On the framework repo, click **Use this template** (or run `gh repo create {{REPO_NAME}} --template jackyckma/mel-agent-framework --public` / `--private` as agreed).
2. Clone the **new instance** repo. Its root **is** the instance skeleton (`team/`, `agents/`, `data/`, `docs/`, `scripts/`, …). There is no nested `template/` folder to copy.
3. The new repo includes `framework/` as a **read-only reference copy**. Agents never edit `framework/`. Humans update it only via a Lead-led, human-approved framework sync. Root `FRAMEWORK_VERSION` records which framework version this instance was created from.
4. Fill placeholders in root `README.md`, `team/mandate.md`, and activated `team/roles/*.md`.
5. Adjust `team/process.md` cadence overrides only if needed (prefer leaving process stable).
6. For combined roles, document the slug mapping in `team/roles/README.md`.
7. Add real sources to `data/sources.yml` (start from `data/sources.example.yml`; keep examples clearly marked).
8. Commit and push.

## Step 3 — GitHub Pages and Actions

1. Instance Settings → Pages: set source to **GitHub Actions** (exact clicks may vary — use GitHub’s current docs).
2. Confirm `.github/workflows/pages.yml` and `validate.yml` are present.
3. Leave `fetch.yml` schedule **commented out** until sources are trusted; then uncomment and set cron.
4. Never put secrets in the repo; use Actions secrets if a source needs a token.
5. Framework-only CI (`test.yml`) is **guarded** so it does not run (or spam) on instance repos created from the template.

**Note:** Enable Pages **per instance**. The framework maintainer still enables **Template repository** on the framework repo Settings (manual).

## Step 4 — Generate bootstrap prompts

For each activated role, take `framework/prompts/<role>.md`, substitute `{{ROLE_NAME}}`, `{{REPO_URL}}`, `{{ROLE_DOC}}`, `{{BASE_ROLE_DOC}}`, `{{ROLE_SLUG}}`.

Also offer `framework/prompts/mel-lead-chat.md` for an **interactive** Lead chat (human inbox / digests).

Keep each prompt under ~150 words. Do **not** paste role duties into the prompt.

## Step 5 — Suggested schedules (tunable)

| Role | Default suggestion | Placeholder |
|------|--------------------|-------------|
| Data Collector | Every 6 hours | `{{CADENCE_COLLECTOR}}` |
| Curator (+ Analyst if combined) | ~1–2 hours after collector | `{{CADENCE_CURATOR}}` / `{{CADENCE_ANALYST}}` |
| Narrative Designer | After analyst window | `{{CADENCE_NARRATIVE}}` |
| Scout | Weekly | `{{CADENCE_SCOUT}}` |
| MEL Lead | Daily digest | `{{CADENCE_LEAD}}` |

Output: role → full bootstrap prompt → schedule → “[create a scheduled task in Claude and paste the prompt]”.

## Step 6 — Post-setup verification checklist

- [ ] Root `README.md` and `team/mandate.md` have no remaining empty `{{…}}` for activated fields
- [ ] `FRAMEWORK_VERSION` matches the framework the template was created from
- [ ] `python scripts/validate_repo.py` passes at the **instance root**
- [ ] Dashboard loads (`docs/index.html` or Pages URL); empty instance shows “No data yet” / stale, not fake-fresh
- [ ] Board README + `_templates/` present; human inbox convention understood (`from: human`)
- [ ] Each active role has `agents/<slug>/state.md`
- [ ] Ownership understood: only Lead edits `team/` (except board); nobody edits `framework/`, `FRAMEWORK_VERSION`, or `roles/_base/` without human-approved sync
- [ ] First Lead run (or chat) can post a hello `needs-human` digest
- [ ] Fetch workflow still disabled until sources reviewed
- [ ] No secrets in the repo
- [ ] Scheduled Tasks created; interactive Lead chat bootstrap available if desired

## Step 7 — Hand-off

1. Link to `framework/docs/OPERATING_GUIDE.md`
2. Prompt + schedule table (+ optional Lead chat prompt)
3. Reminder: change behaviour by editing role docs, not prompts
4. Reminder: framework feedback → `team/framework-feedback/` → human → framework repo
