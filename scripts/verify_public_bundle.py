#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the public github_demo bundle.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to github_demo. Defaults to the parent of this script.",
    )
    args = parser.parse_args()

    repo_root = (args.repo_root or Path(__file__).resolve().parents[1]).resolve()
    manifest_path = repo_root / "results/experiments/manifest.json"
    main_table_path = repo_root / "results/experiments/main_table.json"
    cross_task_validation_path = repo_root / "results/experiments/cross_task_validation.json"
    independent_industrial_second_line_path = repo_root / "results/experiments/independent_industrial_second_line.json"
    industrial_second_line_protocol_path = repo_root / "results/experiments/industrial_second_line_protocol.json"
    industrial_state_decision_probe_path = repo_root / "results/experiments/industrial_state_decision_probe.json"
    industrial_wrapper_protected_slice_path = repo_root / "results/experiments/industrial_wrapper_protected_slice.json"
    causal_sequence_path = repo_root / "results/experiments/causal_sequence.json"
    locality_path = repo_root / "results/experiments/locality_probes.json"
    additional_controls_path = repo_root / "results/experiments/additional_controls.json"
    block_inventory_path = repo_root / "results/experiments/block_inventory.json"
    host_open_input_demo_path = repo_root / "results/open_input_demo/host_open_input_demo.json"
    mcu_open_input_demo_path = repo_root / "results/open_input_demo/mcu_open_input_demo.json"
    mcu_open_input_taskset_path = repo_root / "results/open_input_demo/mcu_open_input_taskset_v1.jsonl"
    mcu_open_input_board_report_path = repo_root / "results/open_input_demo/mcu_open_input_board_report.json"
    scientific_manifest_path = repo_root / "results/research_line/current_host_surface_manifest.json"
    board_summary_path = repo_root / "results/board_proof/esp32c3_logiqa642_board_proof_summary.json"
    board_baseline_comparison_path = repo_root / "results/board_proof/board_baseline_comparison.json"
    overfit_path = repo_root / "results/audit/current_host_surface_overfit_audit_status.json"
    hidden_family_path = repo_root / "results/audit/current_host_surface_hidden_family_forensic_audit_status.json"

    required_paths = [
        manifest_path,
        main_table_path,
        cross_task_validation_path,
        independent_industrial_second_line_path,
        industrial_second_line_protocol_path,
        industrial_state_decision_probe_path,
        industrial_wrapper_protected_slice_path,
        repo_root / "results/experiments/industrial_state_decision_logiqa_lite_v1.txt",
        repo_root / "results/experiments/industrial_state_decision_logiqa_v2.txt",
        repo_root / "results/experiments/industrial_wrapper_protected_slice_v1.txt",
        causal_sequence_path,
        locality_path,
        additional_controls_path,
        block_inventory_path,
        host_open_input_demo_path,
        mcu_open_input_demo_path,
        mcu_open_input_taskset_path,
        mcu_open_input_board_report_path,
        scientific_manifest_path,
        board_summary_path,
        board_baseline_comparison_path,
        overfit_path,
        hidden_family_path,
        repo_root / "scripts/flash_open_input_firmware.py",
        repo_root / "scripts/run_mcu_open_input_demo.py",
        repo_root / "docs/INNOVATION.md",
        repo_root / "docs/FAMILY_AND_ROUTING.md",
        repo_root / "docs/TRUNK_BLOCKS.md",
        repo_root / "docs/PROMOTION_CONTRACT.md",
        repo_root / "docs/EXPERIMENTS.md",
        repo_root / "docs/OPEN_INPUT_DEMO.md",
        repo_root / "docs/OPEN_INPUT_ROADMAP.md",
    ]

    missing = [str(path.relative_to(repo_root)) for path in required_paths if not path.exists()]
    if missing:
        raise SystemExit(json.dumps({"verified": False, "missing": missing}, indent=2))

    manifest = _read_json(manifest_path)
    main_table = _read_json(main_table_path)
    cross_task_validation = _read_json(cross_task_validation_path)
    independent_industrial_second_line = _read_json(independent_industrial_second_line_path)
    industrial_second_line_protocol = _read_json(industrial_second_line_protocol_path)
    industrial_state_decision_probe = _read_json(industrial_state_decision_probe_path)
    industrial_wrapper_protected_slice = _read_json(industrial_wrapper_protected_slice_path)
    locality = _read_json(locality_path)
    additional_controls = _read_json(additional_controls_path)
    block_inventory = _read_json(block_inventory_path)
    mcu_open_input_demo = _read_json(mcu_open_input_demo_path)
    mcu_open_input_board_report = _read_json(mcu_open_input_board_report_path)
    scientific_manifest = _read_json(scientific_manifest_path)
    board_summary = _read_json(board_summary_path)
    board_baseline_comparison = _read_json(board_baseline_comparison_path)
    overfit = _read_json(overfit_path)
    hidden_family = _read_json(hidden_family_path)

    manifest_mismatches = []
    for entry in manifest.get("generated_files", []):
        path = repo_root / entry["path"]
        actual = _sha256(path)
        if actual != entry["sha256"]:
            manifest_mismatches.append(
                {
                    "path": entry["path"],
                    "expected": entry["sha256"],
                    "actual": actual,
                }
            )

    scientific_summary = scientific_manifest.get("scientific_summary", {})
    main_rows = {row["surface_id"]: row for row in main_table.get("rows", [])}
    current_row = main_rows.get("current_scientific_surface", {})
    board_accuracy = float(board_summary.get("accuracy") or 0.0)
    board_baseline_rows = list(board_baseline_comparison.get("rows", []) or [])
    cross_task_summary = dict(cross_task_validation.get("summary", {}) or {})
    independent_second_line_summary = dict(independent_industrial_second_line.get("summary", {}) or {})
    industrial_second_line_protocol_gates = dict(industrial_second_line_protocol.get("gates", {}) or {})
    industrial_second_line_external_union = dict(industrial_second_line_protocol.get("external_union", {}) or {})
    industrial_probe_summary = dict(industrial_state_decision_probe.get("summary", {}) or {})
    industrial_protected_summary = dict(industrial_wrapper_protected_slice.get("summary", {}) or {})
    control_ids = {row.get("control_id") for row in additional_controls.get("controls", [])}
    required_control_ids = {
        "current_surface_no_topology_control",
        "current_surface_depth1_control",
        "current_surface_route_disabled_published_eval_control",
        "parent_synthetic_gpu_lowrank_bc_control",
        "parent_synthetic_gpu_lowrank_dbb_bc_control",
        "parent_target_diagnostic_bc_control",
        "parent_target_diagnostic_dbb_bc_control",
        "parent_gpu_trained_linear_head_baseline",
        "parent_trained_bitfit_option_bias_baseline",
        "parent_trained_lora_style_hash_delta_baseline",
        "parent_trained_lowrank_adapter_baseline",
        "parent_trained_lora_style_hash_delta_budget_matched_baseline",
        "parent_trained_lowrank_adapter_budget_matched_baseline",
        "parent_retrieval_only_baseline",
        "parent_lexical_only_baseline",
    }

    required_controls_present = sorted(required_control_ids & control_ids) == sorted(required_control_ids)
    mcu_open_input_summary = dict(mcu_open_input_demo.get("summary", {}) or {})
    mcu_open_input_gates = dict(mcu_open_input_summary.get("gates", {}) or {})
    mcu_open_input_ok = bool(mcu_open_input_gates.get("all_pass"))
    mcu_board_info = dict(mcu_open_input_demo.get("board_info", {}) or {})
    mcu_board_consistent = (
        str(mcu_open_input_board_report.get("artifact_sha256") or "")
        == str(mcu_board_info.get("artifact_sha256") or "")
        and str(mcu_open_input_board_report.get("evaluation_mode") or "")
        == str(mcu_board_info.get("evaluation_mode") or "")
    )

    result = {
        "verified": len(missing) == 0
        and len(manifest_mismatches) == 0
        and required_controls_present
        and mcu_open_input_ok
        and mcu_board_consistent
        and len(board_baseline_rows) >= 3
        and bool(cross_task_summary.get("all_published_surfaces_match_parent_ifeval"))
        and bool(independent_second_line_summary.get("independent_above_parent"))
        and bool(independent_second_line_summary.get("independent_above_no_trunk"))
        and bool(independent_second_line_summary.get("independent_above_trained_linear"))
        and bool(independent_second_line_summary.get("independent_above_current_surface"))
        and bool(industrial_second_line_protocol_gates.get("all_pass"))
        and float(industrial_second_line_external_union.get("candidate_accuracy") or 0.0)
        > float(industrial_second_line_external_union.get("current_accuracy") or 0.0)
        and float(industrial_second_line_external_union.get("candidate_accuracy") or 0.0)
        > float(industrial_second_line_external_union.get("parent_accuracy") or 0.0)
        and bool(industrial_probe_summary.get("current_above_parent"))
        and bool(industrial_probe_summary.get("current_above_no_trunk"))
        and bool(industrial_probe_summary.get("current_above_trained_linear"))
        and bool(industrial_protected_summary.get("current_above_parent"))
        and bool(industrial_protected_summary.get("current_above_no_trunk"))
        and bool(industrial_protected_summary.get("current_above_trained_linear")),
        "manifest_mismatches": manifest_mismatches,
        "checks": {
            "current_surface_official_logiqa_match": (
                current_row.get("metrics", {}).get("official_logiqa") == scientific_summary.get("official_logiqa")
            ),
            "current_surface_official_ifeval_match": (
                current_row.get("metrics", {}).get("official_ifeval") == scientific_summary.get("official_ifeval")
            ),
            "block_inventory_trunk_count": block_inventory.get("checkpoint_summary", {}).get("trunk_block_count"),
            "locality_probe_count": len(locality.get("probes", [])),
            "additional_control_count": len(additional_controls.get("controls", [])),
            "required_controls_present": required_controls_present,
            "host_open_input_demo_present": host_open_input_demo_path.exists(),
            "mcu_open_input_demo_present": mcu_open_input_demo_path.exists(),
            "mcu_open_input_gate_all_pass": mcu_open_input_ok,
            "mcu_open_input_exact_match_rate": float(mcu_open_input_summary.get("exact_match_rate") or 0.0),
            "mcu_open_input_board_mode": str(mcu_open_input_board_report.get("evaluation_mode") or ""),
            "mcu_open_input_board_artifact_sha256": str(mcu_open_input_board_report.get("artifact_sha256") or ""),
            "mcu_open_input_board_consistent_with_demo": mcu_board_consistent,
            "board_accuracy": board_accuracy,
            "board_baseline_row_count": len(board_baseline_rows),
            "cross_task_task": str(cross_task_validation.get("task") or ""),
            "cross_task_all_surfaces_match_parent_ifeval": bool(cross_task_summary.get("all_published_surfaces_match_parent_ifeval")),
            "cross_task_max_abs_delta_vs_parent_ifeval": float(cross_task_summary.get("max_abs_delta_vs_parent_ifeval") or 0.0),
            "independent_second_line_task": str(independent_industrial_second_line.get("task") or ""),
            "independent_second_line_samples": int(independent_industrial_second_line.get("taskset", {}).get("samples") or 0),
            "independent_second_line_above_parent": bool(independent_second_line_summary.get("independent_above_parent")),
            "independent_second_line_above_no_trunk": bool(independent_second_line_summary.get("independent_above_no_trunk")),
            "independent_second_line_above_trained_linear": bool(independent_second_line_summary.get("independent_above_trained_linear")),
            "independent_second_line_above_current_surface": bool(independent_second_line_summary.get("independent_above_current_surface")),
            "industrial_second_line_protocol_task": str(industrial_second_line_protocol.get("task") or ""),
            "industrial_second_line_protocol_all_pass": bool(industrial_second_line_protocol_gates.get("all_pass")),
            "industrial_second_line_external_union_samples": int(industrial_second_line_external_union.get("samples") or 0),
            "industrial_second_line_external_union_candidate_accuracy": float(industrial_second_line_external_union.get("candidate_accuracy") or 0.0),
            "industrial_second_line_external_union_current_accuracy": float(industrial_second_line_external_union.get("current_accuracy") or 0.0),
            "industrial_second_line_external_union_parent_accuracy": float(industrial_second_line_external_union.get("parent_accuracy") or 0.0),
            "industrial_probe_task": str(industrial_state_decision_probe.get("task") or ""),
            "industrial_probe_samples": int(industrial_state_decision_probe.get("taskset", {}).get("samples") or 0),
            "industrial_probe_current_above_parent": bool(industrial_probe_summary.get("current_above_parent")),
            "industrial_probe_current_above_no_trunk": bool(industrial_probe_summary.get("current_above_no_trunk")),
            "industrial_probe_current_above_trained_linear": bool(industrial_probe_summary.get("current_above_trained_linear")),
            "industrial_protected_task": str(industrial_wrapper_protected_slice.get("task") or ""),
            "industrial_protected_samples": int(industrial_wrapper_protected_slice.get("taskset", {}).get("samples") or 0),
            "industrial_protected_current_above_parent": bool(industrial_protected_summary.get("current_above_parent")),
            "industrial_protected_current_above_no_trunk": bool(industrial_protected_summary.get("current_above_no_trunk")),
            "industrial_protected_current_above_trained_linear": bool(industrial_protected_summary.get("current_above_trained_linear")),
            "holdout2_accuracy": overfit.get("current_evals", {}).get("holdout2", {}).get("accuracy"),
            "hidden_family_accuracy": hidden_family.get("current_eval", {}).get("accuracy"),
        },
        "required_documents": [
            "docs/INNOVATION.md",
            "docs/FAMILY_AND_ROUTING.md",
            "docs/TRUNK_BLOCKS.md",
            "docs/PROMOTION_CONTRACT.md",
            "docs/EXPERIMENTS.md",
            "docs/OPEN_INPUT_DEMO.md",
            "docs/OPEN_INPUT_ROADMAP.md",
        ],
    }

    print(json.dumps(result, indent=2, ensure_ascii=True))
    if not result["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
