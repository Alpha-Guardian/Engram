#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _run(cmd: list[str], workdir: Path) -> str:
    completed = subprocess.run(
        cmd,
        cwd=workdir,
        text=True,
        capture_output=True,
        check=True,
    )
    return (completed.stdout or "") + (completed.stderr or "")


def _extract_prefixed_line(output: str, prefix: str) -> str:
    for line in output.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise RuntimeError(f"missing expected line: {prefix}\noutput:\n{output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public host-side open-input structured demo.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--manifest-out", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    manifest_out = (
        args.manifest_out.resolve()
        if args.manifest_out is not None
        else (workspace_root / "artifacts/reports/public_controls/public_open_input_demo_manifest.json")
    )

    checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    taskset = workspace_root / "configs/tasksets/chip_structured_exec_taskset_v1.jsonl"
    out_dir = workspace_root / "artifacts/reports/public_controls"
    out_dir.mkdir(parents=True, exist_ok=True)

    structured_cmd = [
        "python3",
        "tools/run_chip_structured_exec_eval.py",
        "--checkpoint",
        str(checkpoint),
        "--taskset",
        str(taskset),
        "--out-dir",
        str(out_dir),
        "--output-tag",
        "current_surface_public_open_input_structured",
    ]
    edge_cmd = [
        "python3",
        "tools/run_chip_edge_runtime_eval.py",
        "--checkpoint",
        str(checkpoint),
        "--ifeval-input-data",
        "artifacts/tmp/authoritative_five_bench_cache/ifeval_input_data.jsonl",
        "--logiqa-input-data",
        "artifacts/tmp/authoritative_five_bench_cache/logiqa_test.txt",
        "--ifeval-samples",
        "16",
        "--logiqa-samples",
        "16",
        "--stability-probe-count",
        "3",
        "--stability-repeats",
        "2",
        "--out-dir",
        str(out_dir),
        "--output-tag",
        "current_surface_public_open_input_edge",
    ]

    structured_output = _run(structured_cmd, workspace_root)
    structured_report = _extract_prefixed_line(structured_output, "chip_structured_exec_report=")
    edge_output = _run(edge_cmd, workspace_root)
    edge_report = _extract_prefixed_line(edge_output, "chip_edge_runtime_report=")

    manifest = {
        "manifest_kind": "public_open_input_demo_v1",
        "generated_at": _now(),
        "checkpoint": str(checkpoint),
        "taskset": str(taskset),
        "structured_report": structured_report,
        "edge_runtime_report": edge_report,
        "claim_boundary": {
            "host_open_input_demo": True,
            "mcu_open_input_demo": False,
            "note": "This public demo is a host-side open-input structured loop. It is intentionally separate from the fixed-batch ESP32-C3 board proof.",
        },
    }
    _write_json(manifest_out, manifest)


if __name__ == "__main__":
    main()
