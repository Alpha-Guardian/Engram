# Engram

`engram` is a public MCU demo for one very small language runtime line. The point of the repository is not to sell a chip product. The point is to show one concrete, audited example of what our training-and-compilation pipeline can push onto an unusually constrained device.

The public artifact in this repo is a `732,034` byte runtime package running on a commodity `ESP32-C3`. The public benchmark-capability reference for the same demo line is `LogiQA = 0.303738` and `IFEval = 0.780037`. The board-side validation published here is narrower and must be read as such: `LogiQA` is reported as a `logiqa_batch_compiled_probe_aggregated` run, while `IFEval` is reported as an `ifeval_compiled_piece_stream_full` run. That difference in execution mode is why the board-side `LogiQA` number (`177 / 642 = 0.2757009345794392`) is not identical to the host-side benchmark reference (`0.303738`).

Under the hood, this demo is not a conventional dense on-device LLM stack. The board-side path is closer to a flash-resident, table-driven runtime: packed token weights, hashed lookup tables, fixed probe samples, and streaming fold / checksum passes over precompiled structures. That is why the repo separates **benchmark capability** from **board runtime validation** so explicitly. We want people to see the actual execution boundary rather than guess at it.

## Quick facts

| Item | Value |
|---|---|
| Target board | `ESP32-C3` |
| Public artifact | `chip_suite_surface_round2_q4_tgz_expack_rgz.json` |
| Artifact size | `732,034 bytes` |
| Artifact SHA256 | `05bd39e2b73d0c15e18e867e2a01c3a51f474e4a590bd5f3838427a2dadadfce` |
| Benchmark capability | `LogiQA = 0.303738`, `IFEval = 0.780037` |
| Board validation | `LogiQA 642 = 177 / 642 = 0.2757009345794392` |
| Board validation | `IFEval 541 compiled-piece-stream, checksum aligned` |
| IFEval board throughput | `189,918.922 tokens/s` |

Reference for the benchmark-capability numbers:

- [results/benchmark_reference/20260309_185732_876699_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_freeze_status.json](results/benchmark_reference/20260309_185732_876699_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_freeze_status.json)

## What is actually running on the board

The public board-side paths in this repository are:

- `LogiQA`: `logiqa_batch_compiled_probe_aggregated`
- `IFEval`: `ifeval_compiled_piece_stream_full`

The shortest way to describe the implementation is:

- the runtime artifact stays flash-resident
- the board works over packed tables and fixed probe structures
- `LogiQA` uses a compiled probe path with sparse weights, hashed features, and fixed retrieval deltas
- `IFEval` uses `compiled_piece_stream_v1`, which is a precompiled piece stream plus streaming fold / token-count / checksum passes

So this repository is **not** presenting unrestricted native LLM generation on MCU. It is presenting a constrained but real board-measured language runtime line whose execution path is documented and auditable.

## Why the LogiQA numbers differ

Two different `LogiQA` numbers appear in this repository:

- `0.303738`: the host-side benchmark-capability reference for the public demo line
- `0.2757009345794392`: the board-side audited result published here

They differ because they are not the same evaluation mode.

The host-side number comes from the benchmark reference file linked above. The board-side number comes from the published `logiqa_batch_compiled_probe_aggregated` path, which is an audited aggregate over `11` board-side batches. That aggregate is useful because it is reproducible and board-measured, but it should not be confused with a single-firmware one-shot rerun of the host benchmark.

## Optional interactive demo firmware

In addition to the audited reproduction firmware, this repository also includes an optional `interactive` firmware variant.

That variant is there for technical readers who want something more direct than a static report readback:

- list the fixed public probe samples currently embedded in the firmware
- inspect a sample by index
- run the current public GPU-only or linear+GPU decision path for that sample over serial

It is still a constrained public demo, not a general open-input inference runtime, and it is not the audited firmware used for the published board-score summaries.

## What is included

- public demo firmware binaries
- flashing and report-read scripts
- an optional interactive serial demo tool
- audited summaries
- raw board reports for the published board-side validation
- reproduction notes
- method-boundary notes

## What is not included

- training pipeline
- training data pipeline
- weight-generation scripts
- private training recipes
- internal research workflow

## What you can reproduce directly

