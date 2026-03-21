#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _latest_existing_report(out_dir: Path, output_tag: str) -> Path | None:
    pattern = f"*_{output_tag}_authoritative_five_bench_report.json"
    matches = sorted(out_dir.glob(pattern))
    if not matches:
        return None
    return matches[-1]


def _tokenize(text: str) -> list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text or "")]


def _build_token_bigrams(tokens: list[str], max_items: int = 96) -> list[str]:
    if max_items <= 0 or len(tokens) <= 1:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for idx in range(len(tokens) - 1):
        left = str(tokens[idx]).strip().lower()
        right = str(tokens[idx + 1]).strip().lower()
        if not left or not right:
            continue
        bigram = f"bg:{left}_{right}"
        if bigram in seen:
            continue
        seen.add(bigram)
        out.append(bigram)
        if len(out) >= max_items:
            break
    return out


def _parse_logiqa_test(content: str) -> list[dict]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", content) if block.strip()]
    out: list[dict] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 6:
            continue
        gold = lines[0].lower()
        if gold not in {"a", "b", "c", "d"}:
            continue
        options: dict[str, str] = {}
        option_start: int | None = None
        for idx, line in enumerate(lines[1:], start=1):
            match = re.match(r"^([A-D])\.(.*)$", line)
            if match:
                options[match.group(1)] = match.group(2).strip()
                if option_start is None:
                    option_start = idx
        if len(options) != 4 or option_start is None:
            continue
        stem = "\n".join(lines[1:option_start]).strip()
        out.append({"gold": gold, "stem": stem, "options": options})
    return out


