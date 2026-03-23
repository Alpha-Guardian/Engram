# Method Contract

This repository publishes the public contract for a constrained auditable capability-upgrade workflow. It does not publish the private frontier search or full training stack.

## Object Of Study

The public method object is not a single block, not a generic PEFT primitive, and not only a board artifact.

The accepted object is:

- a `frozen authoritative parent`
- a set of `residual-family local repairs`
- a `route-gated trunk recurrent surface`
- a `promotion contract` that all accepted repairs must survive
- a `derived bounded artifact` for the board proof

That coupled object is the unit of evidence in this repo.

See:

- [INNOVATION.md](INNOVATION.md)
- [FAMILY_AND_ROUTING.md](FAMILY_AND_ROUTING.md)
- [TRUNK_BLOCKS.md](TRUNK_BLOCKS.md)
- [PROMOTION_CONTRACT.md](PROMOTION_CONTRACT.md)

## Frozen Parent

All public comparisons are anchored to one frozen authoritative parent.

Why that matters:

- gain is always measured relative to the frozen parent
- locality probes compare candidate behavior against the frozen parent
- the exact no-trunk ablation is interpreted as a return to the frozen parent boundary
- additional release-boundary audits are also interpreted against the frozen parent boundary

The parent row is published in:

- [../results/experiments/main_table.json](../results/experiments/main_table.json)

## Residual Family

In public terms, a residual family is a bounded error slice defined by the combination of:

- the parent competition shape
- the local repair target pair
- the route surface that decides where the repair may fire

This repo publishes the accepted family-local repair evidence and representative locality probes. It does not publish the full discovery frontier, rejected candidates, or support-source graph.

## Route Activation

Public route semantics are documented in:

- [FAMILY_AND_ROUTING.md](FAMILY_AND_ROUTING.md)

At a high level:

- question and option token surfaces are converted into a route signature
- a block is eligible only if its route requirements are satisfied
- parent-topology conditions must also match before the recurrent repair can fire

The current public inventory shows:

- `75` trunk recurrent blocks
- median route token count `6`
- route minimum hits of `2` or `3`
- a published-eval route-disabled proxy collapses official `LogiQA` to `0.244548`

See:

- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

## Trunk Recurrent Blocks

The current public surface contains:

- `72` blocks in `option_latent_v2`
- `3` blocks in `pair_score`
- `11,325` exemplars
- `8192` GPU hash dim

The repo publishes block-level structure and representative sanitized fields, but not full route tokens, source ids, or latent prototypes.

Public contrastive controls now also show:

- target-only diagnostic blocks reach only `0.308411`
- a same-parent trained linear-readout control reaches `0.300623`
- a same-parent trained BitFit option-bias control reaches `0.266355`
- a same-parent trained LoRA-style hash-delta control reaches `0.303738`
- a same-parent trained low-rank adapter baseline reaches `0.303738`
- a same-parent trainable-budget-matched LoRA-style control reaches `0.303738`
- a same-parent trainable-budget-matched low-rank adapter control reaches `0.303738`
- architecture-near low-rank adapter controls stay at the frozen-parent level

See:

- [TRUNK_BLOCKS.md](TRUNK_BLOCKS.md)
- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

## Promotion Contract

A local repair counts only if it survives a coupled acceptance predicate. Publicly visible parts of that predicate include:

- official replay against the frozen parent
- external non-regression
- leakage and deep-pretrain audit status
- runtime and shadow cleanliness
- overfit and release-boundary disclosure

The public repo also documents a stricter internal mainline:

- the formal mainline monitors multiple benchmark routes rather than one benchmark only
- in the current public line, that includes `LogiQA`, `GSM8K`, and a narrow instruction-following benchmark
- external dev and external blind are treated as required gates, not optional side receipts

See:

- [PROMOTION_CONTRACT.md](PROMOTION_CONTRACT.md)
- [TRUST_AND_AUDIT.md](TRUST_AND_AUDIT.md)

## Crystallization Boundary

The board proof is a derived artifact, not the whole method claim.

Current public board scope:

- aggregate board-proof summary mode: `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `evaluation_mode = logiqa_batch_compiled_probe`
- `compiled_probe_mode = host_full_exact`
- fixed published batches only

So the board proof demonstrates bounded crystallization correctness, not unrestricted open-input reasoning on MCU.

See:

- [BOARD_METRICS.md](BOARD_METRICS.md)
- [OPEN_INPUT_ROADMAP.md](OPEN_INPUT_ROADMAP.md)

## Published Versus Withheld

Published here:

- accepted mechanism contract
- replayable public evidence
- representative locality probes
- exact no-trunk ablation
- board acceptance and raw readback

Withheld here:

- full family-mining pipeline
- rejected frontier
- support-source graph
- curriculum construction rules
- full checkpoint internals needed to reproduce the private training moat
