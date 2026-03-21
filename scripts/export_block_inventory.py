#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bucket_counts(values: list[int], bounds: list[tuple[int, int | None, str]]) -> dict[str, int]:
    counts = Counter()
    for value in values:
        matched = False
        for lower, upper, label in bounds:
            if value < lower:
                continue
            if upper is None or value <= upper:
                counts[label] += 1
                matched = True
                break
        if not matched:
            counts[str(value)] += 1
    return dict(sorted(counts.items()))


def _numeric_summary(values: list[int | float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "min": 0, "max": 0, "mean": 0.0, "median": 0.0}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(float(mean(values)), 6),
        "median": round(float(median(values)), 6),
    }


def _top_counts(counter: Counter, limit: int = 12) -> list[dict[str, int | str]]:
    rows = []
    for key, count in counter.most_common(limit):
        rows.append({"key": key, "count": count})
    return rows


def _sanitize_block(block: dict) -> dict:
    return {
        "block_name": block.get("block_name") or block.get("name"),
        "mode": block.get("mode"),
        "route_token_count": len(list(block.get("route_tokens") or [])),
        "route_group_count": len(list(block.get("route_token_groups") or [])),
        "route_min_hits": int(block.get("route_min_hits") or 0),
        "route_group_min_matches": int(block.get("route_group_min_matches") or 0),
        "support_count": int(block.get("support_count") or 0),
        "train_count": int(block.get("train_count") or 0),
        "parent_top": block.get("parent_top"),
        "parent_second": block.get("parent_second"),
        "parent_margin_max": float(block.get("parent_margin_max") or 0.0),
        "mapped_gold": block.get("mapped_gold"),
        "mapped_competitor": block.get("mapped_competitor"),
        "depth_steps": int(block.get("depth_steps") or 0),
        "step_scale": float(block.get("step_scale") or 0.0),
        "score_scale": float(block.get("score_scale") or 0.0),
        "evidence_scale": float(block.get("evidence_scale") or 0.0),
        "pair_bias_scale": float(block.get("pair_bias_scale") or 0.0),
        "stop_margin": float(block.get("stop_margin") or 0.0),
        "pair_hash_dim": int(block.get("pair_hash_dim") or 0),
        "latent_dim": int(block.get("latent_dim") or 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a public-safe block inventory summary.")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Path to the source checkpoint. Defaults to the current host surface checkpoint in the workspace root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to results/experiments/block_inventory.json inside github_demo.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = repo_root.parent
    checkpoint_path = args.checkpoint or (
        workspace_root / "artifacts/models/candidates/three_bench_candidate_current_scientific_surface.json"
    )
    output_path = args.output or (repo_root / "results/experiments/block_inventory.json")

    model = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    blocks = list(model.get("logiqa_trunk_recurrent_blocks") or [])

    mode_counts = Counter(str(block.get("mode") or "unknown") for block in blocks)
    parent_pair_counts = Counter(
        f"{block.get('parent_top', '?')}->{block.get('parent_second', '?')}" for block in blocks
    )
    mapped_pair_counts = Counter(
        f"{block.get('mapped_gold', '?')}->{block.get('mapped_competitor', '?')}" for block in blocks
    )

    route_token_counts = [len(list(block.get("route_tokens") or [])) for block in blocks]
    support_counts = [int(block.get("support_count") or 0) for block in blocks]
    depth_steps = [int(block.get("depth_steps") or 0) for block in blocks]
    route_min_hits = Counter(int(block.get("route_min_hits") or 0) for block in blocks)
    route_group_min_matches = Counter(int(block.get("route_group_min_matches") or 0) for block in blocks)

    representative_blocks = sorted(
        (_sanitize_block(block) for block in blocks),
        key=lambda item: (-int(item["support_count"]), str(item["block_name"])),
    )[:12]

    payload = {
        "inventory_kind": "public_block_inventory_v1",
        "source_checkpoint": str(checkpoint_path.relative_to(workspace_root)),
        "source_checkpoint_sha256": _sha256(checkpoint_path),
        "checkpoint_summary": {
            "logiqa_exemplar_count": len(list(model.get("logiqa_exemplars") or [])),
            "gpu_logiqa_hash_dim": int(model.get("gpu_logiqa_hash_dim") or 0),
            "trunk_block_count": len(blocks),
        },
        "mode_counts": dict(sorted(mode_counts.items())),
        "route_token_count_summary": _numeric_summary(route_token_counts),
        "route_token_count_buckets": _bucket_counts(
            route_token_counts,
            [(0, 4, "0-4"), (5, 8, "5-8"), (9, 12, "9-12"), (13, None, "13+")],
        ),
        "support_count_summary": _numeric_summary(support_counts),
        "support_count_buckets": _bucket_counts(
            support_counts,
            [(0, 4, "0-4"), (5, 8, "5-8"), (9, 16, "9-16"), (17, None, "17+")],
        ),
        "depth_steps_summary": _numeric_summary(depth_steps),
        "route_min_hits_distribution": {str(key): value for key, value in sorted(route_min_hits.items())},
        "route_group_min_matches_distribution": {
            str(key): value for key, value in sorted(route_group_min_matches.items())
        },
        "top_parent_pairs": _top_counts(parent_pair_counts),
        "top_mapped_pairs": _top_counts(mapped_pair_counts),
        "representative_blocks": representative_blocks,
        "sensitive_fields_omitted": [
            "route_tokens",
            "route_token_groups",
            "route_exclude_tokens",
            "source_ids",
            "stem_source",
            "stem_tokens",
            "gold_proto",
            "competitor_proto",
        ],
        "note": "This inventory publishes checkpoint-level structure and representative block metadata, not the private family-mining or support-tracing assets.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
