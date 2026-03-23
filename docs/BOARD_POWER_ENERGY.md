# Board Power and Energy

This note prepares a minimal power and energy extension for the public `ESP32-C3` evidence stack.

It does not claim new numbers by itself. It defines a repeatable measurement protocol so that board-level power can be added without redesigning the experiment at the last minute.

## What To Measure

If you only have time for one power pass, measure these three windows:

1. `board_proof_idle`
   - board-proof firmware flashed
   - board fully booted and idle
   - no readback command running
2. `board_proof_readback`
   - board-proof firmware flashed
   - run one published readback command
   - this captures the fixed published audit path
3. `mcu_open_input_36cmd`
   - open-input demo firmware flashed
   - run the public `36`-command MCU demo
   - this gives a meaningful interactive path with real latency

These three windows are enough to answer the most likely reviewer question:

`What is the board-side energy cost of the audited path, and what is the cost of the narrow interactive path?`

## Hardware Assumptions

Use any external instrument that can export timestamped current or power samples to CSV, for example:

- a USB power meter with CSV export
- an inline shunt logger
- a current monitor board
- a lab power supply with logging enabled

Recommended sample rate:

- preferred: `>= 1 kHz`
- acceptable for a first paper pass: `>= 100 Hz`

Minimum columns needed in the CSV:

- time
- current or power
- voltage if power is not already logged

The summarizer script accepts common variants such as:

- `time_s`, `time_ms`
- `current_ma`, `current_a`, `current_ua`
- `voltage_v`
- `power_mw`, `power_w`

## Commands

Board-proof idle:

```bash
py scripts/flash_firmware.py COM3
```

Board-proof readback:

```bash
py scripts/read_board_report.py COM3 --expect-mode logiqa_batch_compiled_probe --expect-artifact-sha256 626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d
```

MCU open-input:

```bash
py scripts/flash_open_input_firmware.py COM3
py scripts/run_mcu_open_input_demo.py --port COM3
```

If you want precise host-side timestamps for alignment with the external logger, wrap each command with:

```bash
python3 scripts/run_power_phase.py --label mcu_open_input_36cmd --output results/board_power/mcu_open_input_36cmd_phase.json -- py scripts/run_mcu_open_input_demo.py --port COM3
```

## Summarize CSV Logs

Example for a readback window that spans `12.40s` to `16.85s` in the raw logger CSV:

```bash
python3 scripts/summarize_power_csv.py \
  --csv path/to/logger_export.csv \
  --label board_proof_readback \
  --start-s 12.40 \
  --end-s 16.85 \
  --output results/board_power/board_proof_readback_power.json \
  --notes "board-proof firmware, published readback command"
```

Example for the `36`-command open-input demo:

```bash
python3 scripts/summarize_power_csv.py \
  --csv path/to/logger_export.csv \
  --label mcu_open_input_36cmd \
  --start-s 20.10 \
  --end-s 24.05 \
  --output results/board_power/mcu_open_input_36cmd_power.json \
  --notes "open-input demo firmware, published 36-command taskset"
```

## Result Files

Store generated summaries under:

- [../results/board_power/](../results/board_power/)

Suggested filenames:

- `board_proof_idle_power.json`
- `board_proof_readback_power.json`
- `mcu_open_input_36cmd_power.json`

## Table To Paste Into The Paper

Once the three JSON summaries exist, the paper can add one compact table like this:

| Window | Avg current (mA) | Avg power (mW) | Energy (mJ) | Duration (s) |
|---|---:|---:|---:|---:|
| board-proof idle | `...` | `...` | `...` | `...` |
| board-proof readback | `...` | `...` | `...` | `...` |
| MCU open-input 36cmd | `...` | `...` | `...` | `...` |

Recommended text:

`As a lightweight power extension, we measured one idle board-proof window, one published readback window, and one 36-command MCU open-input run with an external inline logger. The board-proof path remains a correctness-first compiled executor, while the open-input loop provides the more natural interactive energy point.`

## Interpretation Boundary

Keep the power claim narrow:

- do not turn the board-proof path into a real-time benchmark
- do not compare the fixed compiled board-proof path directly to open-input token generation
- do report idle, readback, and open-input as distinct operating modes

That is enough to strengthen the embedded evaluation without changing the paper's current claim boundary.
