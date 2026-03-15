# HN Draft

## Candidate titles

- `Show HN: A sub-1MB language runtime on ESP32-C3`
- `Show HN: Board-measured language-task runtime on an ESP32-C3`
- `Show HN: A sub-1MB ESP32-C3 language runtime with audited benchmark and board results`

## Body draft

We built a public MCU demo from `engram`: a sub-1MB language runtime running on a commodity ESP32-C3.

The goal of this repository is simple:

- publish a real board-measured language-task runtime
- publish the exact public demo firmware
- publish audited result files
- make the public demo reproducible enough for technical readers

This repository does **not** publish the training pipeline or the private weight-generation workflow.

### Public demo model capability

This public demo line corresponds to:

- `LogiQA = 0.303738`
- `IFEval = 0.780037`

Reference:

- `results/benchmark_reference/20260309_185732_876699_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_freeze_status.json`

### Public board runtime validation

The exact board-side validation published in this repository is:

- `ESP32-C3`
- artifact size: `732,034 bytes`
- artifact SHA256: `05bd39e2b73d0c15e18e867e2a01c3a51f474e4a590bd5f3838427a2dadadfce`

Board-side validation files included here:

- `LogiQA 642`
  - mode: `logiqa_batch_compiled_probe_aggregated`
  - `177 / 642`
  - accuracy `0.2757009345794392`
  - total time `91779 ms`
  - throughput `6.995064230379499 samples/s`

- `IFEval 541`
  - mode: `ifeval_compiled_piece_stream_full`
  - encoding: `compiled_piece_stream_v1`
  - `541` samples
  - `42162` output tokens
  - `222 ms`
  - `189918.922 tokens/s`
  - host alignment is fully audited

### What can be reproduced directly

With the single public firmware in this repository, a reader can directly reproduce:

- the public `IFEval 541` board-report path
- the board report format
- heap and artifact-access measurements
- artifact identity checks through `artifact_sha256`

### Important scope note

- `LogiQA` here is published as an audited aggregate over `11` board-side batches
- `IFEval` here is published as a compiled piece stream full run
- we do **not** present this as unrestricted native LLM generation on MCU
- we do **not** present the full `LogiQA 642` aggregate as a single-firmware one-shot reproduction

### Repo contents

- public firmware binaries
- flashing and board-report readback scripts
- audited summaries
- raw board reports
- reproduction notes
- method-boundary notes
