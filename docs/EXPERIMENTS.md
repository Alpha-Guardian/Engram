# Experiments

This page consolidates the public experiment bundle that supports the current accepted host surface.

## Main Public Comparison Table

| Surface | IFEval | Official LogiQA | External Dev | External Blind |
|---|---:|---:|---:|---:|
| Frozen authoritative parent | `0.780037` | `0.303738` | `0.304598` | `0.425072` |
| Current no-trunk ablation | `0.780037` | `0.303738` | `0.304598` | `0.425072` |
| Earlier three-family promoted surface | `0.780037` | `0.308411` | `0.304598` | `0.425072` |
| Single-family official BC surface | `0.780037` | `0.348910` | `0.308908` | `0.425072` |
| Single-family official DBB-BC surface | `0.780037` | `0.353583` | `0.308908` | `0.425072` |
| Current accepted host surface | `0.780037` | `0.392523` | `0.308908` | `0.425072` |

Source:

- [../results/experiments/main_table.json](../results/experiments/main_table.json)

Interpretation:

- the current accepted host surface improves official `LogiQA` by `+0.088785` over the frozen parent
- the no-trunk ablation collapses exactly back to the parent boundary
- replayable same-parent slices improve on the parent but do not subsume the current surface

## Minimal Second-Task Validation

Public second-task validation uses the same authoritative `IFEval` path already carried by the official dual-bench reports.

Result:

- frozen parent `IFEval = 0.780037`
- no-trunk ablation `IFEval = 0.780037`
- earlier three-family surface `IFEval = 0.780037`
- single-family BC surface `IFEval = 0.780037`
- single-family DBB-BC surface `IFEval = 0.780037`
- current accepted host surface `IFEval = 0.780037`

Interpretation:

- the published same-parent progression does not buy `LogiQA` gain by sacrificing the public instruction-following task
- this is valid cross-task non-regression evidence
- this is not yet evidence of positive transfer or broad multi-task generalization

Source:

- [../results/experiments/cross_task_validation.json](../results/experiments/cross_task_validation.json)

## Independent Industrial Second-Task Line

The repo now also publishes a true parent-derived second-task capability line on a separate small industrial-state decision benchmark.

Result on the published 8-sample `industrial_state_decision_logiqa_v2` benchmark:

- frozen parent `0.25`
- exact no-trunk ablation `0.25`
- same-parent trained linear baseline `0.25`
- current accepted host surface `0.375`
- parent-derived independent industrial second line `0.625`

Pairwise independent-line replay:

- independent vs parent: `improved = 3`, `harmed = 0`
- independent vs no-trunk: `improved = 3`, `harmed = 0`
- independent vs trained linear: `improved = 3`, `harmed = 0`
- independent vs current surface: `improved = 2`, `harmed = 0`

Interpretation:

- this is the clearest current public evidence that the same frozen-parent trunk pipeline can instantiate a new second-task capability line rather than only improve the current `LogiQA` surface
- exact no-trunk and trained linear controls remain at the frozen-parent level on this benchmark
- the current accepted host surface transfers somewhat, but the dedicated parent-derived industrial line is stronger
- because the benchmark is still small, this should be read as second-task capability-production evidence rather than proof of broad industrial generalization

Source:

- [../results/experiments/independent_industrial_second_line.json](../results/experiments/independent_industrial_second_line.json)

## Industrial Second-Line Formal Protocol

The repo also freezes a public protocol for the industrial second line:

- train source: `industrial_wrapper_protected_slice_v1` (`18` samples)
- external dev: `industrial_state_decision_logiqa_lite_v1` (`10` samples)
- blind slice: `industrial_state_decision_logiqa_v2` (`8` samples)
- non-regression monitor: official `IFEval`

Candidate under the frozen protocol:

- checkpoint: independent industrial second-line subset `5+6+8+10`
- dev `= 0.2`
- blind `= 0.5`
- official `IFEval = 0.781885`

Frozen external-union summary after protocol freeze:

- external union samples `= 18`
- candidate `= 0.333333`
- frozen parent `= 0.166667`
- exact no-trunk `= 0.166667`
- trained linear baseline `= 0.166667`
- transferred current surface `= 0.277778`

External-union pairwise replay:

- candidate vs parent: `improved = 3`, `harmed = 0`
- candidate vs no-trunk: `improved = 3`, `harmed = 0`
- candidate vs trained linear: `improved = 3`, `harmed = 0`
- candidate vs current surface: `improved = 1`, `harmed = 0`

Controls under the same protocol:

- frozen parent: dev `0.1`, blind `0.25`
- exact no-trunk: dev `0.1`, blind `0.25`
- trained linear baseline: dev `0.1`, blind `0.25`
- current accepted host surface: dev `0.2`, blind `0.375`

