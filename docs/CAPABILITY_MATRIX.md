# Capability Matrix

This repository deliberately separates three layers.

| Layer | Meaning | Proven here | Not proven here |
|---|---|---|---|
| Research capability line | host-side current scientific surface | official gain, external non-regression, runtime and shadow gates | direct unrestricted MCU execution of the full host pathway |
| Public board proof | audited `ESP32-C3` fixed-batch compiled execution | flash-resident board run, raw readback, exact host-full alignment on published batches | open-input native inference, general runtime equivalence for arbitrary inputs |
| Generalization audit | anti-overfitting evidence | no obvious external collapse, clean holdout2, hidden-family forensic disclosure | strong hidden-family generalization, proof of broad reasoning transfer |

## Current values

### Research capability line

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

Source:

- [../results/research_line/current_scientific_surface_manifest.json](../results/research_line/current_scientific_surface_manifest.json)

### Public board proof

- board proof mode: `logiqa_batch_compiled_probe_aggregated`
- compiled probe mode: `host_full_exact`
- board proof result: `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Source:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

### Generalization audit

- clean `holdout2 = 0.400000`
- `blind_remainder = 0.448133`
- hidden-family holdout: `0 / 85`

Sources:

- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)
- [../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json](../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json)

## How to read this correctly

The strongest honest claim this repository makes is:

- a task-specialized Tiny Expert line can be audited, compressed, and executed on a real `ESP32-C3`
- its host-side capability line is stronger than its board-proof line
- its anti-overfitting evidence is meaningful but still bounded

The repo does **not** claim that these three layers are identical.
