# Trust And Audit

This repository does not ask readers to trust a single score line. It publishes a layered audit stack.

## 1. Overlap and leakage audit

Goal:

- rule out obvious text-level contamination across official and external evaluation sets

Current evidence:

- no exact overlap was found between the clean blind `holdout2` subset and official `LogiQA`
- no exact overlap was found between the clean blind `holdout2` subset and `external_dev`

Source:

- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)

## 2. Official drift audit

Goal:

- measure question-level `base_only` and `candidate_only` flips rather than relying only on aggregate accuracy

Current research line:

- official drift `base_only = 0`
- official drift `candidate_only = 3`

Source:

- [../results/research_line/current_scientific_surface_manifest.json](../results/research_line/current_scientific_surface_manifest.json)

## 3. Protected wins

Goal:

- prevent new routes from winning locally while silently breaking already-earned official wins

This logic is part of the internal route/family gate stack that feeds the current surface. The public repo exposes the resulting current-surface status rather than the full internal route-generation pipeline.

## 4. External non-regression

Goal:

- reject candidates that improve official `LogiQA` while degrading external distributions

Current research line:

- `external_dev = 0.308908`
- `external_blind = 0.425072`

These are part of the public current-surface reference.

Source:

- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)

## 5. Acceptance, runtime, and shadow

Goal:

- ensure the promoted scientific surface is not only accurate, but also runtime-clean and shadow-clean

Current reference:

- `structured_all_pass = true`
- `runtime_pass = true`
- `shadow_pass = true`
- `research_runtime_ready = true`

Sources:

- [../results/research_line/current_scientific_surface_guard_bundle_status.json](../results/research_line/current_scientific_surface_guard_bundle_status.json)
- [../results/research_line/current_scientific_surface_integrity_status.json](../results/research_line/current_scientific_surface_integrity_status.json)
- [../results/research_line/current_scientific_surface_doctor_status.json](../results/research_line/current_scientific_surface_doctor_status.json)

## 6. Clean holdout2 and blind remainder

Goal:

- move beyond a single aggregate blind score
- create a post-hoc clean holdout that is deduplicated against official and `external_dev`

Current results:

- `holdout2 = 0.400000`
- `blind_remainder = 0.448133`

Important boundary:

- this is stronger than a single aggregate blind replay
- it is still weaker than a fully independent unseen sourced dataset

Source:

- [../results/audit/current_scientific_surface_overfit_audit_status.json](../results/audit/current_scientific_surface_overfit_audit_status.json)

## 7. Hidden-family forensic audit

Goal:

- test whether improvements generalize beyond the residual families that drove the observed surface gains

Current result:

- hidden-family holdout rows: `85`
- current surface: `0 / 85`
- freeze and nearby prior surfaces: also `0 / 85`

This is the most important boundary in the public repo.

It means:

- we do **not** currently see obvious external collapse
- we also do **not** currently have strong evidence for hidden-family generalization

Source:

- [../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json](../results/audit/current_scientific_surface_hidden_family_forensic_audit_status.json)

## Board-proof acceptance

The public board-proof line is also audited separately:

- board proof mode: `logiqa_batch_compiled_probe_aggregated`
- compiled probe mode: `host_full_exact`
- aggregate board result: `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Sources:

- [../results/board_proof/board_runtime_audit_acceptance.json](../results/board_proof/board_runtime_audit_acceptance.json)
- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

## Bottom line

The strongest honest statement this repository can make today is:

- there is no obvious text-level leakage or external collapse in the published current surface
- there is a real, audited `ESP32-C3` board proof aligned to host-full fixed-batch decisions
- hidden-family generalization remains weak, and that limitation is published rather than hidden
