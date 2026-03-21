#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _run_logiqa_eval(
    *,
    workspace_root: Path,
    checkpoint: Path,
    out_dir: Path,
    cache_dir: Path,
    output_tag: str,
    logiqa_input: Path,
) -> Path:
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


def _family_blocks(current_obj: dict, prefixes: dict[str, str]) -> dict[str, list[dict]]:
    blocks = list(current_obj.get("logiqa_trunk_recurrent_blocks") or [])
    out: dict[str, list[dict]] = {family_id: [] for family_id in prefixes}
    for block in blocks:
        name = str(block.get("block_name", "") or "")
        for family_id, prefix in prefixes.items():
            if name.startswith(prefix):
                out[family_id].append(copy.deepcopy(block))
                break
    missing = [family_id for family_id, family_blocks in out.items() if not family_blocks]
    if missing:
        raise RuntimeError(f"missing family blocks for ids: {missing}")
    return out


def _ordered_blocks(blocks_by_family: dict[str, list[dict]], family_order: list[str]) -> list[dict]:
    ordered: list[dict] = []
    for family_id in family_order:
        ordered.extend(copy.deepcopy(blocks_by_family[family_id]))
    return ordered


def _build_parent_addition_checkpoint(
    parent_obj: dict,
    blocks_by_family: dict[str, list[dict]],
    family_order: list[str],
    out_path: Path,
) -> None:
    obj = copy.deepcopy(parent_obj)
    obj["logiqa_trunk_recurrent_blocks"] = _ordered_blocks(blocks_by_family, family_order)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _build_current_removal_checkpoint(
    current_obj: dict,
    removed_prefixes: set[str],
    out_path: Path,
) -> None:
    obj = copy.deepcopy(current_obj)
    kept = []
    for block in list(obj.get("logiqa_trunk_recurrent_blocks") or []):
        name = str(block.get("block_name", "") or "")
        if any(name.startswith(prefix) for prefix in removed_prefixes):
            continue
        kept.append(block)
    obj["logiqa_trunk_recurrent_blocks"] = kept
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and evaluate public causal sequence checkpoints.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--manifest-out", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = (args.workspace_root or repo_root.parent).resolve()
    manifest_out = (
        args.manifest_out.resolve()
        if args.manifest_out is not None
        else (workspace_root / "artifacts/reports/public_controls/public_causal_sequence_manifest.json")
    )

    parent_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_20260310_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_ready.json"
    current_checkpoint = workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    parent_obj = _read_json(parent_checkpoint)
    current_obj = _read_json(current_checkpoint)

    family_prefixes = {
        "A_bc": "trunk_option_latent_v2_official_bc_zeroinit_routes",
        "B_dbb_bc": "trunk_option_latent_v2_official_dbb_bc_support_b1_additive",
        "C_ad": "trunk_option_latent_v2_official_ad_support_b1_additive",
    }
    blocks_by_family = _family_blocks(current_obj, family_prefixes)

    cache_dir = workspace_root / "artifacts/tmp/authoritative_five_bench_cache"
    out_dir = workspace_root / "artifacts/reports/public_controls"
    tmp_dir = workspace_root / "artifacts/tmp/public_causal_sequence"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    official_logiqa = cache_dir / "logiqa_test.txt"
    external_dev_logiqa = workspace_root / "artifacts/data/external_logiqa_dev.txt"
    external_blind_logiqa = workspace_root / "artifacts/data/external_logiqa_blind.txt"

    variants = {
        "forward_add_A_bc": {
            "kind": "forward_addition",
            "family_order": ["A_bc"],
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Start from the frozen parent and add the public BC family only."],
        },
        "forward_add_A_bc_B_dbb_bc": {
            "kind": "forward_addition",
            "family_order": ["A_bc", "B_dbb_bc"],
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Start from the frozen parent and add BC followed by DBB-BC."],
        },
        "forward_add_A_bc_B_dbb_bc_C_ad": {
            "kind": "forward_addition",
            "family_order": ["A_bc", "B_dbb_bc", "C_ad"],
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Start from the frozen parent and add BC, DBB-BC, then AD."],
        },
        "order_swap_B_dbb_bc_A_bc_C_ad": {
            "kind": "order_swap",
            "family_order": ["B_dbb_bc", "A_bc", "C_ad"],
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Parent-side three-family surface with DBB-BC applied before BC."],
        },
        "order_swap_C_ad_A_bc_B_dbb_bc": {
            "kind": "order_swap",
            "family_order": ["C_ad", "A_bc", "B_dbb_bc"],
            "source_surface": "frozen_authoritative_parent",
            "notes": ["Parent-side three-family surface with AD applied before BC and DBB-BC."],
        },
        "reverse_remove_C_ad_from_current": {
            "kind": "reverse_removal",
            "removed_families": ["C_ad"],
            "source_surface": "current_scientific_surface",
            "notes": ["Start from the current surface and remove AD first."],
        },
        "reverse_remove_C_ad_B_dbb_bc_from_current": {
            "kind": "reverse_removal",
            "removed_families": ["C_ad", "B_dbb_bc"],
            "source_surface": "current_scientific_surface",
            "notes": ["Start from the current surface and remove AD then DBB-BC."],
        },
        "reverse_remove_C_ad_B_dbb_bc_A_bc_from_current": {
            "kind": "reverse_removal",
            "removed_families": ["C_ad", "B_dbb_bc", "A_bc"],
            "source_surface": "current_scientific_surface",
            "notes": ["Start from the current surface and remove AD, DBB-BC, then BC."],
        },
    }

    for variant_id, meta in variants.items():
        ckpt_path = tmp_dir / f"{variant_id}.json"
        if meta["kind"] in {"forward_addition", "order_swap"}:
            _build_parent_addition_checkpoint(parent_obj, blocks_by_family, list(meta["family_order"]), ckpt_path)
        else:
            removed_prefixes = {family_prefixes[family_id] for family_id in list(meta["removed_families"])}
            _build_current_removal_checkpoint(current_obj, removed_prefixes, ckpt_path)
        meta["checkpoint"] = str(ckpt_path)
        meta["reports"] = {
            "official_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=ckpt_path,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{variant_id}_official_logiqa",
                    logiqa_input=official_logiqa,
                )
            ),
            "external_dev_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=ckpt_path,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{variant_id}_external_dev",
                    logiqa_input=external_dev_logiqa,
                )
            ),
            "external_blind_logiqa": str(
                _run_logiqa_eval(
                    workspace_root=workspace_root,
                    checkpoint=ckpt_path,
                    out_dir=out_dir,
                    cache_dir=cache_dir,
                    output_tag=f"{variant_id}_external_blind",
                    logiqa_input=external_blind_logiqa,
                )
            ),
        }

    manifest = {
        "manifest_kind": "public_causal_sequence_v1",
        "generated_at": _now(),
        "parent_checkpoint": str(parent_checkpoint),
        "current_checkpoint": str(current_checkpoint),
        "families": [
            {"family_id": family_id, "prefix": prefix, "block_count": len(blocks_by_family[family_id])}
            for family_id, prefix in family_prefixes.items()
        ],
        "variants": variants,
        "privacy_boundary": {
            "published_summary_only": True,
            "withheld_from_public_docs": [
                "full family-mining trace",
                "private support graph",
                "full route-token inventory",
            ],
        },
    }
    _write_json(manifest_out, manifest)


if __name__ == "__main__":
    main()
