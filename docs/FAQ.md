# FAQ

## Is this an LLM?

The most robust public wording for this repository is:

- `sub-1MB language reasoning runtime`

This repository does not present the demo as unrestricted full native LLM execution on MCU.

## Are these numbers actually measured on the board?

Yes.

The board writes its report into a flash `report` partition, and the PC-side script reads that JSON back.

## Is this demo fully offline?

Yes, in the sense that the public firmware runs locally on the `ESP32-C3` and the reported board results are read back from the board itself.

The public repo does **not** require a cloud service, remote API, or host-side online inference service during the published board run.

At the same time, the execution mode still matters:

- the public `IFEval` path is a compiled piece stream executed on the board
- the public `LogiQA` board result is an audited aggregate over compiled board-side batches

So the demo is offline, but it should not be described as unrestricted open-input native LLM generation on the MCU.

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

## Why does LogiQA have two different numbers?

Because the repository publishes two different layers on purpose:

- host-side benchmark capability for the public demo line
- board-side validation under a narrower execution mode

For `LogiQA`, that means:

- `0.303738` is the host-side benchmark-capability reference
- `0.2757009345794392` is the published board-side audited result

The board-side number comes from `logiqa_batch_compiled_probe_aggregated`, which is an audited aggregate over `11` board-side batches. It should not be read as the same thing as a one-shot rerun of the host benchmark.

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

## What actually runs on the board?

The shortest accurate description is:

- a flash-resident, table-driven runtime
- packed token-weight and lookup structures
- fixed probe samples and compiled execution paths
- streaming fold / token-count / checksum style passes for the published `IFEval` board mode

This is why the repo keeps saying **benchmark capability** and **board runtime validation** separately. The point is to be explicit about the execution boundary rather than blur it.

## Why is IFEval so fast?

Because the public IFEval mode is:

- `compiled_piece_stream_v1`

This is not a conventional autoregressive token-generation speed number.

## Why is LogiQA reported in batches?

Because the public LogiQA mode is:

- `logiqa_batch_compiled_probe_aggregated`

That means the `642` official samples are aggregated from `11` board-side batches.
