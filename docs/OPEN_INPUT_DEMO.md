# Open-Input Demo

This repository now publishes two open-input demos:

- host-side structured open-input loop
- board-side `ESP32-C3` narrow open-input micro-loop

Both are intentionally separate from the fixed-batch `ESP32-C3` board proof.

## Scope

Track A: host-side structured loop:

- host-side only
- free-text prompt in
- structured JSON out
- exact schema and exact-match evaluation
- explicit unsafe-guard cases

Track B: board-side micro-loop:

- real `ESP32-C3` execution
- free-text command in (`RUN DEEPSEEK <text>`)
- deterministic normalized text out
- exact-match evaluation on published open-input taskset
- stability probe included

Host-side published task families:

- `tool_call`
- `state_machine`
- `config_emit`
- `route_decision`
- `unsafe_guard`

## Current Result

Host-side structured demo under the current scientific surface:

- `json_parse_rate = 1.0`
- `schema_pass_rate = 1.0`
- `exact_match_rate = 1.0`
- `unsafe_guard_rate = 1.0`

Host-side runtime proxy:

- `ifeval_avg_ttft_ms = 3.332616`
- `logiqa_avg_ttft_ms = 80.400484`
- `peak_memory_mb = 0.693346`
- `stability_ok = true`

Board-side MCU micro-loop:

- [../results/open_input_demo/host_open_input_demo.json](../results/open_input_demo/host_open_input_demo.json)
- [../results/open_input_demo/mcu_open_input_demo.json](../results/open_input_demo/mcu_open_input_demo.json)
- [../results/open_input_demo/mcu_open_input_taskset_v1.jsonl](../results/open_input_demo/mcu_open_input_taskset_v1.jsonl)
- [../results/open_input_demo/mcu_open_input_board_report.json](../results/open_input_demo/mcu_open_input_board_report.json)

Current board-side metrics:

- `samples = 36`
- `exact_match_rate = 1.0`
- `nonempty_rate = 1.0`
- `stability_rate = 1.0`
- `avg_latency_ms = 43.814817`
- `evaluation_mode = deepseek_unit_open_input_interactive_v1`
- `artifact_sha256 = c98987ce318b654175a939ac28d81f9a1cd2952053722ef020d03e4e4bd12df8`

## Why This Matters

This closes two distinct public gaps:

- the board proof remains a bounded crystallization proof
- host demo shows a structured open-input path
- board demo shows a real open-input loop on MCU in a narrow constrained scope

So the repo now separates three claims cleanly:

- `fixed-batch board crystallization`
- `host-side open-input structured execution`
- `MCU-side narrow open-input micro-loop`

## What It Does Not Mean

It does not mean:

- unrestricted broad MCU open-input deployment
- broad reasoning generalization
- replacement of the board proof boundary

The current MCU open-input demo is intentionally narrow and strongly constrained.

## Maintainer Path

Maintainers inside the full workspace can refresh the public demo with:

```bash
python3 scripts/run_public_open_input_demo.py
py scripts/flash_open_input_firmware.py COM3
py scripts/run_mcu_open_input_demo.py --port COM3
python3 scripts/build_public_experiment_tables.py
python3 scripts/verify_public_bundle.py
```
