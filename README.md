# Engram

We make constrained, reliable, and auditable edge intelligence possible on ultra-low-cost hardware.

Engram publishes a public proof bundle for a constrained capability-promotion regime under extreme edge constraints.

This repository is not a public dump of the private family-mining, curriculum, or training pipeline. It publishes the accepted mechanism, replayable evidence for that mechanism, and a derived fixed-batch `ESP32-C3` board artifact.

## Overview

Most edge AI systems still push complex reasoning back to cloud APIs. In practice that creates avoidable risk in three areas: latency, recurring cloud cost, and data boundary control.

This repo demonstrates an alternative path: keep constrained, auditable reasoning loops on low-cost `ESP32-C3` class hardware, with explicit boundaries and replayable evidence.

## Positioning

Compared with common deployment patterns:

- `Cloud-first inference`: strong generality, but higher dependency and data-boundary pressure in sensitive environments.
- `Pure rule engines`: predictable behavior, but limited adaptability once task complexity increases.
- `Generic edge model ports`: easier demos, but often weak auditability and unclear acceptance boundaries.

This project focuses on a narrower but defensible point in that space: auditable local capability promotion under strict constraints.

## Early Fit

- `Offline industrial control`: on-device, rule-bound reasoning in plants and field deployments with unstable connectivity.
- `Air-gapped security workflows`: local assistance where data cannot leave the hardware boundary.
- `Deterministic edge decision engines`: constrained control loops for gateways, robots, and embedded operators.

## Current Public Evidence

- Same-parent gain is real and localized: official `LogiQA` improves from `0.303738` to `0.392523`; exact no-trunk ablation returns to `0.303738`.
- A second public task stays stable across the same-parent progression: official `IFEval` remains `0.780037` from frozen parent through the current surface.
- A true parent-derived industrial second-task line is now public: on `industrial_state_decision_logiqa_v2`, the independent line reaches `0.625` while frozen parent, exact no-trunk, and trained linear baseline each remain at `0.25`, and the transferred current surface reaches `0.375`.
- A fixed public second-line protocol now passes end to end: using a frozen public train source, external dev slice, blind slice, and `IFEval` non-regression monitor, the industrial candidate `5+6+8+10` reaches dev `0.2` and blind `0.5`, above parent/no-trunk/trained linear and above the transferred current surface on the blind slice.
- The frozen external union is now also public: across all `18` published external second-task samples, the same candidate reaches `0.333333` versus parent/no-trunk/trained-linear `0.166667` and transferred current `0.277778`.
- A lightly domain-shifted industrial wrapper probe now shows a positive same-parent transfer signal: current reaches `0.2` while frozen parent, exact no-trunk, and trained linear baseline each remain at `0.1`.
- A curated protected industrial-wrapper slice shows a cleaner localized transfer signal: current reaches `0.333333` while frozen parent, exact no-trunk, and trained linear baseline each remain at `0.166667`.
- Neighbor baselines under the same parent boundary do not reproduce the current surface (`BitFit-style`, `LoRA-style`, low-rank adapter-style, trainable-budget-matched LoRA-style, trainable-budget-matched adapter-style, retrieval-only, lexical-only).
- Board derivation is real: fixed-batch `ESP32-C3` proof reaches `249 / 642 = 0.3878504672897196` with `host_full_match = 642 / 642`.
- Board-side comparator bundle is now public: frozen parent reaches `194 / 642 = 0.302181`, trained linear baseline reaches `192 / 642 = 0.299065`, and both keep `host_full_match = 642 / 642`.
- Open-input is separated from board-proof claim: published `ESP32-C3` narrow micro-loop reaches `36 / 36` exact match with stability `1.0`.

Current boundary: this repo demonstrates feasibility, auditability, and a constrained deployment path. It does not claim broad general reasoning on MCU hardware.

## At A Glance

