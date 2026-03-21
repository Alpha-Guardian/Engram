# Open-Input Roadmap

The current board proof is a bounded crystallization proof. It is not the final open-input deployment claim.

## Current Boundary

Current public board mode:

- aggregate board-proof summary mode: `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `evaluation_mode = logiqa_batch_compiled_probe`
- `compiled_probe_mode = host_full_exact`

Meaning:

- fixed published batches
- exact host-full reproduction on those batches
- real board execution

It does not mean unrestricted open-input reasoning on MCU.

## Delivered Phase 0

The repo now already includes a host-side open-input structured loop:

- [OPEN_INPUT_DEMO.md](OPEN_INPUT_DEMO.md)
- [../results/open_input_demo/host_open_input_demo.json](../results/open_input_demo/host_open_input_demo.json)

That phase proves:

- real open text input
- fixed structured JSON output
- explicit unsafe-guard behavior

## Delivered Phase 1

The repo now also includes a board-side open-input micro-loop:

- [OPEN_INPUT_DEMO.md](OPEN_INPUT_DEMO.md)
- [../results/open_input_demo/mcu_open_input_demo.json](../results/open_input_demo/mcu_open_input_demo.json)
- [../results/open_input_demo/mcu_open_input_taskset_v1.jsonl](../results/open_input_demo/mcu_open_input_taskset_v1.jsonl)

This phase proves:

- real free-text input on `ESP32-C3`
- deterministic normalization output on board
- exact-match and stability evidence on the published micro taskset

This is still a narrow unit-normalization loop, not broad open-domain reasoning.

## Next Public Upgrade

The next meaningful upgrade should broaden within constraints while keeping the claim boundary explicit.

Recommended shape:

- small task scope
- real open text input
- explicit constrained output contract
- explicit safety or guard semantics
- repeatable board metrics and acceptance gates

## Why Separate This From The Current Board Proof

Because the current artifact proves crystallization correctness, not open-input deployment.

If those two claims are mixed together, the board result becomes easy to overstate. Keeping them separate preserves trust.

## Suggested Evaluation For Future Upgrades

- schema pass rate
- decision accuracy
- unsafe-guard success rate
- repeated-input stability
- paraphrase robustness
- board latency
- memory footprint

## Public Claim Boundary Now

The strongest honest board claims are now:

- a real `ESP32-C3` fixed-batch bounded artifact derived from the accepted host-side surface
- a real `ESP32-C3` narrow open-input micro-loop with exact-match and stability evidence

And still not:

- unrestricted broad MCU open-input reasoning
