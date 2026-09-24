# HackerEarth submission draft

## Project title

Agentic Predictive Maintenance Studio — Evidence to Action

## Project description

Maintenance teams need a clear path from noisy condition readings to an
actionable, reviewable response. This prototype simulates asset telemetry,
validates data quality, identifies readings above illustrative limits, records
the evidence and decision trace, and prepares a single draft maintenance work
order per asset. A technician must explicitly approve or dismiss that draft.

The reproducible demo contains normal, warning, and critical observations.
It highlights explainability, duplicate-alert control, and human oversight.
The prototype is based on synthetic data and rule-based indicators; it does
not make validated failure forecasts or actuate industrial equipment.

## Built with

Python 3 standard library; HTML, CSS, JavaScript. No paid service or API key.

## Setup instructions

1. Download and extract the source repository.
2. Run `python3 server.py` from the project directory (Python 3.10+).
3. Open `http://127.0.0.1:8765` on the same computer.
4. Choose **Run full sample**, inspect the PUMP-02 alert, and enter a name to
   approve or dismiss its work order.
5. Run `python3 -m unittest discover -s tests -v` to see the decision tests.

## Suggested 75-second demo narration

- 0–10 s: “This is a synthetic, technician-reviewed maintenance prototype.”
- 10–25 s: Click **Process next sample** until PUMP-02 shows a warning.
- 25–40 s: Process its next sample; show the critical evidence and decision trace.
- 40–55 s: Show that one work order has escalated rather than duplicating it.
- 55–65 s: Enter a reviewer name and approve or dismiss the draft.
- 65–75 s: Show a rejected duplicate observation and the unchanged accepted count.

Replace the repository, live demo, and video fields with actual working links
only after they have been uploaded and checked. This draft does not claim a
production integration or a measured reduction in downtime.
