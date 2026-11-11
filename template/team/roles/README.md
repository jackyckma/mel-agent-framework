# Roles (instance)

- **`_base/`** — Generic framework definitions. Do not edit in normal runs; update only via human-approved framework sync.
- **`*.md` (this folder)** — Instance layer: “Follow `_base/<role>.md`, plus domain specifics below.” Fill slots at instantiation.
- **Activation:** schedule only the roles listed in the mandate. Recommended start: Lead+PCM combined, Collector, Curator+Analyst combined, Scout.
- **Combining roles:** use one instance doc that references both bases, one `agents/<slug>/` folder, and document the slug mapping here.

## Slug map (template defaults)

| Role | Agent folder slug | Board from/to slug |
|------|-------------------|--------------------|
| MEL Lead | `mel-lead` | `lead` |
| Scout | `scout` | `scout` |
| Data Collector | `data-collector` | `collector` |
| Data Curator & Dashboard Producer | `data-curator` | `curator` |
| Dashboard Analyst | `dashboard-analyst` | `analyst` |
| Narrative Designer & Content Creator | `narrative-designer` | `narrative` |
| Project & Change Manager | `project-change-manager` | `pcm` |

### Combined-role mapping (fill if used)

| Combined name | Slug | Bases followed |
|---------------|------|----------------|
| _e.g. Lead + PCM_ | _e.g. mel-lead_ | _list bases_ |