| Item | Value |
|---|---|
| Innovation object | `frozen parent + residual-family local repair + coupled promotion gates + derived board artifact` |
| Current public host surface | official `IFEval = 0.780037`, official `LogiQA = 0.392523` |
| Public second-task check | same-parent progression keeps official `IFEval = 0.780037` throughout |
| Public independent second line | parent-derived industrial second line on `industrial_state_decision_logiqa_v2`: independent `0.625`, current `0.375`, parent `0.25`, no-trunk `0.25`, trained linear `0.25` |
| Public second-line protocol | train source `protected18`, dev `lite10`, blind `v2_8`, candidate `5+6+8+10`: dev `0.2`, blind `0.5`, `IFEval = 0.781885`, all gates pass |
| Public second-line external union | frozen external union over `18` published second-task samples: candidate `0.333333`, current `0.277778`, parent/no-trunk/trained linear `0.166667` |
| Public domain-shift probe | lightly domain-shifted industrial wrapper probe: current `0.2`, frozen parent `0.1`, no-trunk `0.1`, trained linear `0.1` |
| Protected transfer slice | curated industrial-wrapper slice: current `0.333333`, frozen parent `0.166667`, no-trunk `0.166667`, trained linear `0.166667` |
| Exact localization control | no-trunk ablation returns to official `LogiQA = 0.303738` |
| Additional controls | route-disabled `0.244548`, no-topology `0.280374`, depth-1 `0.323988`, target-only `0.308411`, trained linear `0.300623`, trained BitFit-style `0.266355`, trained LoRA-style `0.303738`, trained low-rank adapter-style `0.303738`, budget-matched LoRA-style `0.303738`, budget-matched adapter-style `0.303738`, retrieval-only `0.291277`, lexical-only `0.289720`, adapter controls `0.303738` |
| External guard | `external_dev = 0.308908`, `external_blind = 0.425072` |
| Paired official delta | `+0.088785`, exact McNemar `p = 7.658840702050266e-12` |
| Current block inventory | `75` trunk recurrent blocks = `72` `option_latent_v2` + `3` `pair_score` |
| Current retrieval footprint | `11,325` exemplars, `8192` GPU hash dim |
| Hidden-family boundary | `0 / 85` |
| Public board proof | `ESP32-C3`, `249 / 642 = 0.3878504672897196`, `host_full_match = 642 / 642` |
| Public board comparators | frozen parent `194 / 642 = 0.302181`, trained linear baseline `192 / 642 = 0.299065`, both `host_full_match = 642 / 642` |
| Public MCU open-input micro-loop | `ESP32-C3`, `36 / 36 exact match`, `stability = 1.0` |

## Start Here

- [docs/INNOVATION.md](docs/INNOVATION.md)
- [docs/METHOD.md](docs/METHOD.md)
- [docs/FAMILY_AND_ROUTING.md](docs/FAMILY_AND_ROUTING.md)
- [docs/TRUNK_BLOCKS.md](docs/TRUNK_BLOCKS.md)
- [docs/PROMOTION_CONTRACT.md](docs/PROMOTION_CONTRACT.md)
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)
- [docs/TRUST_AND_AUDIT.md](docs/TRUST_AND_AUDIT.md)
- [docs/BOARD_METRICS.md](docs/BOARD_METRICS.md)
- [docs/OPEN_INPUT_DEMO.md](docs/OPEN_INPUT_DEMO.md)
- [docs/OPEN_INPUT_ROADMAP.md](docs/OPEN_INPUT_ROADMAP.md)

## What Is New

This repo now publishes six layers together instead of only a board demo:

- `Mechanism`: the public contract for residual-family routing, trunk recurrent blocks, and promotion gates
- `Experiments`: replayable same-parent comparisons, exact no-trunk ablation, paired replay statistics, locality probes, and published three-family causal sequences
- `Controls`: route-disabled, topology-removal, depth-one, target-only diagnostic, retrieval-only, lexical-only, trained linear-readout, trained BitFit option-bias baseline, trained LoRA-style hash-delta baseline, trained low-rank adapter baseline, trainable-budget-matched LoRA-style and adapter-style baselines, and architecture-near adapter controls
- `Open Input`: a host-side structured JSON loop plus a board-side narrow open-input micro-loop, both kept separate from the fixed-batch board proof
- `Audit boundary`: overfit, hidden-family, runtime, shadow, integrity, and board acceptance evidence
- `Artifact`: a real `ESP32-C3` fixed-batch board proof derived from the current research line

The key claim is not that any one primitive is new in isolation. The public object is the coupled regime that turns family-local repairs into an audited promoted scientific surface and then into a bounded deployment artifact.

## What This Repo Proves

