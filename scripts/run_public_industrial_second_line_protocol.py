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


def _accuracy_from_report(path: Path, benchmark: str = "LogiQA") -> float:
    report = _read_json(path)
    entry = dict(report.get("benchmarks", {}).get(benchmark, {}) or {})
    if benchmark == "IFEval":
        return float(entry.get("strict_prompt_accuracy", 0.0) or 0.0)
    return float(entry.get("accuracy", 0.0) or 0.0)


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
    rows = []
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
        rows.append(
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
        "rows": rows,
    }


def _merge_pair_counts(left: dict, right: dict) -> dict:
    return {
        "samples": int(left.get("samples", 0) or 0) + int(right.get("samples", 0) or 0),
        "improved": int(left.get("improved", 0) or 0) + int(right.get("improved", 0) or 0),
        "harmed": int(left.get("harmed", 0) or 0) + int(right.get("harmed", 0) or 0),
        "ties": int(left.get("ties", 0) or 0) + int(right.get("ties", 0) or 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public industrial second-line formal protocol.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    out_json = (
        args.out_json.resolve()
        if args.out_json is not None
        else (repo_root / "results/experiments/industrial_second_line_protocol.json")
    )

    train_source = repo_root / "results/experiments/industrial_wrapper_protected_slice_v1.txt"
    dev_task = repo_root / "results/experiments/industrial_state_decision_logiqa_lite_v1.txt"
    blind_task = repo_root / "results/experiments/industrial_state_decision_logiqa_v2.txt"
    out_dir = workspace_root / "artifacts/reports/public_cross_task"

    parent_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_20260310_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_ready.json"
    current_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    no_trunk_checkpoint = workspace_root / "artifacts/reports/public_cross_task/checkpoints/current_scientific_surface_no_trunk_industrial_state_decision_probe.json"
    trained_linear_checkpoint = workspace_root / "artifacts/reports/public_controls/checkpoints/parent_gpu_trained_linear_head_baseline.json"
    candidate_checkpoint = workspace_root / "artifacts/reports/public_cross_task/subsets/industrial_wrapper_targets_5_6_8_10.json"

    surfaces = [
        ("frozen_authoritative_parent", "Frozen authoritative parent", parent_checkpoint, "industrial_second_line_protocol_parent"),
        ("current_no_trunk_ablation", "Current no-trunk ablation", no_trunk_checkpoint, "industrial_second_line_protocol_no_trunk"),
        ("parent_gpu_trained_linear_head_baseline", "Parent trained linear baseline", trained_linear_checkpoint, "industrial_second_line_protocol_trained_linear"),
        ("current_scientific_surface", "Current promoted scientific surface", current_checkpoint, "industrial_second_line_protocol_current"),
        ("industrial_second_line_candidate", "Independent industrial second-line candidate 5+6+8+10", candidate_checkpoint, "industrial_second_line_protocol_candidate"),
    ]

    rows = []
    for surface_id, label, checkpoint, output_tag in surfaces:
        dev_cmd = [
            "python3",
            "tools/run_authoritative_five_bench.py",
            "--checkpoint",
            str(checkpoint),
            "--benchmarks",
            "LogiQA",
            "--logiqa-input-data",
            str(dev_task),
            "--out-dir",
            str(out_dir),
            "--output-tag",
            f"{output_tag}_dev",
            "--strict-no-official-fallback",
            "1",
        ]
        blind_cmd = [
            "python3",
            "tools/run_authoritative_five_bench.py",
            "--checkpoint",
            str(checkpoint),
            "--benchmarks",
            "LogiQA",
            "--logiqa-input-data",
            str(blind_task),
            "--out-dir",
            str(out_dir),
            "--output-tag",
            f"{output_tag}_blind",
            "--strict-no-official-fallback",
            "1",
        ]
        dev_output = _run(dev_cmd, workspace_root)
        blind_output = _run(blind_cmd, workspace_root)
        dev_report_path = Path(_extract_prefixed_line(dev_output, "authoritative_five_bench_report="))
        blind_report_path = Path(_extract_prefixed_line(blind_output, "authoritative_five_bench_report="))

        row = {
            "surface_id": surface_id,
            "label": label,
            "metrics": {
                "dev_accuracy": round(_accuracy_from_report(dev_report_path), 6),
                "blind_accuracy": round(_accuracy_from_report(blind_report_path), 6),
            },
            "checkpoint": {
                "path": str(checkpoint.relative_to(workspace_root)).replace("\\", "/"),
                "sha256": _sha256(checkpoint),
            },
            "sources": {
                "dev": {
                    "path": str(dev_report_path.relative_to(workspace_root)).replace("\\", "/"),
                    "sha256": _sha256(dev_report_path),
                },
                "blind": {
                    "path": str(blind_report_path.relative_to(workspace_root)).replace("\\", "/"),
                    "sha256": _sha256(blind_report_path),
                },
            },
        }
        if surface_id == "industrial_second_line_candidate":
            ifeval_cmd = [
                "python3",
                "tools/run_authoritative_five_bench.py",
                "--checkpoint",
                str(checkpoint),
                "--benchmarks",
                "IFEval",
                "--out-dir",
                str(out_dir),
                "--output-tag",
                f"{output_tag}_ifeval",
            ]
            ifeval_output = _run(ifeval_cmd, workspace_root)
            ifeval_report_path = Path(_extract_prefixed_line(ifeval_output, "authoritative_five_bench_report="))
            row["metrics"]["official_ifeval"] = round(_accuracy_from_report(ifeval_report_path, benchmark="IFEval"), 6)
            row["sources"]["ifeval"] = {
                "path": str(ifeval_report_path.relative_to(workspace_root)).replace("\\", "/"),
                "sha256": _sha256(ifeval_report_path),
            }
        rows.append(row)

    row_map = {row["surface_id"]: row for row in rows}
    candidate_row = row_map["industrial_second_line_candidate"]
    parent_row = row_map["frozen_authoritative_parent"]
    no_trunk_row = row_map["current_no_trunk_ablation"]
    trained_linear_row = row_map["parent_gpu_trained_linear_head_baseline"]
    current_row = row_map["current_scientific_surface"]

    parent_ifeval = 0.780037
    candidate_ifeval = float(candidate_row["metrics"].get("official_ifeval") or 0.0)

    load_model, predict_logiqa_option = _load_predictors(workspace_root)
    dev_samples = _parse_logiqa_file(dev_task)
    blind_samples = _parse_logiqa_file(blind_task)
    model_cache = {
        "parent": load_model(parent_checkpoint),
        "no_trunk": load_model(no_trunk_checkpoint),
        "trained_linear": load_model(trained_linear_checkpoint),
        "current": load_model(current_checkpoint),
        "candidate": load_model(candidate_checkpoint),
    }
    pairwise = {
        "dev_candidate_vs_parent": _pair_counts(dev_samples, model_cache["parent"], model_cache["candidate"], predict_logiqa_option),
        "dev_candidate_vs_no_trunk": _pair_counts(dev_samples, model_cache["no_trunk"], model_cache["candidate"], predict_logiqa_option),
        "dev_candidate_vs_trained_linear": _pair_counts(dev_samples, model_cache["trained_linear"], model_cache["candidate"], predict_logiqa_option),
        "dev_candidate_vs_current": _pair_counts(dev_samples, model_cache["current"], model_cache["candidate"], predict_logiqa_option),
        "blind_candidate_vs_parent": _pair_counts(blind_samples, model_cache["parent"], model_cache["candidate"], predict_logiqa_option),
        "blind_candidate_vs_no_trunk": _pair_counts(blind_samples, model_cache["no_trunk"], model_cache["candidate"], predict_logiqa_option),
        "blind_candidate_vs_trained_linear": _pair_counts(blind_samples, model_cache["trained_linear"], model_cache["candidate"], predict_logiqa_option),
        "blind_candidate_vs_current": _pair_counts(blind_samples, model_cache["current"], model_cache["candidate"], predict_logiqa_option),
    }
    aggregate_pairwise = {
        "external_union_candidate_vs_parent": _merge_pair_counts(pairwise["dev_candidate_vs_parent"], pairwise["blind_candidate_vs_parent"]),
        "external_union_candidate_vs_no_trunk": _merge_pair_counts(pairwise["dev_candidate_vs_no_trunk"], pairwise["blind_candidate_vs_no_trunk"]),
        "external_union_candidate_vs_trained_linear": _merge_pair_counts(pairwise["dev_candidate_vs_trained_linear"], pairwise["blind_candidate_vs_trained_linear"]),
        "external_union_candidate_vs_current": _merge_pair_counts(pairwise["dev_candidate_vs_current"], pairwise["blind_candidate_vs_current"]),
    }

    dev_n = len(dev_samples)
    blind_n = len(blind_samples)
    total_n = dev_n + blind_n

    def _union_accuracy(row: dict) -> float:
        return (
            float(row["metrics"]["dev_accuracy"]) * float(dev_n)
            + float(row["metrics"]["blind_accuracy"]) * float(blind_n)
        ) / float(total_n)

    gates = {
        "dev_above_parent": bool(candidate_row["metrics"]["dev_accuracy"] > parent_row["metrics"]["dev_accuracy"]),
        "dev_above_no_trunk": bool(candidate_row["metrics"]["dev_accuracy"] > no_trunk_row["metrics"]["dev_accuracy"]),
        "dev_above_trained_linear": bool(candidate_row["metrics"]["dev_accuracy"] > trained_linear_row["metrics"]["dev_accuracy"]),
        "dev_at_least_current": bool(candidate_row["metrics"]["dev_accuracy"] >= current_row["metrics"]["dev_accuracy"]),
        "blind_above_parent": bool(candidate_row["metrics"]["blind_accuracy"] > parent_row["metrics"]["blind_accuracy"]),
        "blind_above_no_trunk": bool(candidate_row["metrics"]["blind_accuracy"] > no_trunk_row["metrics"]["blind_accuracy"]),
        "blind_above_trained_linear": bool(candidate_row["metrics"]["blind_accuracy"] > trained_linear_row["metrics"]["blind_accuracy"]),
        "blind_above_current": bool(candidate_row["metrics"]["blind_accuracy"] > current_row["metrics"]["blind_accuracy"]),
        "ifeval_non_regression_vs_parent": bool(candidate_ifeval >= parent_ifeval),
    }
    gates["all_pass"] = all(gates.values())

    external_union = {
        "samples": total_n,
        "candidate_accuracy": round(_union_accuracy(candidate_row), 6),
        "parent_accuracy": round(_union_accuracy(parent_row), 6),
        "no_trunk_accuracy": round(_union_accuracy(no_trunk_row), 6),
        "trained_linear_accuracy": round(_union_accuracy(trained_linear_row), 6),
        "current_accuracy": round(_union_accuracy(current_row), 6),
    }
    external_union["candidate_vs_parent_delta"] = round(
        external_union["candidate_accuracy"] - external_union["parent_accuracy"], 6
    )
    external_union["candidate_vs_no_trunk_delta"] = round(
        external_union["candidate_accuracy"] - external_union["no_trunk_accuracy"], 6
    )
    external_union["candidate_vs_trained_linear_delta"] = round(
        external_union["candidate_accuracy"] - external_union["trained_linear_accuracy"], 6
    )
    external_union["candidate_vs_current_delta"] = round(
        external_union["candidate_accuracy"] - external_union["current_accuracy"], 6
    )

    bundle = {
        "bundle_kind": "public_industrial_second_line_protocol_v1",
        "generated_at": _now(),
        "task": "industrial_second_line_protocol",
        "tasksets": {
            "train_source": {
                "path": str(train_source.relative_to(repo_root)).replace("\\", "/"),
                "sha256": _sha256(train_source),
                "samples": len(_parse_logiqa_file(train_source)),
                "role": "public_train_source_for_the_parent_derived_second_line",
            },
            "dev": {
                "path": str(dev_task.relative_to(repo_root)).replace("\\", "/"),
                "sha256": _sha256(dev_task),
                "samples": len(dev_samples),
                "role": "light_domain_shift_external_dev",
            },
            "blind": {
                "path": str(blind_task.relative_to(repo_root)).replace("\\", "/"),
                "sha256": _sha256(blind_task),
                "samples": len(blind_samples),
                "role": "separate_industrial_state_decision_blind_slice",
            },
        },
        "rows": rows,
        "external_union": external_union,
        "gates": gates,
        "pairwise": pairwise,
        "aggregate_pairwise": aggregate_pairwise,
        "notes": [
            "This protocol freezes the public train source, external dev slice, and blind slice for the parent-derived industrial second-line candidate.",
            "The goal is not to prove broad generalization but to prove that the same frozen-parent trunk pipeline can repeatedly produce a second-task capability line under a fixed auditable protocol.",
            "Because the public second-task benchmark is still small, this bundle should be read as capability-production evidence with a bounded public audit surface.",
        ],
    }
    _write_json(out_json, bundle)


if __name__ == "__main__":
    main()
