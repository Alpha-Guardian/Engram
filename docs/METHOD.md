# Method Boundary

This repository publishes a **board-side demo runtime**, not a full training system.

## Current board execution modes

### LogiQA

- Mode: `logiqa_batch_compiled_probe_aggregated`
- Meaning: the `642` official samples are split into `11` batches
- Each batch is built and flashed separately
- The final score is the aggregate across these board runs
- The single public firmware in this repository is not a one-shot reproducer for that full aggregate

### IFEval

- Mode: `ifeval_compiled_piece_stream_full`
- Encoding: `compiled_piece_stream_v1`
- Meaning: the board executes a compiled piece stream and reports aggregate output statistics

## What this demo proves

- `ESP32-C3` can host a sub-1MB language runtime demo
- board reports can be read back from flash
- board results can be aligned exactly with host-side reference data
- the reported numbers are auditable
- a separate public interactive variant can expose fixed embedded samples over serial for inspection

## What this demo does not prove

- unrestricted native LLM generation on `ESP32-C3`
- public release of the training pipeline
- public release of the weight-generation process

## Why this boundary matters

Public demos are easiest to attack when they:

- overstate a real but narrower result
- present a reproducible demo as a general full system

This repository is intentionally explicit about that boundary.
