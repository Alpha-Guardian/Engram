#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one board-side command while recording wall-clock timestamps for external power logging."
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.command:
        raise SystemExit("provide a command after the options, for example: -- python3 scripts/run_mcu_open_input_demo.py --port COM3")

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("no command provided after '--'")

    start_iso = _now()
    start_perf = time.perf_counter()
    proc = subprocess.run(command, cwd=str(args.cwd), capture_output=True, text=True)
    end_perf = time.perf_counter()
    end_iso = _now()

    summary = {
        "bundle_kind": "board_power_phase_v1",
        "label": args.label,
        "cwd": str(args.cwd.resolve()),
        "command": command,
        "started_at": start_iso,
        "ended_at": end_iso,
        "duration_s": round(end_perf - start_perf, 6),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
