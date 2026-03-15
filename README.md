# Engram

`engram` is a public MCU demo that packages a sub-1MB language runtime for a commodity `ESP32-C3`.

Engram is not just a compression project. The broader system we are building is a training-and-compilation stack for tiny offline language runtimes that can be specialized for constrained hardware while preserving as much task logic as possible.

This repository is meant to do one job well:

- show a real board-measured language-task runtime on a low-cost MCU
- publish the exact public demo firmware
- publish audited result files
- make the public demo reproducible enough for technical readers

It is **not** a release of the training pipeline, the private training recipes, or the internal weight-generation workflow.

## Why this repository exists

Most small-model or edge-model demos stop at one of these stages:

- benchmark-only claims with no board evidence
- board evidence with no reproducible artifact
- firmware drops with no audit trail

This repository is intended to close that gap for one public demo line from `engram`.

## What Engram builds

Engram's core direction is:

- train task-specific tiny language runtimes
- compile them into deployable edge artifacts
- ship them onto constrained offline hardware
- study how much usable language-task logic can survive under extreme parameter and memory pressure

The public repository here is one deployment demo from that system, not the full internal training stack.

## What this public demo proves

This repository is meant to show three things clearly:

- Engram can train a very small language-task runtime with meaningful benchmark capability
- Engram can compile that runtime into a deployable MCU artifact
- Engram can validate the result on a real `ESP32-C3` with board-measured audit trails
- Engram can retain nontrivial language-task behavior at a level of logic density that would normally be dismissed as too small to matter

## Why this demo matters

The main point of this repository is model R&D, not a chip product.

We use `ESP32-C3` here because it is a harsh physical constraint:

- very little memory
- very little compute
- very little room for waste

If a language-task runtime can survive under those conditions, that says something about the efficiency of the underlying training-and-compilation pipeline.

This is why we use the board as a test bench rather than a product story: the point is to pressure-test model efficiency under unusually harsh physical limits.

## TL;DR

### Public demo model capability

This public demo line corresponds to:

- `LogiQA = 0.303738`
- `IFEval = 0.780037`

Reference:

- [results/benchmark_reference/20260309_185732_876699_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_freeze_status.json](results/benchmark_reference/20260309_185732_876699_v247r_true_retrievalweight2375_logiqa112_basecountdamp05_research_handoff_freeze_status.json)

### Public board runtime validation

The exact board-measured validation published in this repository is:

- `ESP32-C3`
- artifact: `chip_suite_surface_round2_q4_tgz_expack_rgz.json`
- artifact size: `732,034 bytes`
- artifact SHA256: `05bd39e2b73d0c15e18e867e2a01c3a51f474e4a590bd5f3838427a2dadadfce`

Board-side validation results:

- `LogiQA 642`
  - mode: `logiqa_batch_compiled_probe_aggregated`
  - `177 / 642`
  - accuracy `0.2757009345794392`
  - total time `91779 ms`
  - throughput `6.995064230379499 samples/s`
  - host-path match `642 / 642`

- `IFEval 541`
  - mode: `ifeval_compiled_piece_stream_full`
  - encoding: `compiled_piece_stream_v1`
  - samples `541`
  - non-empty outputs `541`
  - output tokens `42162`
  - total time `222 ms`
  - throughput `189918.922 tokens/s`
  - host alignment: `samples_match = true`, `nonempty_match = true`, `output_tokens_match = true`, `checksum_match = true`

### Optional interactive demo firmware

In addition to the audited reproduction firmware, this repository also includes an optional `interactive` firmware variant.

That variant is intended for technical readers who want something more useful than a static report readback:

- list the fixed public probe samples currently embedded in the firmware
- inspect a sample by index
- run the current public GPU-only or linear+GPU decision path for that sample over serial

It is still a constrained public demo, not a general open-input inference runtime.
It is also not the audited firmware used for the published board-score summaries.

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

With the single public firmware in this repository, you can directly reproduce:

- the current public `IFEval 541` board-report path
- the board report format
- heap and artifact-access measurements
- artifact identity checks through `artifact_sha256`
- the optional interactive sample browser and fixed-sample command shell, if you flash the `interactive` variant

What you **cannot** reproduce with a single flash from this repository:

- the full `LogiQA 642` score as a one-shot single-firmware run

That public `LogiQA 642` number is an audited aggregate over `11` board-side batches. The raw batch reports are included in [results/raw](results/raw).

## Technical outlook

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
