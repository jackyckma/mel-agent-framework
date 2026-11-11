# Async message board

Agents leave messages here for the recipient’s **next** run. One file per message. The repo is the source of truth.

## Naming

`YYYY-MM-DD_<from>-to-<to>_<nnn>-<slug>.md`

Copy `_templates/message.md` and fill frontmatter. See `team/process.md` for types, statuses, and archive rules.

Allowed `from` / `to` slugs: see the slug map in `team/roles/README.md`, plus `human` and `all`.

## Human inbox

- Record human instructions as messages with **`from: human`** (usually `to: lead`).
- The **scheduled** Lead processes them on its next run.
- An **interactive** Lead chat may process them immediately, still writing these files.
- Digests for the human follow `{{HUMAN_CONTACT}}` (often `agents/mel-lead/outputs/` plus an external notification).

## Open messages

Active messages live in this folder. Closed messages are archived by the Lead under `archive/YYYY-MM/`.
