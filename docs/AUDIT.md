# Audit Notes

The public audit package in this repository now has two parts:

- `board proof audit`
- `host surface audit`

## Board proof audit

The current public board proof is:

- [../results/board_proof/board_runtime_audit_acceptance.json](../results/board_proof/board_runtime_audit_acceptance.json)
- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

Accepted properties:

- `ESP32-C3` flash-resident board run
- aggregate board-proof mode: `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `evaluation_mode = logiqa_batch_compiled_probe`
- `compiled_probe_mode = host_full_exact`
- aggregate result `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`
- raw batch reports published under [../results/board_proof/raw](../results/board_proof/raw)

Important boundary:

- this is a correctness and consistency proof for a fixed-batch compiled line
- it is not a speed-comparable unrestricted runtime benchmark

## Host surface audit

The current research-line evidence is published under:

- [../results/research_line](../results/research_line)
- [../results/audit](../results/audit)

That includes:

- current host surface manifest
- reference status
- guard bundle
- full replay
- integrity
- stack check
- overfit audit
- additional raw release-boundary audits

## Current audit conclusion

The strongest honest current conclusion is:

- no obvious external collapse
- no obvious text-level overlap contamination in the clean holdout path
- board proof is real and auditable
- the repo does not claim broad unseen-family generalization

Additional release-boundary audit artifacts remain available in raw form under [../results/audit](../results/audit).
