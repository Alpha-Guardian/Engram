#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import torch
import torch.nn.functional as F


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _make_json_safe(obj):
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if str(key).startswith("_"):
                continue
            safe_value = _make_json_safe(value)
            if safe_value is not None:
                out[str(key)] = safe_value
        return out
    if isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    if isinstance(obj, tuple):
        return [_make_json_safe(v) for v in obj]
    if isinstance(obj, set):
        return sorted(_make_json_safe(v) for v in obj)
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return None


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
        item = f"bg:{left}_{right}"
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
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


def _question_route_tokens(logiqa_paths: list[Path], bigram_max: int) -> list[str]:
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


def _load_curriculum_rows(path: Path, max_logiqa_samples: int) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if str(row.get("task_type", "")).strip() != "logical_reasoning_mcq":
            continue
        target = str(row.get("target", "")).strip().upper()
        if target not in {"A", "B", "C", "D"}:
            continue
        rows.append(row)
        if len(rows) >= max_logiqa_samples:
            break
    if not rows:
        raise RuntimeError("no logical_reasoning_mcq rows found in curriculum")
    return rows


def _hash_feature_dense(
    *,
    text: str,
    hash_dim: int,
    max_tokens: int,
    tokenize_fn,
    stable_tie_breaker_fn,
) -> torch.Tensor:
    toks = tokenize_fn(text)
    if max_tokens > 0:
        toks = toks[:max_tokens]
    vec = torch.zeros((hash_dim,), dtype=torch.float32)
    if not toks:
        return vec
    for tok in toks:
        idx = int(stable_tie_breaker_fn(tok) % hash_dim)
        vec[idx] += 1.0
    vec /= float(max(1, len(toks)))
    return vec


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a trained same-parent LoRA-style hash-delta checkpoint for public controls.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--base-checkpoint", type=Path, required=True)
    parser.add_argument("--curriculum", type=Path, required=True)
    parser.add_argument("--route-source", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cluster-name", default="public_trained_lora_style_hash_delta_baseline")
    parser.add_argument("--hash-dim", type=int, default=4096)
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.03)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--max-logiqa-samples", type=int, default=112)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--delta-scale", type=float, default=1.0)
    parser.add_argument("--cluster-alpha", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=29)
    args = parser.parse_args()

    workspace_root = (args.workspace_root or Path(__file__).resolve().parents[2]).resolve()
    tools_dir = workspace_root / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    from three_benchmark_seed_model import (  # pylint: disable=import-error,import-outside-toplevel
        load_model,
        parse_logiqa_prompt,
        predict_logiqa_option,
        stable_tie_breaker,
        tokenize,
    )

    torch.manual_seed(int(args.seed))

    base_model = load_model(args.base_checkpoint.resolve())
    route_tokens = _question_route_tokens(
        [p.resolve() for p in list(args.route_source or [])],
        int(base_model.get("logiqa_bigram_max", 96) or 96),
    )
    if not route_tokens:
        raise RuntimeError("route token union is empty")

    rows = _load_curriculum_rows(args.curriculum.resolve(), int(args.max_logiqa_samples))
    hash_dim = int(args.hash_dim)
    max_tokens = int(args.max_tokens)
    option_to_idx = {"A": 0, "B": 1, "C": 2, "D": 3}

    feats: list[torch.Tensor] = []
    parent_scores: list[torch.Tensor] = []
    gold_indices: list[int] = []
    sample_ids: list[str] = []

    for row in rows:
        prompt = str(row.get("prompt", "") or "")
        stem, options = parse_logiqa_prompt(prompt)
        if not stem or len(options) != 4:
            continue
        gold = str(row.get("target", "")).strip().upper()
        if gold not in option_to_idx:
            continue
        predict_logiqa_option(stem, options, base_model)
        debug = dict(base_model.get("_last_logiqa_debug", {}) or {})
        parent_pre_side_scores = dict(debug.get("parent_pre_side_scores", {}) or {})
        if not all(opt in parent_pre_side_scores for opt in ["A", "B", "C", "D"]):
            continue
        q_features: list[torch.Tensor] = []
        for opt in ["A", "B", "C", "D"]:
            feat_text = f"[OPT_{opt}] {str(options.get(opt, '') or '')}"
            q_features.append(
                _hash_feature_dense(
                    text=feat_text,
                    hash_dim=hash_dim,
                    max_tokens=max_tokens,
                    tokenize_fn=tokenize,
                    stable_tie_breaker_fn=stable_tie_breaker,
                )
            )
        feats.append(torch.stack(q_features, dim=0))
        parent_scores.append(
            torch.tensor(
                [float(parent_pre_side_scores.get(opt, 0.0) or 0.0) for opt in ["A", "B", "C", "D"]],
                dtype=torch.float32,
            )
        )
        gold_indices.append(int(option_to_idx[gold]))
        sample_ids.append(str(row.get("sample_id") or row.get("id") or ""))

    if not feats:
        raise RuntimeError("no usable logical_reasoning_mcq rows for LoRA-style baseline training")

    x = torch.stack(feats, dim=0)  # [N, 4, D]
    parent = torch.stack(parent_scores, dim=0)  # [N, 4]
    y = torch.tensor(gold_indices, dtype=torch.long)
    n_samples = int(x.shape[0])

    rank = int(args.rank)
    factor_a = torch.zeros((rank, hash_dim), dtype=torch.float32, requires_grad=True)
    factor_b = torch.zeros((rank,), dtype=torch.float32, requires_grad=True)
    optimizer = torch.optim.AdamW([factor_a, factor_b], lr=float(args.lr), weight_decay=float(args.weight_decay))

    loss_last = 0.0
    for _ in range(max(1, int(args.epochs))):
        perm = torch.randperm(n_samples)
        for idx in perm.tolist():
            weight_delta = torch.sum(factor_a * factor_b.view(rank, 1), dim=0)  # [D]
            logits = parent[idx] + torch.matmul(x[idx], weight_delta) * float(args.delta_scale) * float(args.cluster_alpha)
            loss = F.cross_entropy(logits.view(1, 4), y[idx].view(1))
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            loss_last = float(loss.detach().item())

    with torch.no_grad():
        weight_delta = torch.sum(factor_a * factor_b.view(rank, 1), dim=0)
        logits_all = parent + torch.matmul(x, weight_delta) * float(args.delta_scale) * float(args.cluster_alpha)
        pred = torch.argmax(logits_all, dim=1)
        train_acc = float((pred == y).to(torch.float32).mean().item())
        delta_vec = [float(v) for v in weight_delta.detach().cpu().tolist()]

    cluster = {
        "cluster_name": str(args.cluster_name),
        "alpha": float(args.cluster_alpha),
        "route_tokens": list(route_tokens),
        "route_token_groups": [],
        "route_group_min_matches": 0,
        "route_exclude_tokens": [],
        "allowed_tokens": list(route_tokens),
        "support_sample_ids": [sid for sid in sample_ids if sid][: min(32, len(sample_ids))],
        "support_exemplars": [],
        "route_min_hits": 1,
        "update_mode": "both",
        "readout_mode": "cluster_local_gpu_hash_delta_v1",
        "gpu_hash_delta_dim": int(hash_dim),
        "gpu_hash_delta_weights": delta_vec,
        "gpu_hash_delta_scale": float(args.delta_scale),
    }

    out_obj = dict(base_model or {})
    clusters = list(out_obj.get("logiqa_side_branch_clusters", []) or [])
    clusters.append(cluster)
    out_obj["logiqa_side_branch_clusters"] = clusters
    out_obj["logiqa_side_branch_freeze_parent"] = True
    out_obj["public_trained_lora_style_hash_delta_source"] = {
        "cluster_name": str(args.cluster_name),
        "training_task": "logical_reasoning_mcq",
        "training_samples": int(n_samples),
        "hash_dim": int(hash_dim),
        "rank": int(rank),
        "trainable_parameter_count": int(rank * hash_dim + rank),
        "effective_delta_parameter_count": int(hash_dim),
        "epochs": int(args.epochs),
        "lr": float(args.lr),
        "weight_decay": float(args.weight_decay),
        "max_tokens": int(max_tokens),
        "route_union_size": int(len(route_tokens)),
        "seed": int(args.seed),
        "train_accuracy": float(train_acc),
        "loss_last": float(loss_last),
        "note": "same_parent_lora_style_factorized_hash_delta_baseline",
    }

    out_obj = _make_json_safe(out_obj)
    _write_json(args.out.resolve(), out_obj)
    print(f"trained_lora_style_hash_delta_checkpoint={args.out.resolve()}")
    print(f"training_samples={n_samples}")
    print(f"route_union_size={len(route_tokens)}")
    print(f"train_accuracy={train_acc:.6f}")


if __name__ == "__main__":
    main()
