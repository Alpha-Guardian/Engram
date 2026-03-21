#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def _report_scores(report: dict) -> dict[str, float]:
    benchmarks = report.get("benchmarks", {})
    ifeval = benchmarks.get("IFEval", {})
    logiqa = benchmarks.get("LogiQA", {})
    return {
        "official_ifeval": float(ifeval.get("strict_prompt_accuracy") or 0.0),
        "official_logiqa": float(logiqa.get("accuracy") or 0.0),
    }


def _logiqa_score(report: dict) -> float:
    return float(report.get("benchmarks", {}).get("LogiQA", {}).get("accuracy") or 0.0)


def _source_entry(path: Path, workspace_root: Path) -> dict[str, str]:
    return {"path": _rel(path, workspace_root), "sha256": _sha256(path)}


def _normalize_path_text(path_text: str, workspace_root: Path) -> str:
    raw = str(path_text or "").strip().replace("\\", "/")
    if not raw:
        return ""
    path_obj = Path(raw)
    if path_obj.is_absolute():
        try:
            return str(path_obj.resolve().relative_to(workspace_root.resolve())).replace("\\", "/")
        except ValueError:
            return str(path_obj).replace("\\", "/")
    return raw


def _parent_status_fallback_from_existing_main_table(repo_root: Path) -> dict:
    existing_main_table_path = repo_root / "results/experiments/main_table.json"
    existing_main_table = _read_json(existing_main_table_path)
    rows = list(existing_main_table.get("rows", []) or [])
    frozen_row = next((row for row in rows if row.get("surface_id") == "frozen_authoritative_parent"), None)
    if not isinstance(frozen_row, dict):
        raise FileNotFoundError("missing frozen_authoritative_parent row for fallback")
    metrics = dict(frozen_row.get("metrics", {}) or {})
    checkpoint = dict(frozen_row.get("checkpoint", {}) or {})
    sources = dict(frozen_row.get("sources", {}) or {})
    return {
        "official_clean": {
            "ifeval": float(metrics.get("official_ifeval") or 0.0),
            "logiqa": float(metrics.get("official_logiqa") or 0.0),
        },
        "external_dev": {
            "logiqa": float(metrics.get("external_dev_logiqa") or 0.0),
        },
        "external_blind": {
            "logiqa": float(metrics.get("external_blind_logiqa") or 0.0),
        },
        "candidate_checkpoint": str(checkpoint.get("path") or ""),
        "candidate_checkpoint_sha256": str(checkpoint.get("sha256") or ""),
        "source_official_report": str(dict(sources.get("official", {}) or {}).get("path") or ""),
        "source_external_dev_report": str(dict(sources.get("external_dev", {}) or {}).get("path") or ""),
        "source_external_blind_report": str(dict(sources.get("external_blind", {}) or {}).get("path") or ""),
    }


