# Reproduction Guide

## 1. Requirements

- Windows
- Python 3
- an `ESP32-C3` board
- a data-capable USB cable

Install `esptool`:

```bash
py -m pip install esptool
```

## 2. Find The Serial Port

Connect the board and identify the serial port in Device Manager, for example:

- `COM3`
- `COM5`

The examples below use `COM3`.

## 3. Flash The Published Firmware

From the repository root:

```bash
py scripts/flash_firmware.py COM3
```

Default flash layout:

- `0x0` -> `bootloader.bin`
- `0x8000` -> `partitions.bin`
- `0xe000` -> `boot_app0.bin`
- `0x10000` -> `firmware.bin`

## 4. Read Back The Board Report

After flashing and reset:

```bash
py scripts/read_board_report.py COM3 --expect-mode logiqa_batch_compiled_probe --expect-artifact-sha256 626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d
```

Mode note:

- this readback checks one default single-batch report (`logiqa_batch_compiled_probe`)
- the published `642` aggregate summary is reported as `logiqa_batch_compiled_probe_aggregated`

This reads JSON from the board `report` partition.

The expected default report is:

- [../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json](../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json)

## 5. Verify The Main Board Fields

Core fields:

- `artifact_name`
- `artifact_sha256`
- `evaluation_mode`
- `logiqa_compiled_probe`
- `free_heap_bytes`
- `min_free_heap_bytes`
- `artifact_crc32`

Task-specific fields:

- `linear_gpu_probe_samples`
- `linear_gpu_probe_correct`
- `linear_gpu_probe_expected_match`
- `linear_gpu_probe_host_full_match`
- `linear_gpu_probe_first_scores`

## 6. Understand The Aggregate Board Proof

The repository publishes the full board proof separately:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

Important scope note:

- the default firmware reproduces one published fixed batch board report
- the full `LogiQA 642` board proof is the aggregate over the included `11` raw board batches
- those raw board reports are published under [../results/board_proof/raw](../results/board_proof/raw)

## 7. Reproduce MCU Open-Input Micro-Loop

Flash the published MCU open-input firmware:

```bash
py scripts/flash_open_input_firmware.py COM3
```

Run the open-input board evaluation:

```bash
py scripts/run_mcu_open_input_demo.py --port COM3
```

Expected output file:

- [../results/open_input_demo/mcu_open_input_demo.json](../results/open_input_demo/mcu_open_input_demo.json)
- [../results/open_input_demo/mcu_open_input_board_report.json](../results/open_input_demo/mcu_open_input_board_report.json)

Expected acceptance fields:

- `summary.exact_match_rate = 1.0`
- `summary.nonempty_rate = 1.0`
- `summary.stability_probe.stability_rate = 1.0`
- `summary.gates.all_pass = true`

## 8. Verify The Public Bundle

The repository also publishes a local verification helper for the public-safe experiment and document bundle:

```bash
python3 scripts/verify_public_bundle.py
```

This checks:

- required mechanism and experiment docs exist
- generated experiment summaries match their manifest hashes
- the current surface row agrees with the published research manifest

## 9. Compare Against The Research Line

Use:

- [../results/research_line/current_host_surface_manifest.json](../results/research_line/current_host_surface_manifest.json)
- [../results/experiments/main_table.json](../results/experiments/main_table.json)
- [../results/experiments/ablations.json](../results/experiments/ablations.json)

This lets you compare:

- frozen parent
- exact no-trunk ablation
- same-parent contextual surfaces
- current host-side accepted surface
- board proof line

## 10. Verify File Integrity

Use `sha256sums.txt` in the repository root to verify:

- documentation files
- scripts
- firmware binaries
- result JSON files

## 11. Maintainer Refresh

Maintainers working inside the full monorepo can refresh the public-safe experiment bundle with:

```bash
python3 scripts/run_public_logiqa_controls.py
python3 scripts/run_public_causal_sequence.py
python3 scripts/run_public_open_input_demo.py
py scripts/run_mcu_open_input_demo.py --port COM3
python3 scripts/export_block_inventory.py
python3 scripts/build_public_experiment_tables.py
python3 scripts/verify_public_bundle.py
```

This path depends on the private workspace artifacts outside `github_demo`, so it is a maintainer path rather than a standalone public reproduction path.

`run_public_logiqa_controls.py` now regenerates:

- route-disabled, topology-removal, and depth-one current-surface controls
- target-only diagnostic controls
- retrieval-only and lexical-only classic baselines
- same-parent trained linear-readout control
- same-parent trained BitFit option-bias control
- same-parent trained LoRA-style hash-delta control
- same-parent trained low-rank adapter baseline
- same-parent trainable-budget-matched LoRA-style baseline
- same-parent trainable-budget-matched low-rank adapter baseline
- same-parent low-rank adapter-style controls

`run_public_causal_sequence.py` now regenerates:

- forward-addition three-family causal checkpoints
- order-swap three-family checkpoints
- reverse-removal checkpoints from the current surface

`run_public_open_input_demo.py` now regenerates:

- the host-side structured open-input exact-match report
- the host-side runtime proxy report

`run_mcu_open_input_demo.py` now regenerates:

- the board-side MCU open-input micro-loop exact-match report
- split-level and stability evidence for the published MCU taskset

## 12. Detailed References

For deeper reference, see:

- [BOARD_METRICS.md](BOARD_METRICS.md)
- [METHOD.md](METHOD.md)
- [EXPERIMENTS.md](EXPERIMENTS.md)
- [OPEN_INPUT_DEMO.md](OPEN_INPUT_DEMO.md)
