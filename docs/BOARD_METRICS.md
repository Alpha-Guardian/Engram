# Board Metrics

This page consolidates the current public `ESP32-C3` board metrics into one place.

All values below come from real board readback JSON in:

- [../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json](../results/board_proof/raw/esp32c3_logiqa_batch_current_surface_runtime_topk_official642_k24_hostfullexact_000_064.json)
- [../results/board_proof/esp32c3_logiqa642_board_proof_summary.json](../results/board_proof/esp32c3_logiqa642_board_proof_summary.json)
- [../results/board_proof/board_runtime_audit_acceptance.json](../results/board_proof/board_runtime_audit_acceptance.json)

Nothing here is hand-entered from memory. The numbers are copied from the published board reports.

## Hardware and binary footprint

| Metric | Value |
|---|---|
| Target board | `ESP32-C3` |
| Artifact name | `chip_suite_surface_round2_q4_tgz_expack_rgz.json` |
| Artifact SHA256 | `626a1bfcc0a86585db82130744094ee4512eaaead8b4d9f1dba07175c010719d` |
| Artifact size | `1,380,771 bytes` |
| Firmware size (`firmware.bin`) | `1,784,352 bytes` |
| Sketch size on board | `1,784,352 bytes` |
| Free heap | `310,024 bytes` |
| Min free heap | `306,296 bytes` |
| Artifact runtime decoded on board | `false` |

## Artifact integrity metrics

| Metric | Value |
|---|---|
| `artifact_crc32` | `3080397803` |
| `artifact_crc_ms` | `891` |
| `artifact_stride_scan_ms` | `11` |
| `artifact_stride_checksum` | `455673` |
| `has_logiqa_token_weights_packed` | `1` |
| `has_logiqa_exemplars_packed` | `1` |
| `has_gpu_logiqa_hash_dim` | `1` |

## IFEval probe metrics

The default firmware includes an embedded `IFEval` probe block. The current published board report shows:

| Metric | Value |
|---|---|
| `ifeval_probe_samples` | `64` |
| `ifeval_probe_offset` | `0` |
| `ifeval_probe_nonempty` | `64` |
| `ifeval_probe_output_tokens` | `6438` |
| `ifeval_probe_ms` | `32` |
| `ifeval_probe_tokens_per_sec` | `201187.5` |
| `ifeval_probe_checksum` | `149594523` |
| `ifeval_probe_encoding_version` | `1` |

## LogiQA GPU-only probe metrics

The same default board report also exposes the GPU-only probe path for the fixed batch:

| Metric | Value |
|---|---|
| `gpu_probe_samples` | `64` |
| `gpu_probe_correct` | `17` |
| `gpu_probe_expected_match` | `64` |
| `gpu_probe_ms` | `898` |
| `gpu_probe_samples_per_sec` | `71.269` |
| `gpu_probe_pred_prefix` | `BBCBCDDBDDBBDBCC` |
| `gpu_probe_first_scores` | `-0.001979,-0.001603,-0.001724,-0.001603` |

## LogiQA compiled board-proof metrics

The published board-proof line uses:

- aggregate board-proof summary mode: `evaluation_mode = logiqa_batch_compiled_probe_aggregated`
- default single-batch board readback mode: `evaluation_mode = logiqa_batch_compiled_probe`
- `compiled_probe_mode = host_full_exact`

Single-batch metrics from the default board report:

| Metric | Value |
|---|---|
| `linear_gpu_probe_samples` | `64` |
| `linear_gpu_probe_offset` | `0` |
| `linear_gpu_probe_correct` | `26` |
| `linear_gpu_probe_expected_match` | `64` |
| `linear_gpu_probe_host_full_match` | `64` |
| `linear_gpu_probe_ms` | `0` |
| `linear_gpu_probe_samples_per_sec` | `0.0` |
| `linear_gpu_probe_pred_prefix` | `CCAABBDCADDCABBC` |
| `linear_gpu_probe_first_scores` | `8.023393,8.081159,13.144008,4.683906` |

Aggregate `LogiQA 642` board-proof metrics:

| Metric | Value |
|---|---|
| `aggregate_batch_count` | `11` |
| `total_samples` | `642` |
| `total_correct` | `249` |
| `accuracy` | `0.3878504672897196` |
| `host_full_match` | `642` |

## Board Comparator Bundle

The repo now publishes two board-side comparators on the same fixed `642`-sample path:

| Artifact | Accuracy | Correct | Host full match |
|---|---:|---:|---:|
| frozen parent | `0.302181` | `194 / 642` | `642 / 642` |
| parent trained linear baseline | `0.299065` | `192 / 642` | `642 / 642` |

Compared with the current scientific surface:

| Artifact | Accuracy | Delta vs current |
|---|---:|---:|
| current scientific surface | `0.387850` | `0.000000` |
| frozen parent | `0.302181` | `-0.085670` |
| parent trained linear baseline | `0.299065` | `-0.088785` |

Source:

- [../results/board_proof/board_baseline_comparison.json](../results/board_proof/board_baseline_comparison.json)

## Why do IFEval and LogiQA look so fast?

Because the published board line is **not** an unrestricted open-input runtime benchmark.

### IFEval

The current default firmware exposes an embedded `IFEval` probe:

- fixed probe sample count: `64`
- fixed offset: `0`
- fixed compiled encoding

So the published `IFEval` board numbers are:

- real
- board-measured
- reproducible

but they are **probe throughput numbers**, not a claim about open-ended autoregressive generation on arbitrary prompts.

### LogiQA

The current board proof uses:

- `compiled_probe_mode = host_full_exact`

That means the board is running a fixed compiled path that reproduces the final host-full scores for the published batches. In that mode, the board-side `ms` is not a meaningful general runtime benchmark, because the board is effectively executing a fixed compiled exact-score path and then argmaxing.

So for `LogiQA`, the important published evidence is:

- `249 / 642 = 0.3878504672897196`
- `host_full_match = 642`

not the aggregate `total_ms`.

## Honest interpretation

These numbers are strong because they are:

- real
- board-read back
- aligned to published raw JSON

They should **not** be misread as:

- unrestricted open-input throughput numbers
- a generic MCU token-generation benchmark

They are board-proof metrics for a constrained, auditable Tiny Expert line.
