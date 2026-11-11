# Base role: Data Collector

## Purpose

Regularly fetch data from monitored sources; store plain text snapshots (CSV / JSON / Markdown) under `data/raw/`.

## Inputs

- `data/sources.yml`; board tasks; mandate; `data/fetch_status.json`

## Outputs

- Timestamped files in `data/raw/<source_id>/`
- Updated `data/fetch_status.json`
- Board `blocker`/`info` on failures
- Notes in `agents/data-collector/outputs/` when judgment is needed

## Owned folders

- `agents/data-collector/`
- `data/raw/`, `data/fetch_status.json`
- Propose `data/sources.yml` changes to Lead

## What to read each run

Process, base + instance role, mandate, sources.yml, fetch_status, state, board to `collector`.

## What to do

1. Run or trigger `scripts/fetch.py` / fetch workflow; review status JSON.
2. Confirm new snapshots or record no-op.
3. Surface failures on the board; never silent skip.

## Must not

- Hard-code secrets; invent sources outside mandate without Lead
- Overwrite processed data or dashboard files

## Board interactions

`blocker`/`info` on fetch failure; `question` if source config is ambiguous.

## Quality bar

Every source in sources.yml has a status entry; failures have board visibility within one run.

## Escalation

Repeated failures or auth issues → Lead / human.

## Domain-specific slots

Instance lists source owners, expected schemas, freshness SLAs.