Gate result:

- dev above parent: pass
- dev above no-trunk: pass
- dev above trained linear: pass
- dev at least current: pass
- blind above parent: pass
- blind above no-trunk: pass
- blind above trained linear: pass
- blind above current: pass
- `IFEval` non-regression vs parent: pass
- overall protocol gate: pass

Interpretation:

- this is the current strongest public evidence that the same frozen-parent trunk pipeline can produce a new second-task capability line under a fixed auditable protocol
- the protocol is stronger than a single held-out score because it fixes train source, external dev, blind slice, and a non-regression monitor
- the frozen external union thickens the evidence beyond a single blind slice: after protocol freeze, the candidate stays above parent, no-trunk, trained linear, and the transferred current surface across all `18` published external samples
- the benchmark is still small, so this should be presented as bounded capability-production evidence rather than proof of broad industrial generalization

Source:

- [../results/experiments/industrial_second_line_protocol.json](../results/experiments/industrial_second_line_protocol.json)

## Lightly Domain-Shifted Industrial Wrapper Probe

The repo now also publishes a small second-task probe that wraps current-win reasoning shapes in industrial and embedded review language while preserving a `LogiQA`-style multiple-choice reasoning surface.

Result on the published 10-sample probe:

- frozen parent `0.1`
- exact no-trunk ablation `0.1`
- same-parent trained linear baseline `0.1`
- current accepted host surface `0.2`

Pairwise current-versus-control replay:

- current vs parent: `improved = 1`, `harmed = 0`
- current vs no-trunk: `improved = 1`, `harmed = 0`
- current vs trained linear: `improved = 1`, `harmed = 0`

Interpretation:

- this is a weak but positive task-transfer signal under a light domain shift toward deployment-shaped language
- the gain still localizes to the promoted trunk blocks because exact no-trunk falls back to the frozen-parent level
- the same-parent trained linear baseline also stays at the frozen-parent level
- this is still an exploratory transfer probe, not a claim of broad industrial generalization

Source:

- [../results/experiments/industrial_state_decision_probe.json](../results/experiments/industrial_state_decision_probe.json)

## Protected Transfer Slice

The repo also publishes a curated protected slice built from public current-win reasoning shapes and wrapped in industrial or embedded review language.

Result on the published 18-sample protected slice:

- frozen parent `0.166667`
- exact no-trunk ablation `0.166667`
- same-parent trained linear baseline `0.166667`
- current accepted host surface `0.333333`

Pairwise current-versus-control replay:

- current vs parent: `improved = 3`, `harmed = 0`
- current vs no-trunk: `improved = 3`, `harmed = 0`
- current vs trained linear: `improved = 3`, `harmed = 0`

Interpretation:

- this is cleaner localized transfer evidence than the broader lightly domain-shifted wrapper probe
- exact no-trunk and trained linear staying at the frozen-parent level keep the causal story intact
- because the slice is curated, it should be read as protected-slice evidence, not as a broad naturally sampled second-task benchmark

Source:

- [../results/experiments/industrial_wrapper_protected_slice.json](../results/experiments/industrial_wrapper_protected_slice.json)

## Exploratory Second-Task Probe: GSM8K

An additional exploratory probe was run on `GSM8K` under the same frozen-parent boundary.

Result:

- official `GSM8K`: parent `0.019712`, current `0.019712`, no-trunk `0.019712`
- external dev `GSM8K`: parent `0.016064`, current `0.016064`, no-trunk `0.016064`
- external blind `GSM8K`: parent `0.024096`, current `0.024096`, no-trunk `0.024096`

Interpretation:

- no positive second-task gain is currently visible on `GSM8K`
- the present public object is still best described as a bounded `LogiQA` specialist surface
- the next real multi-task step is not more wording, but a new second-task family and promotion path

Source:

- [../results/experiments/gsm8k_second_task_probe.json](../results/experiments/gsm8k_second_task_probe.json)

## Exact No-Trunk Ablation

Current public exact ablation:

- remove the promoted trunk blocks from the current checkpoint
- replay the same authoritative and external pipelines

Result:

- official `LogiQA` returns from `0.392523` to `0.303738`
- `external_dev` returns from `0.308908` to `0.304598`
- `external_blind` remains `0.425072`

Interpretation:

- the public gain localizes to the promoted trunk blocks rather than generic checkpoint drift

Source:

- [../results/experiments/ablations.json](../results/experiments/ablations.json)

## Paired Replay Statistics

Current public paired replay versus the no-trunk / parent boundary:

