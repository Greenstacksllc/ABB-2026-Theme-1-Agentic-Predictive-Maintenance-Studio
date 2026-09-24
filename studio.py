"""Demonstration maintenance workflow using synthetic data only.

This public reference implementation intentionally excludes proprietary methods.
It is a decision-support prototype, not a safety controller or validated model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LIMITS = {"vibration_mm_s": 7.0, "temperature_c": 80.0, "pressure_bar": 8.0}
REQUIRED = ("asset_id", "timestamp", *LIMITS)


@dataclass
class AssetState:
    asset_id: str
    last_timestamp: datetime | None = None
    observations: int = 0
    elevated_streak: int = 0
    last_values: dict[str, float] = field(default_factory=dict)


class MaintenanceStudio:
    """Three bounded stages: validate, assess, and draft a reviewable action."""

    def __init__(self) -> None:
        self.assets: dict[str, AssetState] = {}
        self.work_orders: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.rejections: list[dict[str, str]] = []

    def ingest(self, row: dict[str, Any]) -> dict[str, Any]:
        """Validate one observation; reject invalid or late data before state changes."""
        try:
            missing = [name for name in REQUIRED if name not in row or row[name] in (None, "")]
            if missing:
                raise ValueError("missing: " + ", ".join(missing))
            asset = str(row["asset_id"]).strip()
            if not asset or len(asset) > 80:
                raise ValueError("asset_id must contain 1–80 characters")
            timestamp = datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("timestamp must include a timezone")
            timestamp = timestamp.astimezone(timezone.utc)
            values = {key: float(row[key]) for key in LIMITS}
            if any(not math.isfinite(v) or v < 0 or v > 10000 for v in values.values()):
                raise ValueError("sensor values must be finite and within 0–10000")
            state = self.assets.get(asset)
            if state and state.last_timestamp and timestamp <= state.last_timestamp:
                raise ValueError("duplicate or out-of-order timestamp for asset")
        except (TypeError, ValueError, OverflowError) as exc:
            rejection = {"asset_id": str(row.get("asset_id", "unknown"))[:80], "reason": str(exc)}
            self.rejections.append(rejection)
            return {"accepted": False, **rejection}

        # Assessment uses transparent limits. These are illustrative demo values,
        # not manufacturer specifications or a trained failure probability.
        ratios = {key: values[key] / threshold for key, threshold in LIMITS.items()}
        breached = [key for key, ratio in ratios.items() if ratio >= 1]
        previous = state.last_values if state else {}
        rising = [key for key in LIMITS if key in previous and values[key] > previous[key] * 1.1]
        streak = (state.elevated_streak if state else 0) + 1 if breached else 0
        severity = "critical" if len(breached) >= 2 or streak >= 3 else "warning" if breached else "normal"
        score = round(min(100.0, max(ratios.values()) * 60 + 10 * (len(breached) - 1 if breached else 0)), 1)
        new_state = state or AssetState(asset)
        new_state.last_timestamp = timestamp
        new_state.last_values = values
        new_state.observations += 1
        new_state.elevated_streak = streak
        self.assets[asset] = new_state

        evidence = [{"sensor": key, "observed": values[key], "demo_limit": LIMITS[key]}
                    for key in breached]
        event: dict[str, Any] = {
            "asset_id": asset, "timestamp": timestamp.isoformat(), "severity": severity,
            "relative_risk_indicator": score, "evidence": evidence,
            "rising_sensors": rising, "elevated_streak": streak,
            "trace": ["Ingestion: validated telemetry and ordering",
                      "Assessment: compared readings with illustrative limits"],
        }
        if severity != "normal":
            # One open draft per asset. Further readings enrich the evidence,
            # rather than creating a work order on every sample.
            order_id = f"WO-{asset}"
            order = self.work_orders.get(order_id)
            if not order or order["status"] in ("closed", "dismissed"):
                order = {"id": order_id, "asset_id": asset, "status": "needs_review"}
                self.work_orders[order_id] = order
            if order["status"] == "needs_review":
                order.update({"severity": severity, "evidence": evidence,
                              "recommended_action": self._recommend(breached),
                              "latest_observation": timestamp.isoformat()})
            event["work_order_id"] = order_id
            event["trace"].append("Planning: updated a draft work order for human review")
        else:
            event["trace"].append("Planning: no action drafted")
        self.events.append(event)
        return {"accepted": True, **event}

    @staticmethod
    def _recommend(breached: list[str]) -> str:
        actions = {
            "vibration_mm_s": "Inspect vibration source and rotating components",
            "temperature_c": "Check cooling and thermal load",
            "pressure_bar": "Verify pressure instrumentation and process conditions",
        }
        return "; ".join(actions[key] for key in breached) + ". Verify onsite before any intervention."

    def review(self, order_id: str, decision: str, reviewer: str) -> dict[str, Any]:
        if decision not in ("approve", "dismiss") or not reviewer.strip():
            raise ValueError("decision and reviewer are required")
        order = self.work_orders.get(order_id)
        if not order or order["status"] != "needs_review":
            raise ValueError("work order is unavailable for review")
        order["status"] = "approved" if decision == "approve" else "dismissed"
        order["reviewer"] = reviewer.strip()[:80]
        order["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        return order.copy()

    def snapshot(self) -> dict[str, Any]:
        return {
            "assets": [{"asset_id": state.asset_id, "observations": state.observations,
                        "last_values": state.last_values, "elevated_streak": state.elevated_streak}
                       for state in self.assets.values()],
            "events": self.events[-100:], "work_orders": list(self.work_orders.values()),
            "rejections": self.rejections[-100:],
            "disclaimer": "Synthetic demo. Rule-based indicators are not validated predictions or safety instructions.",
        }


def demo_rows() -> list[dict[str, Any]]:
    base = "2026-09-24T12:00:"
    return [
        {"asset_id": "MOTOR-01", "timestamp": base + "00Z", "vibration_mm_s": 3.1, "temperature_c": 55, "pressure_bar": 4.1},
        {"asset_id": "PUMP-02", "timestamp": base + "01Z", "vibration_mm_s": 5.2, "temperature_c": 72, "pressure_bar": 6.1},
        {"asset_id": "PUMP-02", "timestamp": base + "02Z", "vibration_mm_s": 7.4, "temperature_c": 76, "pressure_bar": 6.4},
        {"asset_id": "PUMP-02", "timestamp": base + "03Z", "vibration_mm_s": 8.6, "temperature_c": 84, "pressure_bar": 6.6},
        {"asset_id": "MOTOR-01", "timestamp": base + "04Z", "vibration_mm_s": 3.2, "temperature_c": 56, "pressure_bar": 4.0},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic predictive maintenance demonstration")
    parser.add_argument("--csv", type=Path, help="CSV with asset_id, timestamp and three sensor columns")
    args = parser.parse_args()
    studio = MaintenanceStudio()
    if args.csv:
        with args.csv.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    else:
        rows = demo_rows()
    for row in rows:
        studio.ingest(row)
    print(json.dumps(studio.snapshot(), indent=2))


if __name__ == "__main__":
    main()
