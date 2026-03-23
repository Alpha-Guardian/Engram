# Board Power Results

This directory is reserved for board-level current, power, and energy summaries.

Suggested contents:

- `board_proof_idle_power.json`
- `board_proof_readback_power.json`
- `mcu_open_input_36cmd_power.json`
- matching `*_phase.json` timestamp files from `scripts/run_power_phase.py`

Use [../../docs/BOARD_POWER_ENERGY.md](../../docs/BOARD_POWER_ENERGY.md) for the measurement protocol and [../../scripts/summarize_power_csv.py](../../scripts/summarize_power_csv.py) to export normalized JSON summaries from raw logger CSV files.
