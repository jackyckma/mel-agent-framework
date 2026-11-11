# Instantiate a MEL agent-team instance

Use this guide in a Claude chat with a human operator. The chat interviews the human, fills the template, and outputs bootstrap prompts and schedules. Keep language plain.

## Placeholders (complete list)

Replace every `{{…}}` when creating an instance:

| Placeholder | Meaning |
|-------------|---------|
| `{{TOPIC}}` | Short topic name (e.g. “energy transition in Region X”) |
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
| `{{CADENCE_COLLECTOR}}` | Collector schedule (default suggestion below) |
| `{{CADENCE_CURATOR}}` | Curator schedule |
| `{{CADENCE_ANALYST}}` | Analyst schedule |
| `{{CADENCE_NARRATIVE}}` | Narrative schedule |
| `{{CADENCE_SCOUT}}` | Scout schedule |
| `{{CADENCE_LEAD}}` | Lead digest schedule |
| `{{SOURCES_NOTES}}` | Human notes on initial sources |
| `{{HUMAN_CONTACT}}` | How the Lead reaches the human (channel placeholder) |
| `{{FRAMEWORK_VERSION}}` | Copied framework version string |

## Step 0 — Prerequisites

- Human has a GitHub account and can create a **new public or private** repo.
- Human can [create a scheduled task in Claude and paste the prompt] (exact UI may change; do not invent button names).
- Framework version to copy: read `FRAMEWORK_VERSION` from this framework repo.

## Step 1 — Interview the human

Ask, one cluster at a time; confirm answers before writing files:

1. **Topic & purpose** — What is monitored? Why? (`{{TOPIC}}`, `{{PURPOSE}}`)
2. **Audience & decisions** — Who reads outputs? Which decisions do they inform? (`{{AUDIENCE}}`, `{{DECISIONS_INFORMED}}`)
3. **Scope** — In / out of scope (`{{SCOPE}}`, `{{OUT_OF_SCOPE}}`)
4. **Sources** — Websites, APIs, feeds, cadence expectations (`{{SOURCES_NOTES}}`)
5. **Cadences** — Accept defaults or tune (see Step 5)
6. **Roles to activate** — Recommend starting with four:
   - MEL Lead **+** Project & Change Manager (combined)
   - Data Collector
   - Data Curator & Dashboard Producer **+** Dashboard Analyst (combined)
   - Scout  
   Ship others as inactive base docs until needed. Record `{{ACTIVE_ROLES}}`.
7. **Repo** — Desired `{{ORG_OR_USER}}` / `{{REPO_NAME}}` / visibility.
8. **Human contact** — How the Lead reports (`{{HUMAN_CONTACT}}`).

## Step 2 — Create the instance repo

1. Create an empty GitHub repository `{{REPO_NAME}}`.
2. Copy the contents of this framework’s `template/` directory to the **root** of the instance repo.
3. Also copy useful root docs the instance needs: `prompts/` (or keep prompts only in the chat output), and set `FRAMEWORK_VERSION` to `{{FRAMEWORK_VERSION}}`.
4. Fill `team/mandate.md` slots with interview answers.
5. Adjust `team/process.md` only if the human needs a documented cadence exception (prefer leaving process stable).
6. For each activated role, fill domain slots in `team/roles/<role>.md`. For combined roles, put both sets of duties in one instance role doc and point `agents/` at one slug (document the mapping in `team/roles/README.md`).
7. Add real sources to `data/sources.yml` (start from `data/sources.example.yml`; remove or keep the example clearly marked).
8. Commit and push.

## Step 3 — GitHub Pages and Actions

1. In the **instance** repo Settings → Pages: set source to **GitHub Actions** (or the branch/`docs/` folder if that is how the instance enables Pages). Exact clicks may vary — use GitHub’s current docs.
2. Confirm `.github/workflows/pages.yml` and `validate.yml` are present.
3. Leave `fetch.yml` schedule **commented out** until sources are trusted; then uncomment and set cron.
4. Never put secrets in the repo; use GitHub Actions secrets if a source needs a token (extend `fetch.py` carefully).

**Note:** Enable Pages **per instance**. The framework repo itself is not the live dashboard host. The framework owner should also mark the framework repo as a **Template repository** in Settings (manual).

## Step 4 — Generate bootstrap prompts

For each activated role, take `prompts/<role>.md` from the framework, substitute:

- `{{ROLE_NAME}}`
- `{{REPO_URL}}`
- `{{ROLE_DOC}}`, `{{BASE_ROLE_DOC}}`, `{{ROLE_SLUG}}`

Keep each prompt under ~150 words. Do **not** paste role duties into the prompt.

## Step 5 — Suggested schedules (tunable)

Stagger the pipeline so upstream work lands before downstream reads:

| Role | Default suggestion | Placeholder |
|------|--------------------|-------------|
| Data Collector | Every 6 hours, e.g. minute 0 | `{{CADENCE_COLLECTOR}}` |
| Curator (+ Analyst if combined) | ~1–2 hours after collector | `{{CADENCE_CURATOR}}` / `{{CADENCE_ANALYST}}` |
| Narrative Designer | After analyst window, daily or twice weekly | `{{CADENCE_NARRATIVE}}` |
| Scout | Weekly | `{{CADENCE_SCOUT}}` |
| MEL Lead | Daily digest | `{{CADENCE_LEAD}}` |

Output for the human: a table of role → bootstrap prompt (full text) → schedule string → “create a scheduled task in Claude and paste the prompt”.

## Step 6 — Post-setup verification checklist

- [ ] `team/mandate.md` has no remaining empty `{{…}}` for activated fields
- [ ] `FRAMEWORK_VERSION` matches the framework copy
- [ ] `python scripts/validate_repo.py` passes in the instance
- [ ] Example or real `docs/data/*.json` loads in the dashboard locally (open `docs/index.html` or Pages URL)
- [ ] Board has a README; `_templates/` present
- [ ] Each active role has `agents/<slug>/state.md`
- [ ] Ownership table understood by the human (only Lead edits `team/` except board messages)
- [ ] First Lead run can post a hello `needs-human` digest
- [ ] Fetch workflow still disabled until sources reviewed
- [ ] No secrets in the repo
- [ ] Scheduled Tasks created for each active role with thin prompts only

## Step 7 — Hand-off

Give the human:

1. Link to `docs/OPERATING_GUIDE.md` (in framework or copied into instance `docs/ops/` if desired)
2. The prompt + schedule table
3. Reminder: change behaviour by editing role docs, not prompts
4. Reminder: framework feedback goes `team/framework-feedback/` → human → framework repo