- official `LogiQA` delta `= +0.088785`
- official improved only `= 66`
- official harmed only `= 9`
- official bootstrap `95% CI = [0.063863, 0.115265]`
- official exact McNemar `p = 7.658840702050266e-12`
- external dev delta `= +0.004310`
- external blind delta `= 0.000000`

Interpretation:

- the official gain is statistically strong
- external behavior does not show an obvious published collapse

Source:

- [../results/experiments/ablations.json](../results/experiments/ablations.json)

## Additional Controls

The public repo now also ships thirteen extra LogiQA-local controls:

| Control | Official LogiQA | External Dev | External Blind | Interpretation |
|---|---:|---:|---:|---|
| current surface, published-eval route-disabled proxy | `0.244548` | `0.261494` | `0.322767` | disabling route selectivity on the published evaluation surface causes a large collapse |
| current surface, no topology gate | `0.280374` | `0.295977` | `0.371758` | removing parent topology conditions substantially harms both official and external behavior |
| current surface, depth = 1 | `0.323988` | `0.304598` | `0.423631` | one recurrent step keeps only part of the gain |
| frozen parent + BC low-rank adapter control | `0.303738` | `0.304598` | `0.425072` | architecture-near adapter control does not improve over the frozen parent |
| frozen parent + DBB-BC low-rank adapter control | `0.303738` | `0.304598` | `0.425072` | architecture-near adapter control does not improve over the frozen parent |
| frozen parent + BC target-only diagnostic control | `0.308411` | `0.304598` | `0.425072` | target-derived blocks alone give only a small gain and do not match support-derived family performance |
| frozen parent + DBB-BC target-only diagnostic control | `0.308411` | `0.304598` | `0.425072` | target-derived blocks alone give only a small gain and do not match support-derived family performance |
| frozen parent + trained linear-readout baseline | `0.300623` | `0.303161` | `0.425072` | a classic trained same-parent linear control does not reproduce the promoted-surface gain |
| frozen parent + trained BitFit option-bias baseline | `0.266355` | `0.297414` | `0.412104` | a same-parent BitFit-style bias-only comparator is also weaker than the frozen parent |
| frozen parent + trained LoRA-style hash-delta baseline | `0.303738` | `0.304598` | `0.425072` | a same-parent LoRA-style factorized hash-delta comparator remains at the frozen-parent level |
| frozen parent + trained low-rank adapter baseline | `0.303738` | `0.304598` | `0.425072` | a same-parent trained low-rank adapter-style PEFT comparator also stays at the frozen-parent level |
| frozen parent + budget-matched LoRA-style baseline | `0.303738` | `0.304598` | `0.425072` | a trainable-budget-matched same-parent LoRA-style comparator also stays at the frozen-parent level |
| frozen parent + budget-matched low-rank adapter baseline | `0.303738` | `0.304598` | `0.425072` | a trainable-budget-matched same-parent low-rank adapter comparator also stays at the frozen-parent level |
| frozen parent + retrieval-only baseline | `0.291277` | `0.287356` | `0.432277` | a classical retrieval-only comparator is weaker than the frozen parent on official and external dev |
| frozen parent + lexical-only baseline | `0.289720` | `0.260057` | `0.273775` | a classical lexical-only comparator is substantially weaker than the frozen parent |

Interpretation:

- route selectivity is necessary rather than optional
- parent topology constraints are necessary, not cosmetic
- recurrence depth matters for the current surface
- support-derived families are materially stronger than target-only diagnostic blocks
- retrieval-only, lexical-only, trained linear, trained BitFit, trained LoRA-style hash-delta, trained low-rank adapter, and trainable-budget-matched PEFT comparators all fail to reach the accepted host surface
- simply attaching same-parent low-rank adapter-style family controls does not reproduce the accepted host-surface gain

Source:

- [../results/experiments/additional_controls.json](../results/experiments/additional_controls.json)

## Causal Sequence

The public repo now exposes a three-family causal sequence built from public BC, DBB-BC, and AD families.

Forward addition from the frozen parent:

- `BC`: official `0.308411`
- `BC + DBB-BC`: official `0.313084`
- `BC + DBB-BC + AD`: official `0.317757`

Reverse removal from the current surface:

- `current - AD`: official `0.387850`
- `current - AD - DBB-BC`: official `0.383178`
- `current - AD - DBB-BC - BC`: official `0.378505`

Order-swap result on the published evals:

- `DBB-BC -> BC -> AD`: official `0.317757`
- `AD -> BC -> DBB-BC`: official `0.317757`

Interpretation:

- the three public families produce a monotone gain when added from the frozen parent
- removing the same three families from the current surface causes a monotone loss
- for this small published three-family subset, order swap did not change the published official or external scores

