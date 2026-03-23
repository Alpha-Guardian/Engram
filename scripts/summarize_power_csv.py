#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


TIME_KEYS = (
    "time_s",
    "time_sec",
    "elapsed_s",
    "elapsed_sec",
    "timestamp_s",
    "seconds",
    "t_s",
)

TIME_MS_KEYS = (
    "time_ms",
    "elapsed_ms",
    "timestamp_ms",
    "milliseconds",
    "t_ms",
)

CURRENT_MA_KEYS = (
    "current_ma",
    "avg_current_ma",
    "ibus_ma",
    "current(mA)",
    "current_ma_avg",
)

CURRENT_A_KEYS = (
    "current_a",
    "avg_current_a",
    "current(A)",
)

CURRENT_UA_KEYS = (
    "current_ua",
    "avg_current_ua",
    "current(uA)",
)

VOLTAGE_V_KEYS = (
    "voltage_v",
    "vbus_v",
    "voltage(V)",
    "avg_voltage_v",
)

POWER_MW_KEYS = (
    "power_mw",
    "avg_power_mw",
    "power(mW)",
)

POWER_W_KEYS = (
    "power_w",
    "avg_power_w",
    "power(W)",
)


def _clean_key(key: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in key).strip("_")


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def _pick_float(row: dict[str, str], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if key in row:
            value = _parse_float(row[key])
            if value is not None:
                return value
    return None


def _load_rows(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit(f"CSV has no header: {path}")
        field_map = {name: _clean_key(name) for name in reader.fieldnames}
        rows: list[dict[str, float]] = []
        for raw in reader:
            norm = {field_map[k]: v for k, v in raw.items() if k is not None}
            time_s = _pick_float(norm, TIME_KEYS)
            if time_s is None:
                time_ms = _pick_float(norm, TIME_MS_KEYS)
                if time_ms is not None:
                    time_s = time_ms / 1000.0
            current_ma = _pick_float(norm, CURRENT_MA_KEYS)
            if current_ma is None:
                current_a = _pick_float(norm, CURRENT_A_KEYS)
                if current_a is not None:
                    current_ma = current_a * 1000.0
            if current_ma is None:
                current_ua = _pick_float(norm, CURRENT_UA_KEYS)
                if current_ua is not None:
                    current_ma = current_ua / 1000.0
            voltage_v = _pick_float(norm, VOLTAGE_V_KEYS)
            power_mw = _pick_float(norm, POWER_MW_KEYS)
            if power_mw is None:
                power_w = _pick_float(norm, POWER_W_KEYS)
                if power_w is not None:
                    power_mw = power_w * 1000.0
            if power_mw is None and current_ma is not None and voltage_v is not None:
                power_mw = current_ma * voltage_v
            if time_s is None:
                continue
            row = {"time_s": float(time_s)}
            if current_ma is not None:
                row["current_ma"] = float(current_ma)
            if voltage_v is not None:
                row["voltage_v"] = float(voltage_v)
            if power_mw is not None:
                row["power_mw"] = float(power_mw)
            rows.append(row)
    if not rows:
        raise SystemExit(f"CSV produced no parseable time-series rows: {path}")
    rows.sort(key=lambda x: x["time_s"])
    return rows


def _window(rows: list[dict[str, float]], start_s: float | None, end_s: float | None) -> list[dict[str, float]]:
    if start_s is None and end_s is None:
        return rows
    out: list[dict[str, float]] = []
    for row in rows:
        t = row["time_s"]
        if start_s is not None and t < start_s:
            continue
        if end_s is not None and t > end_s:
            continue
        out.append(row)
    if not out:
        raise SystemExit("selected time window is empty")
    return out


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _integrate_trapezoid(rows: list[dict[str, float]], key: str) -> float | None:
    if len(rows) < 2:
        return None
    total = 0.0
    pairs = 0
    for a, b in zip(rows[:-1], rows[1:]):
        if key not in a or key not in b:
            continue
        dt = b["time_s"] - a["time_s"]
        if dt <= 0:
            continue
        total += 0.5 * (a[key] + b[key]) * dt
        pairs += 1
    if pairs == 0:
        return None
    return total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a board power log CSV into average current, power, and energy."
    )
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--label", default="board_power_window")
    parser.add_argument("--start-s", type=float, default=None)
    parser.add_argument("--end-s", type=float, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    csv_path = args.csv.resolve()
    out_path = args.output.resolve()
    rows = _window(_load_rows(csv_path), args.start_s, args.end_s)

    current_values = [row["current_ma"] for row in rows if "current_ma" in row]
    voltage_values = [row["voltage_v"] for row in rows if "voltage_v" in row]
    power_values = [row["power_mw"] for row in rows if "power_mw" in row]

    energy_mj = _integrate_trapezoid(rows, "power_mw")
    charge_mc = _integrate_trapezoid(rows, "current_ma")

    summary = {
        "bundle_kind": "board_power_summary_v1",
        "label": args.label,
        "source_csv": str(csv_path),
        "notes": args.notes,
        "window": {
            "start_s": float(rows[0]["time_s"]),
            "end_s": float(rows[-1]["time_s"]),
            "duration_s": float(rows[-1]["time_s"] - rows[0]["time_s"]),
            "samples": len(rows),
        },
        "metrics": {
            "avg_current_ma": round(_mean(current_values), 6) if current_values else None,
            "peak_current_ma": round(max(current_values), 6) if current_values else None,
            "avg_voltage_v": round(_mean(voltage_values), 6) if voltage_values else None,
            "avg_power_mw": round(_mean(power_values), 6) if power_values else None,
            "peak_power_mw": round(max(power_values), 6) if power_values else None,
            "energy_mj": round(float(energy_mj), 6) if energy_mj is not None else None,
            "charge_mA_s": round(float(charge_mc), 6) if charge_mc is not None else None,
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
