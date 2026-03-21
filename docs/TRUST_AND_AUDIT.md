# Trust And Audit

This repository does not ask readers to trust a single aggregate score. It publishes a layered audit stack around the current promoted scientific surface and the derived board artifact.

## 1. Exact Localization Control

The strongest public causal control is the exact no-trunk ablation.

Current result:

- official `IFEval` returns to `0.780037`
- official `LogiQA` returns to `0.303738`
- `external_dev` returns to `0.304598`
- `external_blind` returns to `0.425072`

Interpretation:

- the public gain localizes to the promoted trunk blocks rather than generic checkpoint drift

Source:

- [../results/experiments/ablations.json](../results/experiments/ablations.json)

Additional public controls:

- published-eval route-disabled proxy drops official `LogiQA` to `0.244548`
- removing parent topology conditions drops official `LogiQA` to `0.280374`
- reducing all trunk blocks to `depth_steps = 1` yields only `0.323988`
- target-only diagnostic controls reach only `0.308411`
- a same-parent trained linear-readout control reaches `0.300623`
- a same-parent trained BitFit option-bias control reaches `0.266355`
- a same-parent trained LoRA-style hash-delta control reaches `0.303738`
- a same-parent trained low-rank adapter baseline reaches `0.303738`
- a same-parent trainable-budget-matched LoRA-style control reaches `0.303738`
- a same-parent trainable-budget-matched low-rank adapter control reaches `0.303738`
- retrieval-only and lexical-only classic baselines reach only `0.291277` and `0.289720`
- same-parent low-rank adapter-style controls remain at the frozen-parent level

Source:

- [../results/experiments/additional_controls.json](../results/experiments/additional_controls.json)

## 2. Paired Replay Statistics

Aggregate gains are accompanied by question-level paired evidence.

Current public paired replay:

- official `LogiQA` delta `= +0.088785`
- `66` improved only, `9` harmed only
- exact McNemar `p = 7.658840702050266e-12`
- external dev delta `= +0.004310`
- external blind delta `= 0.000000`

Source:

- [../results/experiments/ablations.json](../results/experiments/ablations.json)

## 3. Overlap And Leakage Audit

Goal:

- rule out obvious text-level contamination across official and external evaluation sets

Current evidence:

- no exact overlap was found between clean blind `holdout2` and official `LogiQA`
- no exact overlap was found between clean blind `holdout2` and `external_dev`

Source:

- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)

## 4. External Non-Regression

Goal:

- reject candidates that improve official `LogiQA` while degrading external distributions

Current public line:

- `external_dev = 0.308908`
- `external_blind = 0.425072`

Source:

- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)

## 5. Runtime, Shadow, And Integrity

Goal:

- ensure the promoted surface is not only accurate, but also runtime-clean and shadow-clean

Current public guard status:

- `structured_all_pass = true`
- `runtime_pass = true`
- `shadow_pass = true`
- `research_runtime_ready = true`

Sources:

- [../results/research_line/current_scientific_surface_guard_bundle_status.json](../results/research_line/current_scientific_surface_guard_bundle_status.json)
- [../results/research_line/current_scientific_surface_integrity_status.json](../results/research_line/current_scientific_surface_integrity_status.json)
- [../results/research_line/current_scientific_surface_doctor_status.json](../results/research_line/current_scientific_surface_doctor_status.json)

## 6. Clean Holdout2 And Blind Remainder

Goal:

- move beyond one aggregate blind score
- publish a post-hoc clean subset deduplicated against official and `external_dev`

Current results:

- `holdout2 = 0.400000`
- `blind_remainder = 0.448133`

Important boundary:

- stronger than a single aggregate blind replay
- weaker than a fully independent unseen sourced dataset

Source:

- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)

## 7. Hidden-Family Forensic Audit

Goal:

- test whether current gains generalize beyond the visible residual families that drive the public surface gains

Current result:

- hidden-family holdout rows: `85`
- current surface: `0 / 85`
- freeze and nearby prior surfaces: also `0 / 85`

Interpretation:

- the public line does not show obvious external collapse
- it also does not yet show strong hidden-family generalization

Source:

- [../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json](../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json)

## 8. Board-Proof Acceptance

The derived board artifact is audited separately.

Current public board-proof line:

- aggregate board-proof mode: `logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `logiqa_batch_compiled_probe`
- compiled probe mode: `host_full_exact`
- aggregate board result: `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Sources:

- [../results/board_proof/board_runtime_audit_acceptance.json](../results/board_proof/board_runtime_audit_acceptance.json)
- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

## Bottom Line

The strongest honest public statement is:

- the repo contains a real promoted scientific surface with replayable evidence
- the gain localizes to the promoted trunk blocks under the exact public ablation
- a real `ESP32-C3` artifact reproduces the published host-full fixed batches
- hidden-family generalization remains weak and is published rather than hidden