- A frozen authoritative parent can be improved on official `LogiQA` by a replayable promoted surface while preserving the published external boundary.
- The current gain localizes to the promoted trunk blocks: removing them returns the checkpoint to parent-equivalent behavior on matched replays.
- The same frozen-parent trunk pipeline can instantiate a new independent industrial second-task capability line: on the published `industrial_state_decision_logiqa_v2` benchmark, the parent-derived line reaches `0.625` while frozen parent, exact no-trunk, and trained linear controls each remain at `0.25`.
- Under a fixed public second-line protocol with frozen train source, external dev, blind slice, and `IFEval` non-regression monitor, the candidate subset `5+6+8+10` passes every published gate and outperforms the transferred current surface on the blind slice.
- After freezing that protocol, the candidate also remains ahead on the combined external second-task surface (`18` samples total), not just on a single blind slice.
- A lightly domain-shifted industrial wrapper probe shows a same-parent positive signal (`0.2` vs `0.1`) while the exact no-trunk and trained linear controls stay at the frozen-parent level.
- A curated protected industrial-wrapper slice shows a cleaner same-parent localized transfer signal (`0.333333` vs `0.166667`) while exact no-trunk and trained linear controls stay at the frozen-parent level.
- Representative routed families can fire on their designated targets with zero observed collateral flips in the published narrow and protected slices.
- A small real open-input host loop can be run under the current surface with `exact_match_rate = 1.0` and `unsafe_guard_rate = 1.0` on the published structured taskset.
- A real `ESP32-C3` narrow open-input micro-loop can be run with `36 / 36` exact match and `stability_rate = 1.0` on the published board taskset.
- The accepted host-side surface can be crystallized into a real `ESP32-C3` fixed-batch artifact with exact host-full alignment on the published batches.

## What This Repo Does Not Prove

- unrestricted broad open-input MCU inference
- broad reasoning generalization
- blanket dominance over nearby LoRA, BitFit, adapter, or local-editing baselines
- blanket dominance over all trainable-budget-matched PEFT variants outside the published bundle
- public release of the full search, curriculum, support-selection, or training pipeline

Those boundaries are explicit by design. The repo publishes the accepted evidence bundle without exposing the private asset layer that produced it.

## Quick Start

See [docs/REPRODUCE.md](docs/REPRODUCE.md) for the full walkthrough.

Board path:

```bash
py scripts/flash_firmware.py COM3
py scripts/read_board_report.py COM3 --expect-mode logiqa_batch_compiled_probe --expect-artifact-sha256 626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d
```

Mode note:

- default single-batch board readback uses `evaluation_mode = logiqa_batch_compiled_probe`
- published 642 aggregate board-proof summary uses `evaluation_mode = logiqa_batch_compiled_probe_aggregated`

MCU open-input micro-loop path:

```bash
py scripts/flash_open_input_firmware.py COM3
py scripts/run_mcu_open_input_demo.py --port COM3
```

Public-bundle verification:

```bash
python3 scripts/verify_public_bundle.py
```

Public experiment assets:

- [results/experiments/main_table.json](results/experiments/main_table.json)
- [results/experiments/cross_task_validation.json](results/experiments/cross_task_validation.json)
- [results/experiments/independent_industrial_second_line.json](results/experiments/independent_industrial_second_line.json)
- [results/experiments/industrial_second_line_protocol.json](results/experiments/industrial_second_line_protocol.json)
- [results/experiments/industrial_state_decision_probe.json](results/experiments/industrial_state_decision_probe.json)
- [results/experiments/industrial_wrapper_protected_slice.json](results/experiments/industrial_wrapper_protected_slice.json)
- [results/experiments/ablations.json](results/experiments/ablations.json)
- [results/experiments/additional_controls.json](results/experiments/additional_controls.json)
- [results/experiments/causal_sequence.json](results/experiments/causal_sequence.json)
- [results/experiments/locality_probes.json](results/experiments/locality_probes.json)
- [results/experiments/block_inventory.json](results/experiments/block_inventory.json)
- [results/experiments/manifest.json](results/experiments/manifest.json)
- [results/open_input_demo/host_open_input_demo.json](results/open_input_demo/host_open_input_demo.json)
- [results/open_input_demo/mcu_open_input_demo.json](results/open_input_demo/mcu_open_input_demo.json)
- [results/open_input_demo/mcu_open_input_taskset_v1.jsonl](results/open_input_demo/mcu_open_input_taskset_v1.jsonl)
- [results/open_input_demo/mcu_open_input_board_report.json](results/open_input_demo/mcu_open_input_board_report.json)
- [results/board_proof/board_baseline_comparison.json](results/board_proof/board_baseline_comparison.json)

## Repository Layout

- [docs](docs)
  - public method contract, experiments, audit boundary, and roadmap
- [results/experiments](results/experiments)
  - public-safe experiment tables and block inventory
- [results/open_input_demo](results/open_input_demo)
  - host-side structured open-input demo summary and MCU narrow open-input micro-loop evidence
- [results/research_line](results/research_line)
  - current promoted scientific surface manifest and guard bundle
- [results/audit](results/audit)
  - overfit and hidden-family forensic evidence
- [results/board_proof](results/board_proof)
  - `ESP32-C3` board summary, acceptance, and raw batch reports
- [firmware](firmware)
  - published binaries for the board-proof line
- [scripts](scripts)
  - flashing, report readback, bundle verification, and maintainer summary export scripts
