# HN Draft

## Candidate titles

- `Show HN: An offline Tiny Expert board proof on ESP32-C3`
- `Show HN: A table-driven edge reasoning runtime with audited ESP32-C3 results`
- `Show HN: An auditable Tiny Expert line for extreme edge constraints`

## Short post

We built a public Tiny Expert board proof that runs on a commodity `ESP32-C3`.

The current board-proof result in the repo is:

- `LogiQA 642 = 249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

The current host-side scientific surface published alongside it is:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

This is not a public release of unrestricted on-device LLM inference. The board line is a fixed-batch compiled proof, and the repo is explicit about that boundary.

What we care about is a different question:

- can useful benchmark capability be distilled into a very small, offline, auditable edge runtime instead of only being served from large cloud models?

The repo includes:

- firmware binaries
- board raw reports and aggregate summary
- current research-line manifest
- replay, integrity, overfit, and hidden-family forensic audit evidence

Most interestingly, the project is honest about where the evidence is strong and where it is weak:

- no obvious external collapse
- but hidden-family generalization is still weak

Repo:

- `README.md`
- `docs/TRUST_AND_AUDIT.md`
- `results/board_proof`