def _surface_row(
    *,
    surface_id: str,
    label: str,
    family_scope: str,
    official_ifeval: float,
    official_logiqa: float,
    external_dev_logiqa: float,
    external_blind_logiqa: float,
    checkpoint_path: str,
    checkpoint_sha256: str,
    official_source: Path,
    external_dev_source: Path,
    external_blind_source: Path,
    workspace_root: Path,
    notes: list[str],
) -> dict:
    return {
        "surface_id": surface_id,
        "label": label,
        "family_scope": family_scope,
        "metrics": {
            "official_ifeval": round(official_ifeval, 6),
            "official_logiqa": round(official_logiqa, 6),
            "external_dev_logiqa": round(external_dev_logiqa, 6),
            "external_blind_logiqa": round(external_blind_logiqa, 6),
        },
        "checkpoint": {
            "path": _normalize_path_text(checkpoint_path, workspace_root),
            "sha256": checkpoint_sha256,
        },
        "sources": {
            "official": _source_entry(official_source, workspace_root),
            "external_dev": _source_entry(external_dev_source, workspace_root),
            "external_blind": _source_entry(external_blind_source, workspace_root),
        },
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build public-safe experiment summary tables.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Workspace root containing artifacts/. Defaults to the parent of github_demo.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated JSON outputs. Defaults to github_demo/results/experiments.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    output_dir = (args.output_dir or (repo_root / "results/experiments")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    open_input_output_dir = (repo_root / "results/open_input_demo").resolve()
    open_input_output_dir.mkdir(parents=True, exist_ok=True)

    parent_status_path = workspace_root / "artifacts/reports/focused_followup/20260310_v247r_freeze_currentenv_reference_status.json"
    current_official_path = workspace_root / "artifacts/reports/colm2026/20260320_000913_056137_colm2026_current_official_dualbench_authoritative_five_bench_report.json"
    current_external_dev_path = workspace_root / "artifacts/reports/colm2026/20260320_000913_044103_colm2026_current_external_dev_authoritative_five_bench_report.json"
    current_external_blind_path = workspace_root / "artifacts/reports/colm2026/20260320_000913_049843_colm2026_current_external_blind_authoritative_five_bench_report.json"
    no_trunk_official_path = workspace_root / "artifacts/reports/colm2026/20260320_001501_785418_colm2026_current_no_trunk_official_dualbench_authoritative_five_bench_report.json"
    no_trunk_external_dev_path = workspace_root / "artifacts/reports/colm2026/20260320_001501_807161_colm2026_current_no_trunk_external_dev_authoritative_five_bench_report.json"
    no_trunk_external_blind_path = workspace_root / "artifacts/reports/colm2026/20260320_001502_026264_colm2026_current_no_trunk_external_blind_authoritative_five_bench_report.json"
    three_family_official_path = workspace_root / "artifacts/reports/focused_followup/20260314_043958_388350_20260314_trunk_option_latent_v2_three_family_combined_postopt_official_dualbench_authoritative_five_bench_report.json"
    three_family_external_dev_path = workspace_root / "artifacts/reports/focused_followup/20260314_043958_424101_20260314_trunk_option_latent_v2_three_family_combined_postopt_external_dev_authoritative_five_bench_report.json"
    three_family_external_blind_path = workspace_root / "artifacts/reports/focused_followup/20260314_043958_431485_20260314_trunk_option_latent_v2_three_family_combined_postopt_external_blind_authoritative_five_bench_report.json"
    bc_official_path = workspace_root / "artifacts/reports/focused_followup/20260315_083940_973363_20260315_trunk_option_latent_v2_official_bc_support_b1_dualbench_authoritative_five_bench_report.json"
    bc_external_dev_path = workspace_root / "artifacts/reports/focused_followup/20260315_083940_947874_20260315_trunk_option_latent_v2_official_bc_support_b1_external_dev_authoritative_five_bench_report.json"
    bc_external_blind_path = workspace_root / "artifacts/reports/focused_followup/20260315_083946_825637_20260315_trunk_option_latent_v2_official_bc_support_b1_external_blind_authoritative_five_bench_report.json"
    dbb_bc_official_path = workspace_root / "artifacts/reports/focused_followup/20260315_101307_351353_20260315_trunk_option_latent_v2_official_dbb_bc_support_b1_dualbench_authoritative_five_bench_report.json"
    dbb_bc_external_dev_path = workspace_root / "artifacts/reports/focused_followup/20260315_101313_619228_20260315_trunk_option_latent_v2_official_dbb_bc_support_b1_external_dev_authoritative_five_bench_report.json"
    dbb_bc_external_blind_path = workspace_root / "artifacts/reports/focused_followup/20260315_101307_296894_20260315_trunk_option_latent_v2_official_dbb_bc_support_b1_external_blind_authoritative_five_bench_report.json"
    paired_stats_path = workspace_root / "artifacts/reports/colm2026/paired_replay_stats.json"
    public_controls_manifest_path = workspace_root / "artifacts/reports/public_controls/public_logiqa_controls_manifest.json"
    public_causal_sequence_manifest_path = workspace_root / "artifacts/reports/public_controls/public_causal_sequence_manifest.json"
    public_open_input_manifest_path = workspace_root / "artifacts/reports/public_controls/public_open_input_demo_manifest.json"

    locality_paths = [
        workspace_root / "artifacts/reports/colm2026/current_surface_official_ad_support_b1_additive_narrow_locality_probe_vs_authoritative_parent.json",
        workspace_root / "artifacts/reports/colm2026/current_surface_official_ad_support_b1_additive_locality_probe_vs_authoritative_parent.json",
        workspace_root / "artifacts/reports/colm2026/current_surface_official_bc_zeroinit_routes_narrow_locality_probe_vs_authoritative_parent.json",
        workspace_root / "artifacts/reports/colm2026/current_surface_official_bc_zeroinit_routes_locality_probe_vs_authoritative_parent.json",
        workspace_root / "artifacts/reports/colm2026/current_surface_official_dbb_bc_support_b1_additive_narrow_locality_probe_vs_authoritative_parent.json",
        workspace_root / "artifacts/reports/colm2026/current_surface_official_dbb_bc_support_b1_additive_locality_probe_vs_authoritative_parent.json",
    ]

    if parent_status_path.exists():
        parent_status = _read_json(parent_status_path)
    else:
        parent_status = _parent_status_fallback_from_existing_main_table(repo_root)
    current_official = _read_json(current_official_path)
    current_external_dev = _read_json(current_external_dev_path)
    current_external_blind = _read_json(current_external_blind_path)
    no_trunk_official = _read_json(no_trunk_official_path)
    no_trunk_external_dev = _read_json(no_trunk_external_dev_path)
    no_trunk_external_blind = _read_json(no_trunk_external_blind_path)
    three_family_official = _read_json(three_family_official_path)
    three_family_external_dev = _read_json(three_family_external_dev_path)
    three_family_external_blind = _read_json(three_family_external_blind_path)
    bc_official = _read_json(bc_official_path)
    bc_external_dev = _read_json(bc_external_dev_path)
    bc_external_blind = _read_json(bc_external_blind_path)
    dbb_bc_official = _read_json(dbb_bc_official_path)
    dbb_bc_external_dev = _read_json(dbb_bc_external_dev_path)
    dbb_bc_external_blind = _read_json(dbb_bc_external_blind_path)
    paired_stats = _read_json(paired_stats_path)

    current_scores = _report_scores(current_official)
    no_trunk_scores = _report_scores(no_trunk_official)
    three_family_scores = _report_scores(three_family_official)
    bc_scores = _report_scores(bc_official)
    dbb_bc_scores = _report_scores(dbb_bc_official)

    rows = [
        _surface_row(
            surface_id="frozen_authoritative_parent",
            label="Frozen authoritative parent",
            family_scope="authoritative_parent",
            official_ifeval=float(parent_status["official_clean"]["ifeval"]),
            official_logiqa=float(parent_status["official_clean"]["logiqa"]),
            external_dev_logiqa=float(parent_status["external_dev"]["logiqa"]),
            external_blind_logiqa=float(parent_status["external_blind"]["logiqa"]),
            checkpoint_path=str(parent_status["candidate_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(parent_status["candidate_checkpoint_sha256"]),
            official_source=workspace_root / str(parent_status["source_official_report"]).replace("\\", "/"),
            external_dev_source=workspace_root / str(parent_status["source_external_dev_report"]).replace("\\", "/"),
            external_blind_source=workspace_root / str(parent_status["source_external_blind_report"]).replace("\\", "/"),
            workspace_root=workspace_root,
            notes=[
                "This is the frozen authoritative comparison boundary.",
                "Same-parent trained linear, BitFit-style, LoRA-style, low-rank adapter-style, and trainable-budget-matched PEFT controls are published separately.",
            ],
        ),
        _surface_row(
            surface_id="current_no_trunk_ablation",
            label="Current no-trunk ablation",
            family_scope="exact_ablation",
            official_ifeval=no_trunk_scores["official_ifeval"],
            official_logiqa=no_trunk_scores["official_logiqa"],
            external_dev_logiqa=_logiqa_score(no_trunk_external_dev),
            external_blind_logiqa=_logiqa_score(no_trunk_external_blind),
            checkpoint_path=str(no_trunk_official["model_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(no_trunk_official["checkpoint_sha256"]),
            official_source=no_trunk_official_path,
            external_dev_source=no_trunk_external_dev_path,
            external_blind_source=no_trunk_external_blind_path,
            workspace_root=workspace_root,
            notes=[
                "Exact ablation of the current checkpoint with promoted trunk blocks removed.",
                "On matched replays this collapses back to the frozen authoritative parent.",
            ],
        ),
        _surface_row(
            surface_id="three_family_promoted_surface",
            label="Earlier three-family promoted surface",
            family_scope="same_parent_context",
            official_ifeval=three_family_scores["official_ifeval"],
            official_logiqa=three_family_scores["official_logiqa"],
            external_dev_logiqa=_logiqa_score(three_family_external_dev),
            external_blind_logiqa=_logiqa_score(three_family_external_blind),
            checkpoint_path=str(three_family_official["model_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(three_family_official["checkpoint_sha256"]),
            official_source=three_family_official_path,
            external_dev_source=three_family_external_dev_path,
            external_blind_source=three_family_external_blind_path,
            workspace_root=workspace_root,
            notes=[
                "Replayable earlier promoted surface under the same parent boundary.",
                "Useful as context, not a substitute for external classic baselines.",
            ],
        ),
        _surface_row(
            surface_id="single_family_official_bc_support_b1",
            label="Single-family official BC surface",
            family_scope="same_parent_context",
            official_ifeval=bc_scores["official_ifeval"],
            official_logiqa=bc_scores["official_logiqa"],
            external_dev_logiqa=_logiqa_score(bc_external_dev),
            external_blind_logiqa=_logiqa_score(bc_external_blind),
            checkpoint_path=str(bc_official["model_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(bc_official["checkpoint_sha256"]),
            official_source=bc_official_path,
            external_dev_source=bc_external_dev_path,
            external_blind_source=bc_external_blind_path,
            workspace_root=workspace_root,
            notes=[
                "Replayable one-family slice under the same frozen parent.",
            ],
        ),
        _surface_row(
            surface_id="single_family_official_dbb_bc_support_b1",
            label="Single-family official DBB-BC surface",
            family_scope="same_parent_context",
            official_ifeval=dbb_bc_scores["official_ifeval"],
            official_logiqa=dbb_bc_scores["official_logiqa"],
            external_dev_logiqa=_logiqa_score(dbb_bc_external_dev),
            external_blind_logiqa=_logiqa_score(dbb_bc_external_blind),
            checkpoint_path=str(dbb_bc_official["model_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(dbb_bc_official["checkpoint_sha256"]),
            official_source=dbb_bc_official_path,
            external_dev_source=dbb_bc_external_dev_path,
            external_blind_source=dbb_bc_external_blind_path,
            workspace_root=workspace_root,
            notes=[
                "Replayable one-family slice under the same frozen parent.",
            ],
        ),
        _surface_row(
            surface_id="current_scientific_surface",
            label="Current promoted scientific surface",
            family_scope="current_surface",
            official_ifeval=current_scores["official_ifeval"],
            official_logiqa=current_scores["official_logiqa"],
            external_dev_logiqa=_logiqa_score(current_external_dev),
            external_blind_logiqa=_logiqa_score(current_external_blind),
            checkpoint_path=str(current_official["model_checkpoint"]).replace("\\", "/"),
            checkpoint_sha256=str(current_official["checkpoint_sha256"]),
            official_source=current_official_path,
            external_dev_source=current_external_dev_path,
            external_blind_source=current_external_blind_path,
            workspace_root=workspace_root,
            notes=[
                "Current public host-side promoted surface.",
                "Published as a research surface, not as a commercial freeze replacement.",
            ],
        ),
    ]

    parent_logiqa = rows[0]["metrics"]["official_logiqa"]
    for row in rows:
        row["metrics"]["delta_vs_parent_logiqa"] = round(row["metrics"]["official_logiqa"] - parent_logiqa, 6)

    main_table = {
        "table_kind": "public_main_table_v1",
        "generated_at": _now(),
        "rows": rows,
        "notes": [
            "The authoritative comparison boundary in the public bundle is frozen parent versus current promoted surface.",
            "The no-trunk ablation is the exact post-hoc localization control currently published.",
            "Same-parent family slices provide context but do not substitute for the stricter comparator bundle in additional_controls.json.",
        ],
    }

    parent_ifeval = rows[0]["metrics"]["official_ifeval"]
    cross_task_validation = {
        "bundle_kind": "public_cross_task_validation_v1",
        "generated_at": _now(),
        "task": "IFEval",
        "metric": "strict_prompt_accuracy",
        "rows": [
            {
                "surface_id": row["surface_id"],
                "label": row["label"],
                "official_ifeval": row["metrics"]["official_ifeval"],
                "delta_vs_parent_ifeval": round(row["metrics"]["official_ifeval"] - parent_ifeval, 6),
                "official_logiqa": row["metrics"]["official_logiqa"],
            }
            for row in rows
        ],
        "summary": {
            "parent_ifeval": parent_ifeval,
            "current_ifeval": rows[-1]["metrics"]["official_ifeval"],
            "max_abs_delta_vs_parent_ifeval": max(
                abs(float(row["metrics"]["official_ifeval"]) - float(parent_ifeval)) for row in rows
            ),
            "all_published_surfaces_match_parent_ifeval": all(
                float(row["metrics"]["official_ifeval"]) == float(parent_ifeval) for row in rows
            ),
        },
        "notes": [
            "This bundle is a second-task non-regression check on the public authoritative IFEval path.",
            "It shows that the published same-parent progression keeps the parent IFEval score while LogiQA changes.",
            "It does not establish positive transfer or broad multi-task capability gains beyond the published boundary.",
        ],
    }

    baselines = {
        "baseline_bundle_kind": "public_baselines_v1",
        "generated_at": _now(),
        "authoritative_comparison": [
            row for row in rows if row["surface_id"] in {"frozen_authoritative_parent", "current_no_trunk_ablation", "current_scientific_surface"}
        ],
        "same_parent_context": [
            row for row in rows if row["family_scope"] == "same_parent_context"
        ],
        "comparator_coverage": {
            "matched_same_parent_classic_peft_baselines": "published_trainable_budget_matched_controls",
            "same_parent_classic_comparator_bundle": "published_in_additional_controls",
            "architecture_near_adapter_controls": "published_in_additional_controls",
            "target_only_diagnostic_controls": "published_in_additional_controls",
            "public_claim_boundary": "No blanket dominance claim over all nearby PEFT or local-editing methods; the published same-parent comparator bundle now includes retrieval-only, lexical-only, trained linear-readout, trained BitFit-style option-bias, trained LoRA-style factorized hash-delta, trained low-rank adapter-style controls, and trainable-budget-matched LoRA-style and adapter-style controls under the same frozen parent.",
        },
    }

    ablations = {
        "ablation_bundle_kind": "public_ablations_v1",
        "generated_at": _now(),
        "exact_no_trunk_ablation": {
            "ablation_surface_id": "current_no_trunk_ablation",
            "parent_equivalence": {
                "official_ifeval_match": rows[1]["metrics"]["official_ifeval"] == rows[0]["metrics"]["official_ifeval"],
                "official_logiqa_match": rows[1]["metrics"]["official_logiqa"] == rows[0]["metrics"]["official_logiqa"],
                "external_dev_match": rows[1]["metrics"]["external_dev_logiqa"] == rows[0]["metrics"]["external_dev_logiqa"],
                "external_blind_match": rows[1]["metrics"]["external_blind_logiqa"] == rows[0]["metrics"]["external_blind_logiqa"],
            },
            "current_vs_no_trunk_delta": {
                "official_logiqa": round(rows[-1]["metrics"]["official_logiqa"] - rows[1]["metrics"]["official_logiqa"], 6),
                "external_dev_logiqa": round(rows[-1]["metrics"]["external_dev_logiqa"] - rows[1]["metrics"]["external_dev_logiqa"], 6),
                "external_blind_logiqa": round(rows[-1]["metrics"]["external_blind_logiqa"] - rows[1]["metrics"]["external_blind_logiqa"], 6),
            },
            "paired_replay_stats": paired_stats,
            "source_paths": {
                "paired_replay_stats": _source_entry(paired_stats_path, workspace_root),
                "current_official": _source_entry(current_official_path, workspace_root),
                "no_trunk_official": _source_entry(no_trunk_official_path, workspace_root),
                "current_external_dev": _source_entry(current_external_dev_path, workspace_root),
                "no_trunk_external_dev": _source_entry(no_trunk_external_dev_path, workspace_root),
                "current_external_blind": _source_entry(current_external_blind_path, workspace_root),
                "no_trunk_external_blind": _source_entry(no_trunk_external_blind_path, workspace_root),
            },
        "notes": [
            "The current public bundle exposes one exact causal localization control: remove the promoted trunk blocks and replay the same evaluation pipeline.",
            "Additional topology-removal, route-disabled, target-only diagnostic, same-parent trained linear, BitFit-style, LoRA-style hash-delta, low-rank adapter-style, and trainable-budget-matched PEFT controls are published separately in additional_controls.json.",
        ],
    }
    }

    causal_sequence = {
        "sequence_kind": "public_same_parent_progression_v1",
        "generated_at": _now(),
        "rows": [
            {
                "surface_id": row["surface_id"],
                "label": row["label"],
                "official_logiqa": row["metrics"]["official_logiqa"],
                "delta_vs_parent_logiqa": row["metrics"]["delta_vs_parent_logiqa"],
                "external_dev_logiqa": row["metrics"]["external_dev_logiqa"],
                "external_blind_logiqa": row["metrics"]["external_blind_logiqa"],
                "family_scope": row["family_scope"],
            }
            for row in rows
        ],
        "notes": [
            "This is a replayable same-parent progression, not a full ordered construction trace over all 75 current-surface blocks.",
            "It is intended to show public context: frozen parent, exact no-trunk proxy, earlier promoted surfaces, and the current promoted surface.",
        ],
    }
    if public_causal_sequence_manifest_path.exists():
        causal_manifest = _read_json(public_causal_sequence_manifest_path)
        causal_variants = []
        for variant_id, meta in dict(causal_manifest.get("variants", {}) or {}).items():
            official_report_path = workspace_root / str(meta["reports"]["official_logiqa"])
            external_dev_report_path = workspace_root / str(meta["reports"]["external_dev_logiqa"])
            external_blind_report_path = workspace_root / str(meta["reports"]["external_blind_logiqa"])
            official_report = _read_json(official_report_path)
            external_dev_report = _read_json(external_dev_report_path)
            external_blind_report = _read_json(external_blind_report_path)
            causal_variants.append(
                {
                    "variant_id": variant_id,
                    "kind": str(meta.get("kind") or ""),
                    "source_surface": str(meta.get("source_surface") or ""),
                    "family_order": list(meta.get("family_order") or []),
                    "removed_families": list(meta.get("removed_families") or []),
                    "metrics": {
                        "official_logiqa": _logiqa_score(official_report),
                        "external_dev_logiqa": _logiqa_score(external_dev_report),
                        "external_blind_logiqa": _logiqa_score(external_blind_report),
                        "delta_vs_parent_logiqa": round(_logiqa_score(official_report) - parent_logiqa, 6),
                        "delta_vs_current_logiqa": round(_logiqa_score(official_report) - rows[-1]["metrics"]["official_logiqa"], 6),
                    },
                    "checkpoint": {
                        "path": _normalize_path_text(str(meta["checkpoint"]), workspace_root),
                        "sha256": _sha256(workspace_root / str(meta["checkpoint"]).replace("\\", "/")),
                    },
                    "sources": {
                        "official_logiqa": _source_entry(official_report_path, workspace_root),
                        "external_dev_logiqa": _source_entry(external_dev_report_path, workspace_root),
                        "external_blind_logiqa": _source_entry(external_blind_report_path, workspace_root),
                    },
                    "notes": list(meta.get("notes") or []),
                }
            )
        causal_sequence = {
            "sequence_kind": "public_causal_sequence_v2",
            "generated_at": _now(),
            "families": list(causal_manifest.get("families") or []),
            "reference_surfaces": [
                row for row in rows if row["surface_id"] in {"frozen_authoritative_parent", "current_scientific_surface"}
            ],
            "variants": causal_variants,
            "notes": [
                "This bundle publishes three-family forward addition, order-swap, and reverse-removal experiments using public BC, DBB-BC, and AD families.",
                "Forward additions start from the frozen parent; reverse removals start from the current surface.",
            ],
        }

    locality_entries = []
    for path in locality_paths:
        report = _read_json(path)
        summary = report.get("summary", {})
        locality_entries.append(
            {
                "probe_id": path.stem,
                "family": report.get("block_name_prefix"),
                "scope": "narrow" if "narrow" in path.name else "protected_slice",
                "target_indices": list(report.get("target_indices") or []),
                "summary": {
                    "selected_count": int(summary.get("selected_count") or 0),
                    "triggered_count": int(summary.get("triggered_count") or 0),
                    "locality_target_fixed_count": int(summary.get("locality_target_fixed_count") or 0),
                    "off_target_fire_count": int(summary.get("off_target_fire_count") or 0),
                    "locality_collateral_flip_count": int(summary.get("locality_collateral_flip_count") or 0),
                    "changed_prediction_count": int(summary.get("changed_prediction_count") or 0),
                },
                "source": _source_entry(path, workspace_root),
            }
        )

    locality_probes = {
        "probe_bundle_kind": "public_locality_probes_v1",
        "generated_at": _now(),
        "probes": locality_entries,
        "representative_probes": [
            "current_surface_official_bc_zeroinit_routes_narrow_locality_probe_vs_authoritative_parent",
            "current_surface_official_dbb_bc_support_b1_additive_narrow_locality_probe_vs_authoritative_parent",
            "current_surface_official_bc_zeroinit_routes_locality_probe_vs_authoritative_parent",
            "current_surface_official_dbb_bc_support_b1_additive_locality_probe_vs_authoritative_parent",
        ],
        "notes": [
            "The tightest representative public locality evidence is the BC and DBB-BC pair: both narrow and protected-slice probes show 3 designated targets fixed, zero off-target fires, and zero collateral flips.",
            "The wider AD family is also published here; its protected-slice probe shows broader off-target firing while still reporting zero locality collateral flips on the selected slice.",
        ],
    }

    additional_controls = {
        "controls_bundle_kind": "public_additional_controls_v1",
        "generated_at": _now(),
        "controls": [],
        "notes": [
            "These are additional LogiQA-local controls beyond the exact no-trunk ablation.",
            "The adapter-style controls are same-parent low-rank controls; the bundle now also includes trainable-budget-matched PEFT-style controls.",
            "The topology-removal, depth-one, and published-eval route-disabled controls are current-surface checkpoint edits, not new trained surfaces.",
            "The target-only diagnostic controls keep parent topology but replace support-derived carriers with target-derived blocks only.",
            "The public classical comparator bundle includes retrieval-only, lexical-only, trained linear-readout, trained BitFit-style option-bias, trained LoRA-style factorized hash-delta, trained low-rank adapter-style controls, and trainable-budget-matched LoRA-style and adapter-style controls under the same frozen parent boundary.",
        ],
    }
    if public_controls_manifest_path.exists():
        controls_manifest = _read_json(public_controls_manifest_path)
        control_order = [
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
        ]
        controls_by_id = dict(controls_manifest.get("controls", {}))
        ordered_ids = [control_id for control_id in control_order if control_id in controls_by_id]
        ordered_ids.extend(sorted(control_id for control_id in controls_by_id if control_id not in control_order))
        for control_id in ordered_ids:
            meta = controls_by_id[control_id]
            official_report_path = workspace_root / str(meta["reports"]["official_logiqa"])
            external_dev_report_path = workspace_root / str(meta["reports"]["external_dev_logiqa"])
            external_blind_report_path = workspace_root / str(meta["reports"]["external_blind_logiqa"])
            official_report = _read_json(official_report_path)
            external_dev_report = _read_json(external_dev_report_path)
            external_blind_report = _read_json(external_blind_report_path)
            row = {
                "control_id": control_id,
                "source_surface": str(meta.get("source_surface") or ""),
                "metrics": {
                    "official_ifeval_inherited": float(meta.get("official_ifeval_inherited") or 0.0),
                    "official_logiqa": _logiqa_score(official_report),
                    "external_dev_logiqa": _logiqa_score(external_dev_report),
                    "external_blind_logiqa": _logiqa_score(external_blind_report),
                    "delta_vs_parent_logiqa": round(_logiqa_score(official_report) - parent_logiqa, 6),
                    "delta_vs_current_logiqa": round(_logiqa_score(official_report) - rows[-1]["metrics"]["official_logiqa"], 6),
                },
                "checkpoint": {
                    "path": _normalize_path_text(str(meta["checkpoint"]), workspace_root),
                    "sha256": _sha256(workspace_root / str(meta["checkpoint"]).replace("\\", "/")),
                },
                "sources": {
                    "official_logiqa": _source_entry(official_report_path, workspace_root),
                    "external_dev_logiqa": _source_entry(external_dev_report_path, workspace_root),
                    "external_blind_logiqa": _source_entry(external_blind_report_path, workspace_root),
                },
                "notes": list(meta.get("notes") or []),
            }
            additional_controls["controls"].append(row)

    open_input_summary = None
    host_open_input_existing_path = open_input_output_dir / "host_open_input_demo.json"
    if public_open_input_manifest_path.exists():
        open_input_manifest = _read_json(public_open_input_manifest_path)
        structured_report_path = workspace_root / str(open_input_manifest.get("structured_report") or "")
        edge_report_path = workspace_root / str(open_input_manifest.get("edge_runtime_report") or "")
        structured_report = _read_json(structured_report_path)
        edge_report = _read_json(edge_report_path)
        open_input_summary = {
            "bundle_kind": "public_open_input_demo_v1",
            "generated_at": _now(),
            "checkpoint": _normalize_path_text(str(open_input_manifest.get("checkpoint") or ""), workspace_root),
            "taskset": _normalize_path_text(str(open_input_manifest.get("taskset") or ""), workspace_root),
            "structured_exec": {
                "summary": dict(structured_report.get("summary", {}) or {}),
                "source": _source_entry(structured_report_path, workspace_root),
            },
            "edge_runtime": {
                "summary": dict(edge_report.get("summary", {}) or {}),
                "source": _source_entry(edge_report_path, workspace_root),
            },
            "claim_boundary": dict(open_input_manifest.get("claim_boundary", {}) or {}),
            "notes": [
                "This is a host-side open-input structured loop, separate from the fixed-batch ESP32-C3 board proof.",
                "The taskset covers tool calls, state transitions, runtime config emission, route decisions, and unsafe guard denials.",
            ],
        }
    elif host_open_input_existing_path.exists():
        existing_summary = _read_json(host_open_input_existing_path)
        open_input_summary = dict(existing_summary)
        open_input_summary["checkpoint"] = _normalize_path_text(
            str(existing_summary.get("checkpoint") or ""), workspace_root
        )
        open_input_summary["taskset"] = _normalize_path_text(str(existing_summary.get("taskset") or ""), workspace_root)

    files_to_write = {
        "main_table.json": main_table,
        "cross_task_validation.json": cross_task_validation,
        "baselines.json": baselines,
        "ablations.json": ablations,
        "causal_sequence.json": causal_sequence,
        "locality_probes.json": locality_probes,
        "additional_controls.json": additional_controls,
    }

    for name, payload in files_to_write.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if open_input_summary is not None:
        (open_input_output_dir / "host_open_input_demo.json").write_text(
            json.dumps(open_input_summary, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    source_files = {
        path.resolve()
        for path in [
            parent_status_path,
            current_official_path,
            current_external_dev_path,
            current_external_blind_path,
            no_trunk_official_path,
            no_trunk_external_dev_path,
            no_trunk_external_blind_path,
            three_family_official_path,
            three_family_external_dev_path,
            three_family_external_blind_path,
            bc_official_path,
            bc_external_dev_path,
            bc_external_blind_path,
            dbb_bc_official_path,
            dbb_bc_external_dev_path,
            dbb_bc_external_blind_path,
            paired_stats_path,
            *locality_paths,
            public_controls_manifest_path,
            public_causal_sequence_manifest_path,
            public_open_input_manifest_path,
        ]
        if path.exists()
    }

    generated_files = []
    for path in sorted(output_dir.glob("*.json")):
        if path.name == "manifest.json":
            continue
        generated_files.append({"path": str(path.relative_to(repo_root)), "sha256": _sha256(path)})
    for path in sorted(open_input_output_dir.glob("*.json")):
        generated_files.append({"path": str(path.relative_to(repo_root)), "sha256": _sha256(path)})

    manifest = {
        "manifest_kind": "public_experiment_bundle_manifest_v1",
        "generated_at": _now(),
        "generated_files": generated_files,
        "source_files": [
            {"path": _rel(path, workspace_root), "sha256": _sha256(path)} for path in sorted(source_files)
        ],
        "privacy_boundary": {
                "published": [
                    "accepted surface summaries",
                    "same-parent replayable comparison rows",
                    "exact no-trunk ablation",
                    "representative locality probes",
                    "paired replay statistics",
                    "host-side open-input structured demo summary",
                    "board-side narrow MCU open-input micro-loop summary",
                ],
            "withheld": [
                "full family-mining trace",
                "rejected candidate frontier",
                "support-source graph",
                "full route token inventory",
                "proto vectors and private training pipeline",
            ],
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