With the default audited firmware in this repository, you can directly reproduce:

- the current public `IFEval 541` board-report path
- the board report format
- heap and artifact-access measurements
- artifact identity checks through `artifact_sha256`
- the optional interactive sample browser and fixed-sample command shell, if you flash the `interactive` variant

What you **cannot** reproduce with a single flash from this repository:

- the full `LogiQA 642` score as a one-shot single-firmware run

That public `LogiQA 642` number is an audited aggregate over `11` board-side batches. The raw batch reports are included in [results/raw](results/raw).

## How to read this demo

If you come from embedded systems, the important point is that this repo shows a flash-resident, auditable language-task runtime under severe memory and compute limits.

If you come from model training, the important point is that a public demo line can still retain nontrivial benchmark-level behavior under a very small runtime and storage budget.

For us, the board is a physical proof surface for the training-and-compilation pipeline, not the final destination of the research line.

## Research outlook

This demo is only one public branch of a broader research direction.

The longer-term technical questions we care about include:

- how far language-task capability can be pushed by increasing logic density rather than only scaling parameter count
- how much semantic structure can be preserved per unit of parameter budget
- how tiny offline language runtimes can become reusable building blocks for hardware-constrained language systems
- how domain-specific semantic understanding can be compiled into hardware-executable runtimes under very different memory and compute budgets
- how lessons from highly compressed runtimes can feed back into future high-efficiency large-model training and inference architectures

In other words, the `ESP32-C3` here is not the destination. It is a deliberately harsh test bench for a broader line of model R&D.

## Hardware and runtime footprint

Observed public board range:

- `Sketch Size`: `1,080,208 bytes ~ 1,259,376 bytes`
- `Free Heap`: `309,892 bytes ~ 310,816 bytes`
- `Min Free Heap`: `306,760 bytes ~ 309,464 bytes`
- `artifact CRC board time`: `435 ms ~ 473 ms`

## Quick start

See [docs/REPRODUCE.md](docs/REPRODUCE.md) for the full guide.

Short version:

1. Prepare an `ESP32-C3` board on Windows.
2. Install `Python 3`.
3. Install `esptool`.
4. Optional, for the interactive shell: install `pyserial`.
5. Flash the board:

```bash
py scripts/flash_firmware.py COMx
```

For the optional interactive variant:

```bash
py scripts/flash_firmware.py COMx --variant interactive
```

6. Read back the board report with validation:

```bash
py scripts/read_board_report.py COMx --expect-mode ifeval_compiled_piece_stream_full --expect-artifact-sha256 05bd39e2b73d0c15e18e867e2a01c3a51f474e4a590bd5f3838427a2dadadfce
```

7. Compare the returned JSON against the audited files in [results](results).

For the optional interactive shell:

```bash
py -m pip install pyserial
py scripts/serial_demo.py COMx
```

## Repository layout

- [firmware](firmware)
  - public demo firmware binaries, including `interactive`
- [scripts](scripts)
  - flashing, board-report readback, and interactive serial scripts
- [results](results)
  - audited summaries, benchmark reference, and raw board reports
- [docs](docs)
  - reproduction notes, audit notes, FAQ, and the HN draft

Note: GitHub may classify this repository as `Python` because the public repo mainly contains flashing, readback, and evaluation scripts. The board-side runtime is delivered here as firmware binaries rather than as a full public source release.

## Scope and wording

These are real board-measured results, but the execution modes matter:

- `LogiQA` is published here as a `batch-compiled probe aggregate`
- `IFEval` is published here as a `compiled piece stream full run`

This repository demonstrates:

- a working language-task runtime on `ESP32-C3`
- board-measured readback from flash
- auditable alignment between board output and host-side references
- a clean separation between benchmark-capability claims and board-runtime claims
- a minimal fixed-sample interactive shell for technical inspection

This repository does **not** claim:

- unrestricted native LLM generation on MCU
- direct one-shot execution of a general runtime artifact as-is on the board
- single-firmware one-shot reproduction of the full `LogiQA 642` aggregate

For precise wording and audit boundaries:

- [docs/METHOD.md](docs/METHOD.md)
- [docs/AUDIT.md](docs/AUDIT.md)
- [docs/FAQ.md](docs/FAQ.md)
