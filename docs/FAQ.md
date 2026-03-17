# FAQ

## Is this an LLM?

Not in the usual public sense.

The most accurate public wording is:

- `offline Tiny Expert board proof`
- `task-specialized, table-driven edge reasoning runtime`

This repo does not present the current board line as unrestricted open-input native LLM inference on MCU.

## Is this just a lookup table?

The runtime is table-driven at execution time. That is intentional.

The technical question here is not "can we hide a big dense model behind a tiny label." The question is:

- can benchmark-relevant reasoning capability be distilled into a hardware-executable, auditable, flash-resident Tiny Expert under extreme edge constraints?

So yes, runtime execution is structured and table-driven. That is a feature, not a contradiction.

## Are these numbers actually measured on a real board?

Yes.

The published board proof is a real `ESP32-C3` run with raw JSON read back from the board `report` partition.

## What is the current board-proof result?

The current public board proof is:

- `LogiQA 642 = 249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

Source:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

## Why are there two kinds of numbers?

Because this repo separates:

- `public board proof`
- `research capability line`

Current research capability line:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

Current board proof:

- fixed-batch compiled board result `249 / 642 = 0.3878504672897196`

They are related, but they are not the same layer.

## Why is the board number slightly lower than the research line?

Because the board line is a constrained fixed-batch compiled proof, while the research line is the current host-side audited scientific surface.

The board result proves:

- real MCU execution
- exact fixed-batch host-full alignment

The research line proves:

- the broader current official and external capability state

## Is this fully offline?

Yes for the published board proof.

The firmware runs locally on `ESP32-C3`. The reported board result is read back from the board itself. No cloud inference service is required for the published board proof.

## Why not just quantize a bigger LLM?

That is a different approach.

This line is not trying to preserve a broad open-domain model. It is trying to distill task capability into:

- smaller memory
- lower power
- stricter auditability
- better deployment stability

## Does this prove general reasoning?

No.

The current public evidence supports:

- no obvious external collapse
- a real auditable board proof

It does **not** support:

- strong hidden-family generalization
- proof of broad reasoning transfer

## Is this overfit to LogiQA?

The current evidence says:

- no obvious text-level leakage
- no obvious external collapse on `external_dev` and `external_blind`
- clean `holdout2 = 0.400000`
- `blind_remainder = 0.448133`

But the hidden-family forensic audit remains weak:

- hidden-family holdout `0 / 85`

So the strongest honest statement is:

- no obvious external overfit collapse
- but hidden-family generalization is still not strong

## Why is hidden-family performance still weak?

Because current gains are much stronger on the visible residual surface than on frozen hidden logical families.

This is precisely why the repository publishes the forensic audit instead of hiding it.

## Why is auditability such a big deal here?

For many edge deployments:

- being inspectable matters more than being broadly eloquent
- deterministic failure analysis matters more than open-ended generation
- constrained offline execution matters more than a bigger generic model

That is why this repo emphasizes trust and boundary disclosure so heavily.
