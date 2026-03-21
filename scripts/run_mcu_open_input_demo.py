#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _norm_text(text: str) -> str:
    return " ".join(str(text or "").strip().split())


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    idx = (len(sorted_values) - 1) * max(0.0, min(1.0, float(q)))
    lo = int(idx)
    hi = min(len(sorted_values) - 1, lo + 1)
    if lo == hi:
        return float(sorted_values[lo])
    w = idx - lo
    return float(sorted_values[lo] * (1.0 - w) + sorted_values[hi] * w)


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        obj = json.loads(s)
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _collect_key_values(lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in lines:
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _run_deepseek_command(ser, command: str, timeout_s: float) -> tuple[bool, list[str], float]:
    # pyserial returns bytes and handles \r\n framing from board output.
    start = time.perf_counter()
    ser.reset_input_buffer()
    ser.write((command + "\n").encode("utf-8"))
    ser.flush()
    lines: list[str] = []
    output_seen = False
    expected_cmd = f"cmd={command}"
    cmd_seen = False
    deadline = start + max(0.1, timeout_s)
    while time.perf_counter() < deadline:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        lines.append(line)
        if line == expected_cmd:
            cmd_seen = True
            continue
        if line.startswith("deepseek_output=") and cmd_seen:
            output_seen = True
            break
        if line.startswith("error=") and cmd_seen:
            break
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return output_seen, lines, elapsed_ms


def _run_info_command(ser, timeout_s: float) -> list[str]:
    ser.reset_input_buffer()
    ser.write(b"INFO\n")
    ser.flush()
    lines: list[str] = []
    deadline = time.perf_counter() + max(0.2, timeout_s)
    while time.perf_counter() < deadline:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        lines.append(line)
    return lines


def _parse_deepseek_output(lines: list[str]) -> str:
    for line in reversed(lines):
        if line.startswith("deepseek_output="):
            return line[len("deepseek_output=") :].strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the published ESP32-C3 MCU open-input demo and export summary JSON.")
    parser.add_argument("--port", default="COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument(
        "--taskset",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results/open_input_demo/mcu_open_input_taskset_v1.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results/open_input_demo/mcu_open_input_demo.json",
    )
    parser.add_argument("--command-timeout-ms", type=int, default=1500)
    parser.add_argument("--boot-wait-ms", type=int, default=1200)
    parser.add_argument("--stability-probes", type=int, default=3)
    parser.add_argument("--stability-repeats", type=int, default=2)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    taskset_path = args.taskset.resolve()
    output_path = args.output.resolve()
    taskset_display = str(taskset_path)
    output_display = str(output_path)
    try:
        taskset_display = str(taskset_path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        pass
    try:
        output_display = str(output_path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        pass
    if not taskset_path.exists():
        raise SystemExit(f"taskset not found: {taskset_path}")

    rows = _read_jsonl(taskset_path)
    if not rows:
        raise SystemExit(f"taskset is empty: {taskset_path}")

    try:
        import serial  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "pyserial is not installed in this Python environment. Run "
            "`py -m pip install pyserial` and retry."
        ) from exc

    ser = serial.Serial(args.port, baudrate=args.baud, timeout=0.05)
    try:
        time.sleep(max(0.0, float(args.boot_wait_ms) / 1000.0))
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Warm up and get basic runtime identity.
        ser.reset_input_buffer()
        ser.write(b"HELP\n")
        ser.flush()
        time.sleep(0.2)
        info_lines = _run_info_command(ser, timeout_s=0.8)
        board_info_raw = _collect_key_values(info_lines)
        board_info = {
            "artifact_name": str(board_info_raw.get("artifact_name", "")),
            "artifact_sha256": str(board_info_raw.get("artifact_sha256", "")),
            "board_run_id": str(board_info_raw.get("board_run_id", "")),
            "evaluation_mode": str(board_info_raw.get("evaluation_mode", "")),
            "gpu_sample_count": str(board_info_raw.get("gpu_sample_count", "")),
            "linear_sample_count": str(board_info_raw.get("linear_sample_count", "")),
            "ifeval_sample_count": str(board_info_raw.get("ifeval_sample_count", "")),
        }

        timeout_s = max(0.2, float(args.command_timeout_ms) / 1000.0)
        per_row: list[dict] = []
        latencies: list[float] = []
        exact_match_count = 0
        nonempty_count = 0

        for idx, row in enumerate(rows):
            source = str(row.get("source", "") or "")
            target = str(row.get("target", "") or "")
            split = str(row.get("split", "new") or "new").strip().lower()
            if not source:
                continue
            ok, lines, elapsed_ms = _run_deepseek_command(ser, f"RUN DEEPSEEK {source}", timeout_s=timeout_s)
            output = _parse_deepseek_output(lines)
            nonempty = bool(output)
            exact_match = _norm_text(output) == _norm_text(target)
            if exact_match:
                exact_match_count += 1
            if nonempty:
                nonempty_count += 1
            latencies.append(float(elapsed_ms))
            per_row.append(
                {
                    "index": idx,
                    "split": split,
                    "source": source,
                    "target": target,
                    "output": output,
                    "exact_match": exact_match,
                    "nonempty": nonempty,
                    "response_ok": bool(ok),
                    "latency_ms": round(float(elapsed_ms), 6),
                }
            )

        # Stability probe: first N rows, repeated runs.
        probe_count = min(max(0, int(args.stability_probes)), len(per_row))
        repeats = max(1, int(args.stability_repeats))
        stability_cases: list[dict] = []
        stable_cases = 0
        for i in range(probe_count):
            source = str(per_row[i]["source"])
            outputs: list[str] = []
            for _ in range(repeats):
                _, lines, _ = _run_deepseek_command(ser, f"RUN DEEPSEEK {source}", timeout_s=timeout_s)
                outputs.append(_parse_deepseek_output(lines))
            unique_outputs = sorted(set(outputs))
            stable = len(unique_outputs) == 1
            if stable:
                stable_cases += 1
            stability_cases.append(
                {
                    "index": int(per_row[i]["index"]),
                    "repeats": repeats,
                    "unique_outputs": len(unique_outputs),
                    "stable": stable,
                }
            )
    finally:
        ser.close()

    total = len(per_row)
    sorted_latencies = sorted(latencies)
    split_summary: dict[str, dict[str, float]] = {}
    for split_name in sorted(set(str(row.get("split", "new")) for row in per_row)):
        split_rows = [row for row in per_row if str(row.get("split", "new")) == split_name]
        split_total = len(split_rows)
        split_exact = sum(1 for row in split_rows if bool(row.get("exact_match")))
        split_nonempty = sum(1 for row in split_rows if bool(row.get("nonempty")))
        split_summary[split_name] = {
            "samples": split_total,
            "exact_match_rate": round(split_exact / split_total, 6) if split_total else 0.0,
            "nonempty_rate": round(split_nonempty / split_total, 6) if split_total else 0.0,
        }

    payload = {
        "bundle_kind": "public_mcu_open_input_demo_v1",
        "generated_at": _now(),
        "port": args.port,
        "board_info": board_info,
        "taskset": {
            "path": taskset_display,
            "sha256": _sha256(taskset_path),
            "samples": total,
        },
        "summary": {
            "samples": total,
            "exact_match_rate": round(exact_match_count / total, 6) if total else 0.0,
            "nonempty_rate": round(nonempty_count / total, 6) if total else 0.0,
            "avg_latency_ms": round(statistics.fmean(latencies), 6) if latencies else 0.0,
            "p50_latency_ms": round(_percentile(sorted_latencies, 0.50), 6),
            "p95_latency_ms": round(_percentile(sorted_latencies, 0.95), 6),
            "split_metrics": split_summary,
            "stability_probe": {
                "probe_cases": probe_count,
                "stable_cases": stable_cases,
                "stability_rate": round(stable_cases / probe_count, 6) if probe_count else 0.0,
                "cases": stability_cases,
            },
            "gates": {
                "min_exact_match_rate": 1.0,
                "min_nonempty_rate": 1.0,
                "exact_match_pass": (round(exact_match_count / total, 6) if total else 0.0) >= 1.0,
                "nonempty_pass": (round(nonempty_count / total, 6) if total else 0.0) >= 1.0,
            },
        },
        "claim_boundary": {
            "host_open_input_demo": True,
            "mcu_open_input_demo": True,
            "scope": "narrow_unit_normalization_loop",
            "note": "This MCU demo is a tightly constrained open-input micro-loop and does not replace the fixed-batch board-proof boundary.",
        },
        "rows": per_row,
    }
    payload["summary"]["gates"]["all_pass"] = bool(
        payload["summary"]["gates"]["exact_match_pass"] and payload["summary"]["gates"]["nonempty_pass"]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"mcu_open_input_report={output_display}")
    print(f"samples={total}")
    print(f"exact_match_rate={payload['summary']['exact_match_rate']}")
    print(f"nonempty_rate={payload['summary']['nonempty_rate']}")
    print(f"all_pass={payload['summary']['gates']['all_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    taskset_display = str(taskset_path)
    output_display = str(output_path)
    try:
        taskset_display = str(taskset_path.relative_to(repo_root))
    except ValueError:
        pass
    try:
        output_display = str(output_path.relative_to(repo_root))
    except ValueError:
        pass
