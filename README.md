# Engram

Engram is an offline Tiny Expert board proof for extreme edge constraints.

This repository is not a cloud-LLM replacement and not a public release of the full training stack. It is a task-specialized, table-driven, auditable edge reasoning line that shows how benchmark capability can be crystallized into a very small, flash-resident runtime on a commodity `ESP32-C3`.

The repo now publishes two layers on purpose:

- `Public board proof`: a real `ESP32-C3` fixed-batch compiled run for `LogiQA 642`
- `Research capability line`: the current audited host-side scientific surface with official, external, runtime, and overfitting status

## Quick facts

| Item | Value |
|---|---|
| Target board | `ESP32-C3` |
| Public board proof mode | `logiqa_batch_compiled_probe_aggregated` |
| Compiled probe mode | `host_full_exact` |
| Public board proof | `249 / 642 = 0.3878504672897196` |
| Board proof host alignment | `host_full_match = 642 / 642` |
| Runtime artifact | `chip_suite_surface_round2_q4_tgz_expack_rgz.json` |
| Artifact size | `1,380,771 bytes` |
| Default firmware size | `1,784,352 bytes` |
| Research line | official `IFEval = 0.780037`, official `LogiQA = 0.392523` |
| External guard | `external_dev = 0.308908`, `external_blind = 0.425072` |
| Trust boundary | clean `holdout2 = 0.400000`, hidden-family `0 / 85` |

## Why this matters

Many edge deployments do not need a general cloud assistant. They need a tiny, deterministic, offline decision system that fits severe memory and power budgets and can still be audited when something goes wrong.

This repository is a public proof of that direction:

- `Offline`: no cloud inference is required for the published board proof
- `Table-driven`: the runtime is flash-resident and structured, not a dense open-input LLM stack
- `Auditable`: board reports, benchmark references, integrity checks, and overfitting evidence are all published
- `Edge-constrained`: the target is a commodity `ESP32-C3`, not a GPU server

## What this repo proves

### 1. Public board proof

The board proof in this repository is a real `ESP32-C3` execution line.

- Board summary: [results/board_proof/esp32c3_logiqa642_board_proof_summary.json](results/board_proof/esp32c3_logiqa642_board_proof_summary.json)
- Board acceptance: [results/board_proof/board_runtime_audit_acceptance.json](results/board_proof/board_runtime_audit_acceptance.json)
- Raw board batches: [results/board_proof/raw](results/board_proof/raw)

The published board result is:

- `LogiQA 642 = 249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

That means the board-side compiled path exactly reproduces the host full decisions for the published fixed batches.

### 2. Research capability line

The current audited host-side scientific surface is published separately:

- [results/research_line/current_scientific_surface_manifest.json](results/research_line/current_scientific_surface_manifest.json)
- [results/research_line/current_scientific_surface_reference_status.json](results/research_line/current_scientific_surface_reference_status.json)
- [results/research_line/current_scientific_surface_guard_bundle_status.json](results/research_line/current_scientific_surface_guard_bundle_status.json)

Current reference metrics:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

### 3. Trust and audit layer

The repository also ships the public evidence layer for:

- replay and integrity
- runtime and shadow gates
- overlap and external non-regression
- post-hoc clean holdout audit
- hidden-family forensic audit

See:

- [docs/TRUST_AND_AUDIT.md](docs/TRUST_AND_AUDIT.md)
- [results/audit/current_scientific_surface_overfit_audit_status.json](results/audit/current_scientific_surface_overfit_audit_status.json)
- [results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json](results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json)

## Hard boundaries

This repository does **not** claim:

- unrestricted open-input native LLM inference on `ESP32-C3`
- public release of the full training pipeline
- public release of the full materialization and candidate-generation workflow
- proof of general reasoning beyond the audited task surface

The current board line is:

- a fixed-batch compiled board proof
- aligned to host full decisions
- auditable through raw board reports and published summaries

That boundary matters. The point of this repository is to show a real, reproducible, edge-constrained Tiny Expert line without pretending it is a general-purpose on-device chatbot.

## Quick start

See [docs/REPRODUCE.md](docs/REPRODUCE.md) for the full walkthrough.

Shortest path:

1. Flash the published firmware:

```bash
py scripts/flash_firmware.py COM3
```

2. Read the board report back:

```bash
py scripts/read_board_report.py COM3 --expect-mode logiqa_batch_compiled_probe --expect-artifact-sha256 626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d
```

3. Compare the returned JSON against:

- [results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json](results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json)
- [results/board_proof/esp32c3_logiqa642_board_proof_summary.json](results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

Important scope note:

- the default firmware reproduces a published fixed batch board report
- the full `642` score is the audited aggregate over the included `11` board-side raw reports

## Repository layout

- [firmware](firmware)
  - the published `ESP32-C3` board-proof binaries
- [results/board_proof](results/board_proof)
  - the current board-proof summary, acceptance, and raw batch reports
- [results/research_line](results/research_line)
  - the current scientific surface manifest and replay status
- [results/audit](results/audit)
  - the current overfitting and hidden-family forensic evidence
- [docs](docs)
  - method boundary, audit notes, capability framing, and reproduction notes
- [scripts](scripts)
  - flashing and report readback helpers

## Further reading

- [docs/WHY_TINY_EXPERTS.md](docs/WHY_TINY_EXPERTS.md)
- [docs/CAPABILITY_MATRIX.md](docs/CAPABILITY_MATRIX.md)
- [docs/BOARD_METRICS.md](docs/BOARD_METRICS.md)
- [docs/TRUST_AND_AUDIT.md](docs/TRUST_AND_AUDIT.md)
- [docs/RESEARCH_LINE.md](docs/RESEARCH_LINE.md)
- [docs/METHOD.md](docs/METHOD.md)
- [docs/FAQ.md](docs/FAQ.md)