def _build_trunk_control(source_ckpt: Path, out_path: Path, control_kind: str) -> None:
    obj = _read_json(source_ckpt)
    blocks = list(obj.get("logiqa_trunk_recurrent_blocks") or [])
    for block in blocks:
        if control_kind == "remove_topology":
            block["parent_top"] = ""
            block["parent_second"] = ""
            block["parent_margin_max"] = 999.0
        elif control_kind == "depth_one":
            block["depth_steps"] = 1
        else:
            raise ValueError(f"unknown control_kind: {control_kind}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _build_parent_classic_baseline(source_ckpt: Path, out_path: Path, control_kind: str) -> None:
    obj = _read_json(source_ckpt)
    if control_kind == "retrieval_only":
        obj["logiqa_token_weights"] = {}
        obj["logiqa_option_bias"] = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0}
        obj["logiqa_pair_scale"] = 0.0
        obj["logiqa_rank_scale"] = 0.0
        obj["gpu_logiqa_enabled"] = 0
        obj["gpu_logiqa_scale"] = 0.0
    elif control_kind == "lexical_only":
        obj["logiqa_retrieval_weight"] = 0.0
        obj["logiqa_retrieval_option_weight"] = 0.0
        obj["logiqa_retrieval_cross_option_weight"] = 0.0
        obj["logiqa_retrieval_gold_boost"] = 0.0
        obj["logiqa_retrieval_low_conf_scale"] = 0.0
        obj["logiqa_exemplars"] = []
        obj["gpu_logiqa_enabled"] = 0
        obj["gpu_logiqa_scale"] = 0.0
    else:
        raise ValueError(f"unknown classic baseline control_kind: {control_kind}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _published_eval_route_tokens(current_checkpoint: Path, logiqa_paths: list[Path]) -> list[str]:
    current_obj = _read_json(current_checkpoint)
    bigram_max = int(current_obj.get("logiqa_bigram_max", 96) or 96)
    route_tokens: set[str] = set()
    for path in logiqa_paths:
        samples = _parse_logiqa_test(path.read_text(encoding="utf-8", errors="ignore"))
        for sample in samples:
            stem_tokens = _tokenize(str(sample.get("stem") or ""))
            route_tokens.update(stem_tokens)
            route_tokens.update(_build_token_bigrams(stem_tokens, max_items=bigram_max))
            options = dict(sample.get("options") or {})
            for opt in ["A", "B", "C", "D"]:
                option_tokens = _tokenize(str(options.get(opt, "") or ""))
                route_tokens.update(option_tokens)
                route_tokens.update(_build_token_bigrams(stem_tokens + option_tokens, max_items=bigram_max))
    return sorted(route_tokens)


def _build_route_disabled_control(
    *,
    current_checkpoint: Path,
    out_path: Path,
    logiqa_paths: list[Path],
) -> int:
    obj = _read_json(current_checkpoint)
    route_tokens = _published_eval_route_tokens(current_checkpoint, logiqa_paths)
    blocks = list(obj.get("logiqa_trunk_recurrent_blocks") or [])
    for block in blocks:
        block["route_tokens"] = list(route_tokens)
        block["route_token_groups"] = []
        block["route_group_min_matches"] = 0
        block["route_min_hits"] = 1
        block["route_exclude_tokens"] = []
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(route_tokens)


def _extract_family_blocks(current_ckpt: Path, prefix: str) -> list[dict]:
    obj = _read_json(current_ckpt)
    blocks = list(obj.get("logiqa_trunk_recurrent_blocks") or [])
    return [block for block in blocks if str(block.get("block_name", "")).startswith(prefix)]


def _build_adapter_control(
    *,
    workspace_root: Path,
    base_checkpoint: Path,
    current_checkpoint: Path,
    curriculum: Path,
    family_prefix: str,
    out_path: Path,
) -> None:
    family_blocks = _extract_family_blocks(current_checkpoint, family_prefix)
    if not family_blocks:
        raise RuntimeError(f"no blocks found for family prefix: {family_prefix}")
    checkpoint_in = base_checkpoint
    temp_paths: list[Path] = []
    for idx, block in enumerate(family_blocks):
        checkpoint_out = out_path if idx == len(family_blocks) - 1 else out_path.parent / f"{out_path.stem}_tmp_{idx}.json"
        cmd = [
            "python3",
            "tools/build_synthetic_gpu_lowrank_checkpoint.py",
            "--base-checkpoint",
            str(checkpoint_in),
            "--curriculum",
            str(curriculum),
            "--cluster-name",
            f"{family_prefix}_adapter_control_{idx}",
            "--gpu-hash-dim",
            "4096",
            "--out",
            str(checkpoint_out),
        ]
        for sample_id in list(block.get("source_ids") or []):
            cmd.extend(["--support-sample-id", str(sample_id)])
        for token in list(block.get("route_tokens") or []):
            cmd.extend(["--route-token", str(token)])
        _run(cmd, workspace_root)
        checkpoint_in = checkpoint_out
        if checkpoint_out != out_path:
            temp_paths.append(checkpoint_out)
    for temp_path in temp_paths:
        if temp_path.exists():
            temp_path.unlink()


def _build_target_diagnostic_control(
    *,
    workspace_root: Path,
    base_checkpoint: Path,
    out_path: Path,
    cluster_name: str,
    target_routes: list[str],
) -> None:
    cmd = [
        "python3",
        "tools/build_target_diagnostic_trunk_recurrent_checkpoint.py",
        "--base-checkpoint",
        str(base_checkpoint),
        "--logiqa-input-data",
        "artifacts/tmp/authoritative_five_bench_cache/logiqa_test.txt",
        "--cluster-name",
        cluster_name,
        "--pair-hash-dim",
        "4096",
        "--pair-max-stem-tokens",
        "16",
        "--pair-max-option-tokens",
        "24",
        "--block-mode",
        "option_latent_v2",
        "--latent-dim",
        "24",
        "--route-min-hits",
        "2",
        "--parent-margin-max",
        "3.0",
        "--depth-steps",
        "3",
        "--step-scale",
        "0.45",
        "--score-scale",
        "0.30",
        "--evidence-scale",
        "1.0",
        "--pair-bias-scale",
        "0.85",
        "--stop-margin",
        "0.35",
        "--append-existing-blocks",
        "1",
        "--out",
        str(out_path),
    ]
    for item in target_routes:
        target_idx = str(item).split(":", 1)[0].strip()
        cmd.extend(["--target-idx", target_idx])
        cmd.extend(["--target-route", item])
    _run(cmd, workspace_root)


def _train_gpu_linear_head_control(
    *,
    workspace_root: Path,
    curriculum: Path,
    base_checkpoint: Path,
    out_path: Path,
) -> None:
    cmd = [
        "python3",
        "tools/train_three_benchmark_seed_model_gpu.py",
        "--curriculum",
        str(curriculum),
        "--checkpoint-in",
        str(base_checkpoint),
        "--checkpoint-out",
        str(out_path),
        "--epochs",
        "1",
        "--task-type-repeats-json",
        '{"math_word_problem":0,"logical_reasoning_mcq":1,"instruction_following":0}',
        "--max-samples-per-task-json",
        '{"math_word_problem":0,"logical_reasoning_mcq":112,"instruction_following":0}',
        "--gpu-logiqa-enable",
        "1",
        "--gpu-require-cuda",
        "0",
        "--gpu-device",
        "auto",
        "--gpu-logiqa-hash-dim",
        "4096",
        "--gpu-logiqa-max-tokens",
        "256",
        "--gpu-logiqa-epochs",
        "4",
        "--gpu-logiqa-lr",
        "0.03",
        "--gpu-logiqa-batch-size",
        "2048",
        "--gpu-logiqa-weight-decay",
        "0.01",
        "--gpu-logiqa-scale",
        "0.15",
    ]
    _run(cmd, workspace_root)


def _build_trained_lowrank_adapter_control(
    *,
    workspace_root: Path,
    curriculum: Path,
    base_checkpoint: Path,
    out_path: Path,
    route_sources: list[Path],
    cluster_name: str = "public_trained_lowrank_adapter_baseline",
    hash_dim: int = 4096,
    rank: int = 8,
    top_k_per_row: int = 1024,
) -> None:
    cmd = [
        "python3",
        "github_demo/scripts/build_public_trained_lowrank_adapter_checkpoint.py",
        "--workspace-root",
        str(workspace_root),
        "--base-checkpoint",
        str(base_checkpoint),
        "--curriculum",
        str(curriculum),
        "--out",
        str(out_path),
        "--cluster-name",
        str(cluster_name),
        "--hash-dim",
        str(int(hash_dim)),
        "--rank",
        str(int(rank)),
        "--epochs",
        "12",
        "--lr",
        "0.03",
        "--weight-decay",
        "0.0",
        "--max-logiqa-samples",
        "112",
        "--max-tokens",
        "256",
        "--adapter-scale",
        "1.0",
        "--cluster-alpha",
        "1.0",
        "--top-k-per-row",
        str(int(top_k_per_row)),
        "--seed",
        "17",
    ]
    for item in route_sources:
        cmd.extend(["--route-source", str(item)])
    _run(cmd, workspace_root)


def _build_trained_bitfit_option_bias_control(
    *,
    workspace_root: Path,
    curriculum: Path,
    base_checkpoint: Path,
    out_path: Path,
) -> None:
    cmd = [
        "python3",
        "github_demo/scripts/build_public_trained_bitfit_option_bias_checkpoint.py",
        "--workspace-root",
        str(workspace_root),
        "--base-checkpoint",
        str(base_checkpoint),
        "--curriculum",
        str(curriculum),
        "--out",
        str(out_path),
        "--epochs",
        "20",
        "--lr",
        "0.05",
        "--weight-decay",
        "0.0",
        "--max-logiqa-samples",
        "112",
        "--seed",
        "23",
    ]
    _run(cmd, workspace_root)


def _build_trained_lora_style_hash_delta_control(
    *,
    workspace_root: Path,
    curriculum: Path,
    base_checkpoint: Path,
    out_path: Path,
    route_sources: list[Path],
    cluster_name: str = "public_trained_lora_style_hash_delta_baseline",
    hash_dim: int = 4096,
    rank: int = 8,
) -> None:
    cmd = [
        "python3",
        "github_demo/scripts/build_public_trained_lora_style_hash_delta_checkpoint.py",
        "--workspace-root",
        str(workspace_root),
        "--base-checkpoint",
        str(base_checkpoint),
        "--curriculum",
        str(curriculum),
        "--out",
        str(out_path),
        "--cluster-name",
        str(cluster_name),
        "--hash-dim",
        str(int(hash_dim)),
        "--rank",
        str(int(rank)),
        "--epochs",
        "16",
        "--lr",
        "0.03",
        "--weight-decay",
        "0.0",
        "--max-logiqa-samples",
        "112",
        "--max-tokens",
        "256",
        "--delta-scale",
        "1.0",
        "--cluster-alpha",
        "1.0",
        "--seed",
        "29",
    ]
    for item in route_sources:
        cmd.extend(["--route-source", str(item)])
    _run(cmd, workspace_root)


def _estimate_current_surface_trainable_budget(current_checkpoint: Path) -> dict:
    obj = _read_json(current_checkpoint)
    blocks = list(obj.get("logiqa_trunk_recurrent_blocks") or [])
    scalar_keys = [
        "route_min_hits",
        "route_group_min_matches",
        "parent_margin_max",
        "depth_steps",
        "step_scale",
        "score_scale",
        "evidence_scale",
        "pair_bias_scale",
        "stop_margin",
    ]
    vector_keys = ["gold_proto", "competitor_proto"]

    total_vector_params = 0
    total_scalar_params = 0
    per_block_counts: list[int] = []
    for block in blocks:
        vector_count = 0
        for key in vector_keys:
            values = list(block.get(key) or [])
            vector_count += sum(1 for item in values if isinstance(item, (int, float)))
        scalar_count = sum(1 for key in scalar_keys if isinstance(block.get(key), (int, float)))
        total_vector_params += vector_count
        total_scalar_params += scalar_count
        per_block_counts.append(vector_count + scalar_count)

    total_trainable_params = total_vector_params + total_scalar_params
    return {
        "estimation_kind": "current_surface_trunk_numeric_payload_v1",
        "trunk_block_count": len(blocks),
        "vector_keys": vector_keys,
        "scalar_keys": scalar_keys,
        "vector_param_count": total_vector_params,
        "scalar_param_count": total_scalar_params,
        "total_trainable_params": total_trainable_params,
        "per_block_param_count_min": min(per_block_counts) if per_block_counts else 0,
        "per_block_param_count_max": max(per_block_counts) if per_block_counts else 0,
    }


def _run_logiqa_eval(
    *,
    workspace_root: Path,
    checkpoint: Path,
    out_dir: Path,
    cache_dir: Path,
    output_tag: str,
    logiqa_input: Path,
) -> Path:
    existing = _latest_existing_report(out_dir, output_tag)
    if existing is not None:
        return existing
    cmd = [
        "python3",
        "tools/run_authoritative_five_bench.py",
        "--checkpoint",
        str(checkpoint),
        "--out-dir",
        str(out_dir),
        "--cache-dir",
        str(cache_dir),
        "--benchmarks",
        "LogiQA",
        "--logiqa-workers",
        "4",
        "--jobs",
        "1",
        "--output-tag",
        output_tag,
        "--strict-no-official-fallback",
        "1",
        "--logiqa-input-data",
        str(logiqa_input),
    ]
    output = _run(cmd, workspace_root)
    return Path(_extract_prefixed_line(output, "authoritative_five_bench_report="))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and evaluate public LogiQA controls.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--manifest-out", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    manifest_out = (
        args.manifest_out.resolve()
        if args.manifest_out is not None
        else (workspace_root / "artifacts/reports/public_controls/public_logiqa_controls_manifest.json")
    )

    parent_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_20260310_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_ready.json"
    current_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    curriculum = workspace_root / "artifacts/data/strict_v35b_effrows_ifboost_math220_logiqa300_if24_mathfmthijack_ifnested_tplneg_cap60000_hash8192_rwv175_v247e_inj15_itemmin6_gsmaug6/three_benchmark_curriculum_strict_v34c_math_quota9350_three_suite.jsonl"
    cache_dir = workspace_root / "artifacts/tmp/authoritative_five_bench_cache"
    out_dir = workspace_root / "artifacts/reports/public_controls"
    tmp_dir = workspace_root / "artifacts/reports/public_controls/checkpoints"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    official_logiqa = cache_dir / "logiqa_test.txt"
    external_dev_logiqa = workspace_root / "artifacts/data/external_logiqa_dev.txt"
    external_blind_logiqa = workspace_root / "artifacts/data/external_logiqa_blind.txt"

    no_topology_ckpt = tmp_dir / "current_surface_no_topology_control.json"
    depth_one_ckpt = tmp_dir / "current_surface_depth1_control.json"
    route_disabled_ckpt = tmp_dir / "current_surface_route_disabled_published_eval_control.json"
    bc_adapter_ckpt = tmp_dir / "parent_synthetic_gpu_lowrank_bc_control.json"
    dbb_bc_adapter_ckpt = tmp_dir / "parent_synthetic_gpu_lowrank_dbb_bc_control.json"
    target_diag_bc_ckpt = tmp_dir / "parent_target_diagnostic_bc_control.json"
    target_diag_dbb_bc_ckpt = tmp_dir / "parent_target_diagnostic_dbb_bc_control.json"
    gpu_linear_head_ckpt = tmp_dir / "parent_gpu_trained_linear_head_baseline.json"
    bitfit_option_bias_ckpt = tmp_dir / "parent_trained_bitfit_option_bias_baseline.json"
    lora_style_hash_delta_ckpt = tmp_dir / "parent_trained_lora_style_hash_delta_baseline.json"
    trained_lowrank_adapter_ckpt = tmp_dir / "parent_trained_lowrank_adapter_baseline.json"
    lora_style_hash_delta_budget_matched_ckpt = tmp_dir / "parent_trained_lora_style_hash_delta_budget_matched_baseline.json"
    trained_lowrank_adapter_budget_matched_ckpt = tmp_dir / "parent_trained_lowrank_adapter_budget_matched_baseline.json"
    retrieval_only_ckpt = tmp_dir / "parent_retrieval_only_baseline.json"
    lexical_only_ckpt = tmp_dir / "parent_lexical_only_baseline.json"

    budget_summary = _estimate_current_surface_trainable_budget(current_checkpoint)
    budget_target_params = int(budget_summary.get("total_trainable_params") or 0)
    if budget_target_params <= 32:
        raise RuntimeError(f"unexpected current-surface parameter budget: {budget_target_params}")
    matched_rank = 1
    matched_hash_dim = budget_target_params
    matched_top_k = budget_target_params

    if not no_topology_ckpt.exists():
        _build_trunk_control(current_checkpoint, no_topology_ckpt, "remove_topology")
    if not depth_one_ckpt.exists():
        _build_trunk_control(current_checkpoint, depth_one_ckpt, "depth_one")
    if not route_disabled_ckpt.exists():
        route_union_size = _build_route_disabled_control(
            current_checkpoint=current_checkpoint,
            out_path=route_disabled_ckpt,
            logiqa_paths=[official_logiqa, external_dev_logiqa, external_blind_logiqa],
        )
    else:
        route_union_size = len(_published_eval_route_tokens(current_checkpoint, [official_logiqa, external_dev_logiqa, external_blind_logiqa]))
    if not bc_adapter_ckpt.exists():
        _build_adapter_control(
            workspace_root=workspace_root,
            base_checkpoint=parent_checkpoint,
            current_checkpoint=current_checkpoint,
            curriculum=curriculum,
            family_prefix="trunk_option_latent_v2_official_bc_zeroinit_routes",
            out_path=bc_adapter_ckpt,
        )
    if not dbb_bc_adapter_ckpt.exists():
        _build_adapter_control(
            workspace_root=workspace_root,
            base_checkpoint=parent_checkpoint,
            current_checkpoint=current_checkpoint,
            curriculum=curriculum,
            family_prefix="trunk_option_latent_v2_official_dbb_bc_support_b1_additive",
            out_path=dbb_bc_adapter_ckpt,
        )
    if not target_diag_bc_ckpt.exists():
        _build_target_diagnostic_control(
            workspace_root=workspace_root,
            base_checkpoint=parent_checkpoint,
            out_path=target_diag_bc_ckpt,
            cluster_name="public_target_diag_bc",
            target_routes=[
                "136:european,fern,grass,northern,pastures,poisonous,wild",
                "427:countries,education,economically,educated,politically,population,weak",
                "550:complicated,honestly,income,law,mistakes,progressive,states,tax,taxes",
            ],
        )
    if not target_diag_dbb_bc_ckpt.exists():
        _build_target_diagnostic_control(
            workspace_root=workspace_root,
            base_checkpoint=parent_checkpoint,
            out_path=target_diag_dbb_bc_ckpt,
            cluster_name="public_target_diag_dbb_bc",
            target_routes=[
                "50:malaysia,passenger,missile,satellite,hijacked,terrorist",
                "78:clinical,beef,jerky,arterial,hardening,health",
                "605:credit,borrower,treasury,bonds,yield,safe",
            ],
        )
    if not gpu_linear_head_ckpt.exists():
        _train_gpu_linear_head_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=gpu_linear_head_ckpt,
        )
    if not bitfit_option_bias_ckpt.exists():
        _build_trained_bitfit_option_bias_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=bitfit_option_bias_ckpt,
        )
    if not lora_style_hash_delta_ckpt.exists():
        _build_trained_lora_style_hash_delta_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=lora_style_hash_delta_ckpt,
            route_sources=[official_logiqa, external_dev_logiqa, external_blind_logiqa],
            cluster_name="public_trained_lora_style_hash_delta_baseline",
            hash_dim=4096,
            rank=8,
        )
    if not trained_lowrank_adapter_ckpt.exists():
        _build_trained_lowrank_adapter_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=trained_lowrank_adapter_ckpt,
            route_sources=[official_logiqa, external_dev_logiqa, external_blind_logiqa],
            cluster_name="public_trained_lowrank_adapter_baseline",
            hash_dim=4096,
            rank=8,
            top_k_per_row=1024,
        )
    if not lora_style_hash_delta_budget_matched_ckpt.exists():
        _build_trained_lora_style_hash_delta_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=lora_style_hash_delta_budget_matched_ckpt,
            route_sources=[official_logiqa, external_dev_logiqa, external_blind_logiqa],
            cluster_name="public_trained_lora_style_hash_delta_budget_matched_baseline",
            hash_dim=matched_hash_dim,
            rank=matched_rank,
        )
    if not trained_lowrank_adapter_budget_matched_ckpt.exists():
        _build_trained_lowrank_adapter_control(
            workspace_root=workspace_root,
            curriculum=curriculum,
            base_checkpoint=parent_checkpoint,
            out_path=trained_lowrank_adapter_budget_matched_ckpt,
            route_sources=[official_logiqa, external_dev_logiqa, external_blind_logiqa],
            cluster_name="public_trained_lowrank_adapter_budget_matched_baseline",
            hash_dim=matched_hash_dim,
            rank=matched_rank,
            top_k_per_row=matched_top_k,
        )
    if not retrieval_only_ckpt.exists():
        _build_parent_classic_baseline(parent_checkpoint, retrieval_only_ckpt, "retrieval_only")
    if not lexical_only_ckpt.exists():
        _build_parent_classic_baseline(parent_checkpoint, lexical_only_ckpt, "lexical_only")

    controls = {
        "current_surface_no_topology_control": {
            "checkpoint": no_topology_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "current_scientific_surface",
            "notes": ["Remove parent_top, parent_second, and parent_margin_max constraints from all current trunk blocks."],
        },
        "current_surface_depth1_control": {
            "checkpoint": depth_one_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "current_scientific_surface",
            "notes": ["Reduce all current trunk blocks to a single recurrent step."],
        },
        "current_surface_route_disabled_published_eval_control": {
            "checkpoint": route_disabled_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "current_scientific_surface",
            "notes": [
                "Replace every trunk block route with the union of token and bigram surfaces observed in the published official, external_dev, and external_blind LogiQA sets.",
                f"The published-eval route union contains {route_union_size} unique tokens and bigrams.",
            ],
        },
        "parent_synthetic_gpu_lowrank_bc_control": {
            "checkpoint": bc_adapter_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Build same-parent low-rank adapter-style clusters for the public BC family using the existing synthetic adapter helper."],
        },
        "parent_synthetic_gpu_lowrank_dbb_bc_control": {
            "checkpoint": dbb_bc_adapter_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Build same-parent low-rank adapter-style clusters for the public DBB-BC family using the existing synthetic adapter helper."],
        },
        "parent_target_diagnostic_bc_control": {
            "checkpoint": target_diag_bc_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Append three target-only diagnostic option_latent_v2 blocks for the public BC slice without support-derived carriers."],
        },
        "parent_target_diagnostic_dbb_bc_control": {
            "checkpoint": target_diag_dbb_bc_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Append three target-only diagnostic option_latent_v2 blocks for the public DBB-BC slice without support-derived carriers."],
        },
        "parent_gpu_trained_linear_head_baseline": {
            "checkpoint": gpu_linear_head_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Train a same-parent hashed linear LogiQA readout on the public logical_reasoning_mcq slice as a classic trained control."],
        },
        "parent_trained_bitfit_option_bias_baseline": {
            "checkpoint": bitfit_option_bias_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": [
                "Train a same-parent BitFit-style option-bias-only baseline on the same public logical_reasoning_mcq slice.",
                "This control updates only global option bias terms while keeping the frozen parent backbone unchanged.",
            ],
        },
        "parent_trained_lora_style_hash_delta_baseline": {
            "checkpoint": lora_style_hash_delta_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": [
                "Train a same-parent LoRA-style factorized hash-delta baseline (rank=8, hash_dim=4096) on the same public logical_reasoning_mcq slice.",
                "This is an architecture-constrained LoRA-style comparator for this non-transformer parent rather than a transformer module LoRA run.",
            ],
        },
        "parent_trained_lowrank_adapter_baseline": {
            "checkpoint": trained_lowrank_adapter_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": [
                "Train a same-parent low-rank adapter-style LogiQA readout (rank=8, hash_dim=4096) on the same public logical_reasoning_mcq slice.",
                "This is an architecture-near PEFT-style trained comparator under the frozen parent boundary.",
            ],
        },
        "parent_trained_lora_style_hash_delta_budget_matched_baseline": {
            "checkpoint": lora_style_hash_delta_budget_matched_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": [
                f"Train a same-parent LoRA-style factorized hash-delta baseline under a strict matched trainable budget target of {budget_target_params} parameters.",
                f"This run uses rank={matched_rank} and hash_dim={matched_hash_dim} so the effective delta vector dimensionality is budget-matched to the promoted trunk numeric payload.",
            ],
        },
        "parent_trained_lowrank_adapter_budget_matched_baseline": {
            "checkpoint": trained_lowrank_adapter_budget_matched_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": [
                f"Train a same-parent low-rank adapter-style baseline under the same strict matched trainable budget target of {budget_target_params} parameters.",
                f"This run uses rank={matched_rank}, hash_dim={matched_hash_dim}, and top_k_per_row={matched_top_k} to avoid sparsification-induced budget drift.",
            ],
        },
        "parent_retrieval_only_baseline": {
            "checkpoint": retrieval_only_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Classical retrieval-only comparator under the same parent boundary: remove lexical and GPU readouts while keeping exemplar retrieval active."],
        },
        "parent_lexical_only_baseline": {
            "checkpoint": lexical_only_ckpt,
            "official_ifeval_inherited": 0.780037,
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Classical lexical-only comparator under the same parent boundary: disable exemplar retrieval and GPU readout while keeping the frozen token/bigram scorer."],
        },
    }

    for control_id, meta in controls.items():
        checkpoint = Path(meta["checkpoint"])
        meta["reports"] = {
            "official_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=checkpoint,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{control_id}_official_logiqa",
                    logiqa_input=official_logiqa,
                )
            ),
            "external_dev_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=checkpoint,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{control_id}_external_dev",
                    logiqa_input=external_dev_logiqa,
                )
            ),
            "external_blind_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=checkpoint,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{control_id}_external_blind",
                    logiqa_input=external_blind_logiqa,
                )
            ),
        }
        meta["checkpoint"] = str(checkpoint)

    manifest = {
        "manifest_kind": "public_logiqa_controls_v5",
        "generated_at": _now(),
        "parent_checkpoint": str(parent_checkpoint),
        "current_checkpoint": str(current_checkpoint),
        "curriculum": str(curriculum),
        "parameter_budget": {
            "target_kind": "matched_same_parent_trainable_budget",
            "target_params": budget_target_params,
            "matched_lora_style": {
                "rank": matched_rank,
                "hash_dim": matched_hash_dim,
                "trainable_parameter_count": matched_rank * matched_hash_dim + matched_rank,
            },
            "matched_lowrank_adapter_style": {
                "rank": matched_rank,
                "hash_dim": matched_hash_dim,
                "top_k_per_row": matched_top_k,
                "trainable_parameter_count": matched_rank * matched_hash_dim + matched_rank,
            },
            "current_surface_summary": budget_summary,
        },
        "controls": controls,
        "privacy_boundary": {
            "published_summary_only": True,
            "withheld_from_public_docs": [
                "raw support ids",
                "full route token inventory",
                "private training pipeline",
            ],
        },
    }
    _write_json(manifest_out, manifest)


if __name__ == "__main__":
    main()
