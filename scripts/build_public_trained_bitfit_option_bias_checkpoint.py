#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a trained same-parent BitFit-style option-bias baseline checkpoint.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--base-checkpoint", type=Path, required=True)
    parser.add_argument("--curriculum", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--max-logiqa-samples", type=int, default=112)
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()

    workspace_root = (args.workspace_root or Path(__file__).resolve().parents[2]).resolve()
    tools_dir = workspace_root / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    from three_benchmark_seed_model import (  # pylint: disable=import-error,import-outside-toplevel
        load_model,
        parse_logiqa_prompt,
        predict_logiqa_option,
    )

    torch.manual_seed(int(args.seed))

    base_model = load_model(args.base_checkpoint.resolve())
    rows = _load_curriculum_rows(args.curriculum.resolve(), int(args.max_logiqa_samples))
    option_to_idx = {"A": 0, "B": 1, "C": 2, "D": 3}

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
        parent_scores.append(
            torch.tensor(
                [float(parent_pre_side_scores.get(opt, 0.0) or 0.0) for opt in ["A", "B", "C", "D"]],
                dtype=torch.float32,
            )
        )
        gold_indices.append(int(option_to_idx[gold]))
        sample_ids.append(str(row.get("sample_id") or row.get("id") or ""))

    if not parent_scores:
        raise RuntimeError("no usable logical_reasoning_mcq rows for BitFit baseline training")

    x = torch.stack(parent_scores, dim=0)
    y = torch.tensor(gold_indices, dtype=torch.long)
    n_samples = int(x.shape[0])

    bias_delta = torch.zeros((4,), dtype=torch.float32, requires_grad=True)
    optimizer = torch.optim.AdamW([bias_delta], lr=float(args.lr), weight_decay=float(args.weight_decay))

    loss_last = 0.0
    for _ in range(max(1, int(args.epochs))):
        perm = torch.randperm(n_samples)
        for idx in perm.tolist():
            logits = x[idx] + bias_delta
            loss = F.cross_entropy(logits.view(1, 4), y[idx].view(1))
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            loss_last = float(loss.detach().item())

    with torch.no_grad():
        pred = torch.argmax(x + bias_delta.view(1, 4), dim=1)
        train_acc = float((pred == y).to(torch.float32).mean().item())

    existing_bias = dict(base_model.get("logiqa_option_bias", {}) or {})
    out_bias = {}
    for opt, idx in option_to_idx.items():
        base_val = float(existing_bias.get(opt, 0.0) or 0.0)
        out_bias[opt] = base_val + float(bias_delta[idx].item())

    out_obj = dict(base_model or {})
    out_obj["logiqa_option_bias"] = out_bias
    out_obj["public_trained_bitfit_option_bias_source"] = {
        "training_task": "logical_reasoning_mcq",
        "training_samples": int(n_samples),
        "trainable_parameter_count": 4,
        "epochs": int(args.epochs),
        "lr": float(args.lr),
        "weight_decay": float(args.weight_decay),
        "seed": int(args.seed),
        "train_accuracy": float(train_acc),
        "loss_last": float(loss_last),
        "bias_delta": {
            "A": float(bias_delta[0].item()),
            "B": float(bias_delta[1].item()),
            "C": float(bias_delta[2].item()),
            "D": float(bias_delta[3].item()),
        },
        "note": "same_parent_bitfit_style_option_bias_only_baseline",
        "sample_ids_preview": [sid for sid in sample_ids if sid][:32],
    }

    out_obj = _make_json_safe(out_obj)
    _write_json(args.out.resolve(), out_obj)
    print(f"trained_bitfit_option_bias_checkpoint={args.out.resolve()}")
    print(f"training_samples={n_samples}")
    print(f"train_accuracy={train_acc:.6f}")


if __name__ == "__main__":
    main()
