# FAQ

## Is this an LLM?

The most robust public wording for this repository is:

- `sub-1MB language reasoning runtime`

This repository does not present the demo as unrestricted full native LLM execution on MCU.

## Are these numbers actually measured on the board?

Yes.

The board writes its report into a flash `report` partition, and the PC-side script reads that JSON back.

## Why are there two kinds of numbers in this repository?

Because this repository intentionally separates:

- **benchmark capability**
- **board runtime validation**

The benchmark-capability wording is used to describe the public demo model line.

The board-runtime-validation wording is used to describe the exact board-measured execution mode and report files included here.

For this public demo line, the benchmark-capability reference is:

- `IFEval = 0.780037`
- `LogiQA = 0.303738`

The board-side validation files in this repository are reported separately on purpose.

## Is an OLED required?

No.

This public demo only requires:

- `ESP32-C3`
- USB
- Python
- `esptool`

## Is there anything interactive in the public repo?

Yes.

In addition to the audited board-report firmware, the repository also includes an optional `interactive` firmware variant plus a serial helper script.

That interactive variant lets you:

- list the fixed public sample set embedded in the firmware
- inspect a sample by index
- rerun the current public GPU-only or linear+GPU path for that sample

It is still a constrained demo, not a general free-form inference shell.

## Why is IFEval so fast?

Because the public IFEval mode is:

- `compiled_piece_stream_v1`

This is not a conventional autoregressive token-generation speed number.

## Why is LogiQA reported in batches?

Because the public LogiQA mode is:

- `logiqa_batch_compiled_probe_aggregated`

That means the `642` official samples are aggregated from `11` board-side batches.
