# Audit Notes

The current public acceptance record is:

- [results/board_runtime_audit_acceptance.json](../results/board_runtime_audit_acceptance.json)

## Accepted checks

### LogiQA

- all `11` raw batch reports match the aggregate summary
- aggregate `correct / samples / ms / host_match` values match
- `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- `artifact_runtime_decoded_on_board = false`

### IFEval

- the raw board report matches the aggregate summary
- the host reference matches on:
  - `samples`
  - `nonempty`
  - `output_tokens`
  - `checksum`
- `evaluation_mode = ifeval_compiled_piece_stream_full`
- `artifact_runtime_decoded_on_board = false`

## Public wording after audit

The most accurate public description is:

- `LogiQA`: board-side batch-compiled probe aggregate
- `IFEval`: board-side compiled piece stream full run

## Raw files

- [results/raw/esp32c3_ifeval541_compiled_audited_board_report.json](../results/raw/esp32c3_ifeval541_compiled_audited_board_report.json)
- [results/raw](../results/raw)

The per-batch raw `LogiQA` reports are also included in `results/raw`.
