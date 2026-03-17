# Research Line Snapshot

This repository publishes a public board proof and a public trust layer, not the entire internal training stack.

That distinction matters because the strongest host-side scientific surface is broader than the exact board-proof path published here.

## Current scientific surface

Current published host-side reference:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`
- `runtime_pass = true`
- `shadow_pass = true`

Primary files:

- [../results/research_line/current_scientific_surface_manifest.json](../results/research_line/current_scientific_surface_manifest.json)
- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)

## Public board proof

Published board proof:

- target board: `ESP32-C3`
- mode: `logiqa_batch_compiled_probe_aggregated`
- compiled probe mode: `host_full_exact`
- board result: `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Primary files:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)
- [../results/board_proof/board_runtime_audit_acceptance.json](../results/board_proof/board_runtime_audit_acceptance.json)

## Why they are not identical

The host-side scientific surface and the board-proof path are related but not identical.

The host-side scientific surface is:

- the current audited capability line
- used for official, external, replay, integrity, and overfitting status

The board-proof path is:

- a constrained compiled fixed-batch execution line
- published to demonstrate real flash-resident MCU execution and exact host-full alignment on the released batches

This repo intentionally keeps that distinction visible.

## Why not publish the full internal stack

This repository is designed as a public proof layer, not a dump of the entire internal R&D workflow.

What is public here:

- current scientific surface status
- board proof binaries
- board raw reports
- replay and audit status

What is not public here:

- the full family sweep pipeline
- the full candidate-generation and materialization workflow
- the full internal training and selection logic

## What the current evidence supports

It supports:

- a real edge-constrained Tiny Expert line
- a real `ESP32-C3` board proof
- a host-side capability line that is stronger than the published board proof
- a trust layer that includes negative evidence, not just positive claims

It does not support:

- unrestricted open-input board inference
- proof of general reasoning
- strong hidden-family transfer
