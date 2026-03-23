# FAQ

## What Is The Actual Innovation Object?

Not a single route, not a single block, and not only a board package.

The public innovation object is a coupled regime:

- frozen authoritative parent
- residual-family local repairs
- route-gated trunk recurrent blocks
- coupled promotion gates
- derived bounded board artifact

See:

- [INNOVATION.md](INNOVATION.md)

## Is This Just PEFT Or A Lookup Table?

The runtime is table-driven at execution time, and local adaptation has clear prior art. The narrower claim here is that a family-local repair only counts if it remains anchored to the frozen parent, survives the promotion contract, and can be crystallized into a bounded artifact.

So the public claim is not "we invented PEFT" and not "this is a general LLM on MCU."

## Are The Numbers Real?

Yes.

The public board proof is a real `ESP32-C3` run with raw JSON read back from the board `report` partition.

The public research line is backed by saved authoritative and external replay reports, exact ablation reports, paired replay statistics, and published audit JSON.

## Why Are There Two Kinds Of Numbers?

Because this repo separates:

- `host-side accepted surface`
- `derived fixed-batch board proof`

Current host-side line:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

Current board proof:

- `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

They are related, but they are not the same layer.

## Why Is The Board Number Slightly Lower?

Because the board artifact is a constrained compiled fixed-batch proof, while the host-side line is the broader current host surface.

The board result proves:

- real MCU execution
- exact host-full alignment on the published batches

It does not claim unrestricted open-input board inference.

## What Is A Residual Family?

Publicly, a residual family is a bounded error slice defined by:

- the parent competition shape
- the local repair target pair
- the routed activation surface that decides where the repair may fire

The repo publishes accepted family-local repair evidence. It does not publish the full family-mining frontier.

See:

- [FAMILY_AND_ROUTING.md](FAMILY_AND_ROUTING.md)

## Does This Leak The Private Training Moat?

No, not by itself.

What is public here:

- accepted mechanism contract
- replayable public evidence
- representative locality probes
- exact no-trunk ablation

What remains private:

- family discovery pipeline
- support and carrier mining
- rejected frontier
- curriculum construction rules
- full training and materialization pipeline

## Are There Any Controls Beyond No-Trunk?

Yes.

The repo now also publishes:

- a published-eval route-disabled proxy
- a no-topology current-surface control
- a depth-one current-surface control
- two target-only diagnostic controls
- a retrieval-only classic baseline
- a lexical-only classic baseline
- a same-parent trained linear-readout control
- a same-parent trained BitFit option-bias control
- a same-parent trained LoRA-style hash-delta control
- a same-parent trained low-rank adapter baseline
- a same-parent trainable-budget-matched LoRA-style baseline
- a same-parent trainable-budget-matched low-rank adapter baseline
- two same-parent low-rank adapter-style family controls

See:

- [../results/experiments/additional_controls.json](../results/experiments/additional_controls.json)

## Do You Publish Any Classical Baseline At All?

Yes, but with a clear boundary.

The public bundle now includes:

- a same-parent retrieval-only baseline
- a same-parent lexical-only baseline
- a same-parent trained linear-readout control
- a same-parent trained BitFit option-bias control
- a same-parent trained LoRA-style hash-delta control
- a same-parent trained low-rank adapter baseline
- a same-parent trainable-budget-matched LoRA-style baseline
- a same-parent trainable-budget-matched low-rank adapter baseline

It also includes:

- route-disabled and topology-removal controls
- depth-one recurrence control
- target-only diagnostic controls
- same-parent low-rank adapter-style controls

These give useful rigor, and the repo now publishes trainable-budget-matched same-parent PEFT-style controls for the current public surface.

## What Is Still Missing After The Matched PEFT Controls?

Comparator coverage is stronger, but still incomplete.

This repo therefore does not claim blanket dominance over nearby LoRA, BitFit, adapter, or local-editing baselines. The strongest public causal evidence today is:

- frozen parent
- exact no-trunk ablation
- route-disabled, topology-removal, and depth-one controls
- retrieval-only, lexical-only, trained linear, trained BitFit, trained LoRA-style, and trained low-rank adapter classic baselines
- trainable-budget-matched same-parent LoRA-style and low-rank adapter baselines
- target-only diagnostic controls
- architecture-near low-rank adapter controls
- replayable same-parent slices
- paired replay stats
- representative locality probes

What is still not claimed:

- blanket superiority over every nearby PEFT design
- transformer-module canonical LoRA superiority, because this parent is not a standard transformer PEFT target
- broad unseen-family generalization

See:

- [EXPERIMENTS.md](EXPERIMENTS.md)

## Does This Prove General Reasoning?

No.

The current public evidence supports:

- no obvious external collapse
- a real auditable board proof
- a replayable gain over the frozen parent

It does not support:

- broad unseen-family generalization
- proof of broad reasoning transfer

Additional release-boundary audit artifacts remain available in raw form under [../results/audit](../results/audit).

## Is There Now Any True Open-Input Demo?

Yes, but it is deliberately scoped.

The repo now publishes:

- a host-side open-input structured JSON demo

That demo is real open input, but narrow:

- free-text prompt in
- structured JSON out
- exact-match and unsafe-guard evaluation

It is not the same thing as:

- open-input MCU deployment

See:

- [OPEN_INPUT_DEMO.md](OPEN_INPUT_DEMO.md)

## Why Is Auditability So Important Here?

Because for constrained edge deployments:

- determinism matters
- postmortem analysis matters
- bounded behavior matters
- honest negative evidence matters

That is why this repo keeps the trust boundary visible instead of hiding it behind one headline score.
