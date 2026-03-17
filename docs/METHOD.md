# Method Boundary

This repository publishes a board-proof line and a research reference line. It does not publish the full internal training and materialization stack.

## Current public board mode

The published MCU execution path is:

- `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- `compiled_probe_mode = host_full_exact`

Meaning:

- the official `LogiQA 642` set is represented as `11` fixed board-side batches
- the board executes a compiled fixed-batch path
- for the released board proof, the board-side compiled line reproduces host-full final decisions exactly on those published batches

The aggregate published board result is:

- `249 / 642 = 0.3878504672897196`

## Runtime shape

The current public runtime should be described as:

- flash-resident
- table-driven
- packed artifact structures
- compiled fixed-batch decision path

This is not a public release of unrestricted open-input native inference on `ESP32-C3`.

## Current research capability line

The current scientific surface published in this repository is:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`

That line is host-side and audit-backed. It is related to, but not identical to, the released board proof path.

## What this repository proves

- a current Tiny Expert board line can run on real `ESP32-C3` hardware
- the released board proof is auditable through raw readback JSON
- the board proof is aligned to host-full decisions for the published fixed batches
- the host-side current scientific surface is stronger than the board proof and is separately documented

## What this repository does not prove

- unrestricted general MCU inference
- a full public training or materialization system
- broad general reasoning
- strong hidden-family generalization

The repository is intentionally explicit about those boundaries.