Source:

- [../results/experiments/causal_sequence.json](../results/experiments/causal_sequence.json)

## Locality Probes

Representative public locality evidence:

- `official_bc_zeroinit_routes`, narrow probe: targets fixed `3 / 3`, off-target fires `0`, collateral flips `0`
- `official_bc_zeroinit_routes`, protected slice: targets fixed `3 / 3`, off-target fires `0`, collateral flips `0`
- `official_dbb_bc_support_b1_additive`, narrow probe: targets fixed `3 / 3`, off-target fires `0`, collateral flips `0`
- `official_dbb_bc_support_b1_additive`, protected slice: targets fixed `3 / 3`, off-target fires `0`, collateral flips `0`

Wider public locality context:

- `official_ad_support_b1_additive`, narrow probe: targets fixed `3 / 3`, off-target fires `0`, collateral flips `0`
- `official_ad_support_b1_additive`, protected slice: targets fixed `3 / 3`, off-target fires `6`, collateral flips `0`

Interpretation:

- the tightest representative evidence supports the family-local repair story
- the wider probe set also shows that not every family is equally narrow

Source:

- [../results/experiments/locality_probes.json](../results/experiments/locality_probes.json)

## Negative Evidence Preserved In Public

Current public negative boundary:

- clean `holdout2 = 0.400000`
- `blind_remainder = 0.448133`
- hidden-family `0 / 85`

Interpretation:

- the public line is bounded and specialized
- it should not be sold as broad hidden-family reasoning generalization

Sources:

- [../results/audit/current_host_surface_overfit_audit_status.json](../results/audit/current_host_surface_overfit_audit_status.json)
- [../results/audit/current_host_surface_hidden_family_forensic_audit_status.json](../results/audit/current_host_surface_hidden_family_forensic_audit_status.json)

## Comparator Coverage Boundary

This repo now publishes:

- exact no-trunk ablation
- route-disabled, topology-removal, and depth-one controls
- target-only diagnostic controls
- retrieval-only, lexical-only, and trained linear classic comparators
- trained same-parent BitFit option-bias comparator
- trained same-parent LoRA-style factorized hash-delta comparator
- trained same-parent low-rank adapter-style comparator
- trained same-parent trainable-budget-matched LoRA-style comparator
- trained same-parent trainable-budget-matched low-rank adapter comparator
- architecture-near same-parent low-rank adapter controls

The current public matched-budget protocol uses the promoted trunk numeric payload as the target budget. Under that protocol:

- the trainable-budget target is `3123` published trunk numeric payload values
- the matched LoRA-style control uses `rank = 1`, `hash_dim = 3123`, trainable parameter count `= 3124`
- the matched low-rank adapter control uses `rank = 1`, `hash_dim = 3123`, trainable parameter count `= 3124`
- both matched controls replay exactly at the frozen-parent metric level

So the current public claim is:

- evidence for a constrained auditable capability-upgrade workflow

It is not:

- a blanket dominance claim over all nearby PEFT or local-editing methods

That limitation is intentional and visible.

## Open-Input Evidence

Published open-input evidence now has two separate tracks:

- host-side structured open-input loop
- board-side `ESP32-C3` narrow open-input micro-loop

Current board-side micro-loop result:

- samples `= 36`
- exact match `= 1.0`
- nonempty rate `= 1.0`
- stability rate `= 1.0`

Source:

- [../results/open_input_demo/host_open_input_demo.json](../results/open_input_demo/host_open_input_demo.json)
- [../results/open_input_demo/mcu_open_input_demo.json](../results/open_input_demo/mcu_open_input_demo.json)

## Board-Side Comparator Bundle

The public repo now also includes a narrow board-side comparator bundle on the same `ESP32-C3` fixed `642`-sample path:

| Board artifact | Accuracy | Correct | Host full match |
|---|---:|---:|---:|
| current host surface | `0.387850` | `249 / 642` | `642 / 642` |
| frozen parent | `0.302181` | `194 / 642` | `642 / 642` |
| parent trained linear baseline | `0.299065` | `192 / 642` | `642 / 642` |

Interpretation:

- the current host surface keeps a clear board-side margin over the frozen parent
- a simple trained same-parent linear baseline also fails on the real board path
- all three artifacts preserve exact host-full decision alignment on the compiled batches

Scope boundary:

- this board comparator bundle is intentionally narrow
- stronger route-heavy PEFT-style baselines are published on host-side evals, but they do not currently fit the public `ESP32-C3` artifact budget

Source:

- [../results/board_proof/board_baseline_comparison.json](../results/board_proof/board_baseline_comparison.json)
