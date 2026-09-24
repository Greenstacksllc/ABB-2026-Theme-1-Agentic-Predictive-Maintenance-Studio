# Agentic Predictive Maintenance Studio — ABB Accelerator 2026

An independently runnable, synthetic-data proof of concept by GreenStacks LLC for Theme 1.
It demonstrates a bounded agent workflow: **ingest → assess → draft → human review**.

## Public project links

- [Open the Predictive Maintenance Studio](https://abb-predictive-maintenance-studio.replit.app/)
- [Watch the animated project demo](https://abb-predictive-maintenance-studio.replit.app/abb-maintenance-video/)

The hosted website and animation are separate from this local Python prototype.

## Try it in under a minute

Python 3.10+ is the only requirement. No API keys, external services, or packages.

```bash
python3 server.py
```

Open `http://127.0.0.1:8765`, select **Run full sample**, inspect the PUMP-02
evidence and decision trace, then approve or dismiss the draft with a reviewer name.
Use **Reset demo** to replay. The sample has normal readings, a warning, and a
critical event. You can paste an additional observation into the JSON form.

For a machine-readable CLI demonstration:

```bash
python3 studio.py
python3 studio.py --csv examples/telemetry.csv
python3 -m unittest discover -s tests -v
```

## What the prototype actually does

- Validates sensor values and timezone-aware timestamps; rejects repeated or
  out-of-order observations per asset without corrupting asset state.
- Assesses three telemetry fields against clearly labeled **illustrative demo
  limits** and records observed values and limits for each breached sensor.
- Uses a transparent, rule-based relative indicator and persistence rule. It
  does **not** estimate failure probability or remaining useful life.
- Drafts and updates one reviewable work order per affected asset, avoiding a
  new order for each sample. A named human reviewer approves or dismisses it.
- Keeps an in-memory trace of validation, assessment, and planning decisions.

The local dashboard and CLI share the same `MaintenanceStudio` workflow.
The local server binds to `127.0.0.1`; in Replit it binds to `0.0.0.0` using
the assigned `PORT`. It has no authentication or persistent storage: a public
deployment is a disposable synthetic demo and visitors can reset it or review
its drafts. It must not be used with real operational data. There is no live
equipment connection, ABB system integration, CMMS integration, trained ML
model, or autonomous control. All demonstration readings are synthetic.

## Architecture

| Stage | Input | Output | Guardrail |
| --- | --- | --- | --- |
| Ingestion | Asset ID, UTC timestamp, three readings | Accepted observation or explicit rejection | Range, finiteness, schema, ordering |
| Assessment | Valid reading, per-asset prior state | Severity, relative indicator, evidence | Explainable illustrative limits |
| Planning | Non-normal assessment | Updated draft work order | One draft per asset; no equipment action |
| Review | Draft, reviewer, decision | Approved or dismissed status | Explicit human decision |

`studio.py` contains the workflow and seeded synthetic stream. `server.py`
exposes a local JSON API and serves `dashboard.html`. `tests/` verifies the
critical decision and data-quality behavior. `examples/telemetry.csv` is a
reproducible sample. The software uses Python standard library only.

## Reproduce the demo

1. Load the dashboard and click **Process next sample** twice: the asset
   observations remain normal.
2. Process the next PUMP-02 sample: an evidence-backed warning draft appears.
3. Process the following sample: the same draft escalates to critical, with
   vibration and temperature readings shown next to demo limits.
4. Enter a reviewer name and approve or dismiss the draft. This action is
   recorded in the running process.
5. Paste a duplicate timestamp for PUMP-02: it is rejected, and the accepted
   count remains unchanged. Click **Reset demo** to start over.

## Contest submission notes

- **Project summary:** This synthetic proof of concept converts traceable
  condition monitoring into technician-reviewed maintenance drafts. Its
  differentiator is a clear evidence and decision trail, with human control.
- **Prototype:** Run locally using the command above; the existing hosted
  project is at https://abb-predictive-maintenance-studio.replit.app/ and should
  be updated separately if it is meant to show this implementation.
- **Source:** Submit this repository after syncing these files to GitHub.
- **Demo video:** Record a 60–90 second walkthrough using the five steps above,
  show one review decision, and say that all data and limits are illustrative.
- **Future work:** Obtain permitted industrial data, validate limits with
  domain specialists, measure false alerts and detection lead time, add durable
  per-tenant event storage and authentication, then evaluate a CMMS connector.

**Silicon Lag — patent pending:** Proprietary implementation is deliberately
excluded from this public reference prototype. Any separate integration or
performance assertion needs its own reproducible validation and IP review.

## Ownership and licensing

Copyright (c) 2026 Greenstacks LLC. All rights reserved. See `LICENSE`: evaluation
of this prototype is permitted; other use requires written permission. No
third-party code is bundled.
