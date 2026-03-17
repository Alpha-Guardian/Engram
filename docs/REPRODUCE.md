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

## 2. Find the serial port

Connect the board and identify the serial port in Device Manager, for example:

- `COM3`
- `COM5`

The examples below use `COM3`.

## 3. Flash the published firmware

From the repository root:

```bash
py scripts/flash_firmware.py COM3
```

Default flash layout:

- `0x0` -> `bootloader.bin`
- `0x8000` -> `partitions.bin`
- `0xe000` -> `boot_app0.bin`
- `0x10000` -> `firmware.bin`

## 4. Read back the board report

After flashing and reset:

```bash
py scripts/read_board_report.py COM3 --expect-mode logiqa_batch_compiled_probe --expect-artifact-sha256 626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d
```

This reads JSON from the board `report` partition.

The expected result for the published default firmware is:

- [../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json](../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json)

## 5. Verify the main fields

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

## 6. Understand the aggregate board proof

The repository publishes the full board proof separately as an audited aggregate:

- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)

Important scope note:

- the default firmware reproduces one published fixed batch board report
- the full `LogiQA 642` board proof is the aggregate over the included `11` raw board batches
- those raw board reports are published under [../results/board_proof/raw](../results/board_proof/raw)

## 7. Compare against the current scientific surface

Use:

- [../results/research_line/current_scientific_surface_manifest.json](../results/research_line/current_scientific_surface_manifest.json)
- [../results/research_line/current_scientific_surface_reference_status.json](../results/research_line/current_scientific_surface_reference_status.json)

This lets you compare:

- board proof line
- current host-side research capability line

## 8. Verify file integrity

Use `sha256sums.txt` in the repository root to verify:

- documentation files
- scripts
- firmware binaries
- result JSON files

## 9. Detailed board metrics

For the consolidated hardware, artifact, heap, probe, checksum, and aggregate board-proof metrics, see:

- [BOARD_METRICS.md](BOARD_METRICS.md)
