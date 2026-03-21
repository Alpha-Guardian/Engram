#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_logiqa_file(path: Path) -> list[dict]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", path.read_text(encoding="utf-8", errors="ignore")) if b.strip()]
    rows: list[dict] = []
    for block in blocks:
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        if len(lines) < 6:
            continue
        gold = lines[0].lower()
        if gold not in {"a", "b", "c", "d"}:
            continue
        options: dict[str, str] = {}
        option_start = None
        for idx, line in enumerate(lines[1:], start=1):
            match = re.match(r"^([A-D])\.(.*)$", line)
            if not match:
                continue
            options[match.group(1)] = match.group(2).strip()
            if option_start is None:
                option_start = idx
        if len(options) != 4 or option_start is None:
            continue
        stem = "\n".join(lines[1:option_start]).strip()
        rows.append({"gold": gold, "stem": stem, "options": options})
    return rows


def _accuracy_from_report(path: Path) -> float:
    report = _read_json(path)
    return float(report.get("benchmarks", {}).get("LogiQA", {}).get("accuracy", 0.0) or 0.0)


def _load_predictors(workspace_root: Path) -> tuple[object, object]:
    tools_root = workspace_root / "tools"
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    from three_benchmark_seed_model import load_model, predict_logiqa_option

    return load_model, predict_logiqa_option


def _pair_counts(samples: list[dict], left_model: dict, right_model: dict, predict_logiqa_option: object) -> dict:
    improved = 0
    harmed = 0
    ties = 0
    sample_rows = []
    for idx, sample in enumerate(samples):
        gold = str(sample["gold"]).lower()
        left_pred = str(predict_logiqa_option(str(sample["stem"]), dict(sample["options"]), left_model)).lower()
        right_pred = str(predict_logiqa_option(str(sample["stem"]), dict(sample["options"]), right_model)).lower()
        left_ok = left_pred == gold
        right_ok = right_pred == gold
        if right_ok and not left_ok:
            improved += 1
        elif left_ok and not right_ok:
            harmed += 1
        else:
            ties += 1
        sample_rows.append(
            {
                "index": idx,
                "gold": gold,
                "left_pred": left_pred,
                "right_pred": right_pred,
                "left_correct": left_ok,
                "right_correct": right_ok,
            }
        )
    return {
        "samples": len(samples),
        "improved": improved,
        "harmed": harmed,
        "ties": ties,
        "rows": sample_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public industrial-wrapper protected slice.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    out_json = (
        args.out_json.resolve()
        if args.out_json is not None
        else (repo_root / "results/experiments/industrial_wrapper_protected_slice.json")
    )

    taskset = repo_root / "results/experiments/industrial_wrapper_protected_slice_v1.txt"
    out_dir = workspace_root / "artifacts/reports/public_cross_task"
    parent_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_20260310_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_ready.json"
    current_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    no_trunk_checkpoint = workspace_root / "artifacts/reports/public_cross_task/checkpoints/current_scientific_surface_no_trunk_industrial_state_decision_probe.json"
    trained_linear_checkpoint = workspace_root / "artifacts/reports/public_controls/checkpoints/parent_gpu_trained_linear_head_baseline.json"

    surfaces = [
        ("frozen_authoritative_parent", "Frozen authoritative parent", parent_checkpoint, "industrial_wrapper_protected18_parent"),
        ("current_no_trunk_ablation", "Current no-trunk ablation", no_trunk_checkpoint, "industrial_wrapper_protected18_no_trunk"),
        ("parent_gpu_trained_linear_head_baseline", "Parent trained linear baseline", trained_linear_checkpoint, "industrial_wrapper_protected18_trained_linear"),
        ("current_scientific_surface", "Current promoted scientific surface", current_checkpoint, "industrial_wrapper_protected18_current"),
    ]

    rows = []
    for surface_id, label, checkpoint, output_tag in surfaces:
        cmd = [
            "python3",
            "tools/run_authoritative_five_bench.py",
            "--checkpoint",
            str(checkpoint),
            "--benchmarks",
            "LogiQA",
            "--logiqa-input-data",
            str(taskset),
            "--out-dir",
            str(out_dir),
            "--output-tag",
            output_tag,
            "--strict-no-official-fallback",
            "1",
        ]
        output = _run(cmd, workspace_root)
        report_path = Path(_extract_prefixed_line(output, "authoritative_five_bench_report="))
        rows.append(
            {
                "surface_id": surface_id,
                "label": label,
                "accuracy": round(_accuracy_from_report(report_path), 6),
                "checkpoint": {
                    "path": str(checkpoint.relative_to(workspace_root)).replace("\\", "/"),
                    "sha256": _sha256(checkpoint),
                },
                "source": {
                    "path": str(report_path.relative_to(workspace_root)).replace("\\", "/"),
                    "sha256": _sha256(report_path),
                },
            }
        )

    load_model, predict_logiqa_option = _load_predictors(workspace_root)
    parsed_samples = _parse_logiqa_file(taskset)
    model_cache = {
        "parent": load_model(parent_checkpoint),
        "no_trunk": load_model(no_trunk_checkpoint),
        "trained_linear": load_model(trained_linear_checkpoint),
        "current": load_model(current_checkpoint),
    }
    pairwise = {
        "current_vs_parent": _pair_counts(parsed_samples, model_cache["parent"], model_cache["current"], predict_logiqa_option),
        "current_vs_no_trunk": _pair_counts(parsed_samples, model_cache["no_trunk"], model_cache["current"], predict_logiqa_option),
        "current_vs_trained_linear": _pair_counts(parsed_samples, model_cache["trained_linear"], model_cache["current"], predict_logiqa_option),
    }

    row_map = {row["surface_id"]: row for row in rows}
    current_acc = float(row_map["current_scientific_surface"]["accuracy"])
    parent_acc = float(row_map["frozen_authoritative_parent"]["accuracy"])
    no_trunk_acc = float(row_map["current_no_trunk_ablation"]["accuracy"])
    trained_linear_acc = float(row_map["parent_gpu_trained_linear_head_baseline"]["accuracy"])

    bundle = {
        "bundle_kind": "public_industrial_wrapper_protected_slice_v1",
        "generated_at": _now(),
        "task": "industrial_wrapper_protected_slice_v1",
        "metric": "accuracy",
        "taskset": {
            "path": str(taskset.relative_to(repo_root)).replace("\\", "/"),
            "sha256": _sha256(taskset),
            "samples": len(parsed_samples),
            "task_style": "curated_light_domain_shift_slice",
            "scope": "industrial_or_embedded_wrapper_reasoning",
        },
        "rows": rows,
        "summary": {
            "current_vs_parent_delta": round(current_acc - parent_acc, 6),
            "current_vs_no_trunk_delta": round(current_acc - no_trunk_acc, 6),
            "current_vs_trained_linear_delta": round(current_acc - trained_linear_acc, 6),
            "current_above_parent": bool(current_acc > parent_acc),
            "current_above_no_trunk": bool(current_acc > no_trunk_acc),
            "current_above_trained_linear": bool(current_acc > trained_linear_acc),
        },
        "pairwise": pairwise,
        "notes": [
            "This is a curated protected transfer slice built from public current-win reasoning shapes and wrapped in industrial or embedded review language.",
            "It is intended to show a cleaner route-localized transfer signal than the broader lightly domain-shifted probe.",
            "Because the slice is curated, it should be interpreted as protected-slice evidence rather than as a broad naturally sampled second-task benchmark.",
        ],
    }
    _write_json(out_json, bundle)


if __name__ == "__main__":
    main()
