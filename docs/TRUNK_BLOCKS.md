# Trunk Blocks

This page documents the public structure of the current route-gated trunk recurrent blocks.

## Current Inventory

The current promoted scientific surface contains:

- `75` trunk recurrent blocks
- `72` blocks in `option_latent_v2`
- `3` blocks in `pair_score`
- `11,325` LogiQA exemplars
- `8192` GPU hash dim

Source:

- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

## Public Block Fields

The public inventory exposes representative sanitized fields such as:

- `block_name`
- `mode`
- `route_token_count`
- `route_group_count`
- `route_min_hits`
- `route_group_min_matches`
- `support_count`
- `train_count`
- `parent_top`
- `parent_second`
- `parent_margin_max`
- `mapped_gold`
- `mapped_competitor`
- `depth_steps`
- `step_scale`
- `score_scale`
- `evidence_scale`
- `pair_bias_scale`
- `stop_margin`
- `pair_hash_dim`
- `latent_dim`

These fields are enough to explain what the accepted blocks are trying to do without publishing the private recovery path that produced them.

## Public Semantics

`option_latent_v2` blocks:

- activate on a routed family surface
- inspect the frozen parent competition topology
- apply a recurrent local repair over a gold-versus-competitor latent pair

`pair_score` blocks:

- are simpler pair-targeted repairs
- preserve the same public idea of family-local adjustment

## Public Shape Of The Current Surface

The current inventory shows:

- all public blocks have `depth_steps = 3`
- support counts range from `1` to `8`
- most blocks have route token counts in the `5-8` range

The top parent-topology pairs include:

- `B -> C`
- `C -> B`
- `D -> B`

The top mapped repair pairs include:

- `D -> C`
- `C -> B`
- `C -> D`
- `B -> D`
- `A -> B`

Source:

- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

## Sensitive Fields Omitted

The public inventory intentionally omits:

- full `route_tokens`
- full `route_token_groups`
- `route_exclude_tokens`
- `source_ids`
- `stem_source`
- `stem_tokens`
- `gold_proto`
- `competitor_proto`

Those fields are much closer to the private family-mining and support-selection assets. The public repo keeps the structure and evidence, while withholding the parts that would reveal too much of the training moat.
