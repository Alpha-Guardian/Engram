# Reproduction Guide

## 1. Requirements

- Windows
- Python 3
- An `ESP32-C3` board
- A data-capable USB cable

Install `esptool`:

```bash
py -m pip install esptool
```

Optional, for the interactive sample shell:

```bash
py -m pip install pyserial
```

## 2. Find the serial port

Connect the board and check Device Manager for the serial port, for example:

- `COM3`
- `COM5`

The commands below use `COM3` as an example.

## 3. Flash the firmware

From the repository root:

```bash
py scripts/flash_firmware.py COM3
```

Optional interactive variant:

```bash
py scripts/flash_firmware.py COM3 --variant interactive
```

Default flash layout:

- `0x0` -> `bootloader.bin`
- `0x8000` -> `partitions.bin`
- `0xe000` -> `boot_app0.bin`
- `0x10000` -> `firmware.bin`

## 4. Read the board report

After flashing and reset:

```bash
py scripts/read_board_report.py COM3 --expect-mode ifeval_compiled_piece_stream_full --expect-artifact-sha256 05bd39e2b73d0c15e18e867e2a01c3a51f474e4a590bd5f3838427a2dadadfce
```

This reads a JSON report back from the board `report` partition.

The optional verification flags are recommended for public reproduction because they reduce the chance of accidentally accepting a stale report:

- `--expect-mode`
- `--expect-artifact-sha256`

## 4b. Optional interactive sample shell

If you flashed the `interactive` variant, you can also open a small serial command shell:

```bash
py scripts/serial_demo.py COM3
```

Useful commands:

- `HELP`
- `INFO`
- `LIST GPU`
- `SHOW GPU 0`
- `RUN GPU 0`
- `LIST LINEAR`
- `SHOW LINEAR 0`
- `RUN LINEAR 0`
- `REPORT`

This shell does not turn the board into a general open-input inference runtime.
It exposes a fixed public sample set so technical readers can inspect and rerun the public decision path more directly.
It is separate from the audited firmware used for the published board-score summaries.

## 5. Check the result fields

Main fields to verify:

- `artifact_name`
- `artifact_sha256`
- `evaluation_mode`
- `free_heap_bytes`
- `min_free_heap_bytes`
- `artifact_crc32`

Task-specific fields:

### LogiQA

- `linear_gpu_probe_samples`
- `linear_gpu_probe_correct`
- `linear_gpu_probe_host_full_match`
- `linear_gpu_probe_ms`

### IFEval

- `ifeval_probe_samples`
- `ifeval_probe_nonempty`
- `ifeval_probe_output_tokens`
- `ifeval_probe_ms`
- `ifeval_probe_checksum`

## 6. Compare with the public audited results

Use these files:

- [results/esp32c3_logiqa642_audited_summary.json](../results/esp32c3_logiqa642_audited_summary.json)
- [results/esp32c3_ifeval541_compiled_audited_summary.json](../results/esp32c3_ifeval541_compiled_audited_summary.json)
- [results/board_runtime_audit_acceptance.json](../results/board_runtime_audit_acceptance.json)

Important scope note:

- the single public firmware in this repository directly reproduces the public `IFEval 541` board report path
- the public `LogiQA 642` result is an audited aggregate from `11` board-side batches
- those per-batch raw reports are included in `results/raw`

## 7. File integrity

Use `sha256sums.txt` in the repository root to verify:

- documentation files
- scripts
- firmware files
- result JSON files
