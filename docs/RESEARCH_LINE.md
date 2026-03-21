# Research Line Snapshot

This repository publishes the current promoted scientific surface as a host-side research line, separate from the fixed-batch board proof.

## Current Surface

Current public host-side reference:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`
- `runtime_pass = true`
- `shadow_pass = true`

Primary files:

- [../results/research_line/current_scientific_surface_manifest.json](../results/research_line/current_scientific_surface_manifest.json)
- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)
- [../results/experiments/main_table.json](../results/experiments/main_table.json)

## Independent Industrial Wrapper Prototype

The repo also keeps a separate research-only prototype for a true parent-derived industrial-wrapper second line.

Current prototype status:

- materialized from a zero-init trunk recurrent train spec
- `8` materialized trunk blocks
- protected transfer slice accuracy `= 0.388889`
- lightly domain-shifted industrial wrapper probe accuracy `= 0.1`
- official `LogiQA = 0.283489`
- official `IFEval = 0.781885`

Interpretation:

- this line proves the second-task trunk pipeline can be instantiated into a non-empty independent checkpoint
- it is not promotable yet because it regresses official `LogiQA` below the frozen parent boundary
- it currently behaves more like a protected-slice specialist than a stable second promoted surface

Source:

- [../results/research_line/industrial_wrapper_independent_line_proto.json](../results/research_line/industrial_wrapper_independent_line_proto.json)

## Grouped Subset Search On The Independent Industrial Wrapper Prototype

The repo also keeps a grouped-subset search over the `8` materialized trunk blocks from that parent-derived industrial-wrapper prototype.

Current grouped-subset result:

- `group_b` is the strongest broad light-probe transfer group: `light probe = 0.2`, but `official LogiQA = 0.297508`
- `group_c` is the strongest official-boundary-preserving single group: `official LogiQA = 0.308411`, but `light probe = 0.1`
- `group_cd` is the strongest official single/paired subset overall: `official LogiQA = 0.309969`, but `light probe = 0.0`
- `group_bcd` is the cleanest parent-preserving mixed subset found so far: `official LogiQA = 0.303738`, `IFEval = 0.781885`, but `light probe = 0.1`

Interpretation:

- the blocks that help the broader light industrial probe most are not the same blocks that best preserve the official frozen-parent LogiQA boundary
- the grouped search therefore did not yet find a joint subset that both improves the broader industrial wrapper probe and keeps official `LogiQA` at or above the frozen parent
- this makes the independent industrial-wrapper line more interpretable, but still not promotable

Source:

- [../results/research_line/industrial_wrapper_subset_search_v2.json](../results/research_line/industrial_wrapper_subset_search_v2.json)

## Fine-Grained Block Search On The Best Industrial Target Region

The repo also keeps a finer-grained search over every non-empty subset of the strongest industrial-wrapper target region: `targets = {5, 6, 8, 10, 16}`.

Current fine-grained result:

- `target 6` is the main broad-probe-lifting block: `light probe = 0.2`, but `official LogiQA = 0.294393`
- `targets 5, 8, 10, 16` are the strongest official-boundary-preserving region: `targets 5+8+10+16` reaches `official LogiQA = 0.313084`, but `light probe = 0.0`
- the strongest mixed compromise is `targets 5+6+8+10`: `light probe = 0.2`, `official LogiQA = 0.302181`, `IFEval = 0.781885`
- the cleanest parent-matching subset is the full `5+6+8+10+16`: `official LogiQA = 0.303738`, but `light probe = 0.1`

Interpretation:

- broad industrial-wrapper transfer currently concentrates around `target 6`
- official frozen-parent boundary preservation concentrates around `targets 5, 8, 10, 16`
- the repo still does not have a subset that simultaneously reaches `light probe >= 0.2` and `official LogiQA >= frozen parent`
- this narrows the next optimization direction: recover more of the `target 6` transfer effect without paying the current official-boundary cost

Source:

- [../results/research_line/industrial_wrapper_block_subset_search_r3.json](../results/research_line/industrial_wrapper_block_subset_search_r3.json)

## Why This Matters

The host-side research line is where the public method claim lives:

- the exact no-trunk ablation is measured here
- paired replay statistics are measured here
- locality probes are measured here
- overfit and hidden-family boundaries are measured here

See:

- [EXPERIMENTS.md](EXPERIMENTS.md)
- [TRUST_AND_AUDIT.md](TRUST_AND_AUDIT.md)

## Relation To The Board Proof

The board proof is derived from this line, but it is not identical to it.

The host-side line proves:

- the current accepted capability surface
- the audit-backed comparison to the frozen parent
- the replayable evidence bundle

The board line proves:

- flash-resident real hardware execution
- exact host-full alignment on the published fixed batches

See:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)
- [BOARD_METRICS.md](BOARD_METRICS.md)

## Boundary

The public research line should not be misread as:

- a release of the private training stack
- proof of unrestricted on-device open-input reasoning
- proof of broad hidden-family generalization

Those non-claims remain explicit in the repo because they are part of the trust boundary.
