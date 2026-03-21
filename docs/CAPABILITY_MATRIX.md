# Capability Matrix

This repo deliberately separates four layers.

| Layer | Meaning | Proven Here | Not Proven Here |
|---|---|---|---|
| Method contract | the accepted public mechanism | frozen parent boundary, routed family-local repair, trunk block semantics, promotion contract | private discovery pipeline, full training moat |
| Experiment bundle | replayable evidence for the current surface | exact no-trunk ablation, same-parent slices, paired replay stats, locality probes | complete classic PEFT comparator coverage, full ablation grid |
| Audit boundary | trust and negative evidence | no obvious text overlap, external non-regression, holdout2, hidden-family disclosure | broad hidden-family generalization |
| Board artifact | derived `ESP32-C3` proof | flash-resident fixed-batch execution, raw board readback, exact host-full alignment | unrestricted open-input MCU inference |

## Current Values

### Method / Experiment Layer

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- no-trunk ablation official `LogiQA = 0.303738`
- paired official delta `= +0.088785`
- `75` trunk recurrent blocks

Sources:

- [../results/experiments/main_table.json](../results/experiments/main_table.json)
- [../results/experiments/ablations.json](../results/experiments/ablations.json)
- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

### Audit Layer

- `external_dev = 0.308908`
- `external_blind = 0.425072`
- clean `holdout2 = 0.400000`
- hidden-family `0 / 85`

Sources:

- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)
- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)
- [../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json](../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json)

### Board Layer

- aggregate board-proof mode: `logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `logiqa_batch_compiled_probe`
- compiled probe mode: `host_full_exact`
- board proof result: `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Source:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

## How To Read This Correctly

The strongest honest claim is:

- a task-specialized promoted surface can be audited and materially improved over its frozen parent
- that surface can be crystallized into a bounded board artifact
- the public evidence is meaningful but explicitly bounded

The repo does not claim that these four layers are identical.
