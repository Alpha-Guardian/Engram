# Family And Routing

This page documents the public contract for residual families and route activation. It explains the accepted mechanism without exposing the private family-discovery pipeline.

## Public Definition Of A Residual Family

A residual family is a bounded repair slice defined by the combination of:

- the frozen parent competition shape
- the target-versus-competitor repair pair
- the route surface that decides when the repair may activate

In public terms, a family is not "all similar questions" in the abstract. It is a constrained operational slice where:

- the parent behaves in a characteristic way
- a specific local correction is desired
- routing conditions keep the correction local

## Route Activation Contract

A trunk block becomes eligible only when two kinds of conditions line up.

### 1. Route Surface

Each block carries a route signature built from question and option surface features. Publicly visible route controls include:

- `route_tokens`
- `route_min_hits`
- `route_token_groups`
- `route_group_min_matches`
- `route_exclude_tokens`

At runtime, the question and option text are converted into a token and bigram surface. The block is eligible only if its route thresholds are met and exclude rules do not fire.

### 2. Parent Topology

Route eligibility is still not enough. The block also expects a compatible frozen-parent competition signature, exposed through fields such as:

- `parent_top`
- `parent_second`
- `parent_margin_max`
- `mapped_gold`
- `mapped_competitor`

So the block fires only where the route surface and the parent topology agree.

## Current Public Routing Statistics

From the current surface inventory:

- total trunk blocks: `75`
- route token count median: `6`
- route token count range: `4` to `16`
- `route_min_hits = 2` for `15` blocks
- `route_min_hits = 3` for `60` blocks
- all public blocks currently show `route_group_min_matches = 0`

Source:

- [../results/experiments/block_inventory.json](../results/experiments/block_inventory.json)

## Representative Locality Evidence

The tightest representative public probes are:

- `official_bc_zeroinit_routes`, narrow and protected slice
- `official_dbb_bc_support_b1_additive`, narrow and protected slice

In those four public probes:

- designated targets fixed: `3 / 3`
- off-target fires: `0`
- locality collateral flips: `0`

The wider published probe set also includes:

- `official_ad_support_b1_additive`

Its protected slice shows broader activation:

- off-target fires: `6`
- locality collateral flips: `0`

Source:

- [../results/experiments/locality_probes.json](../results/experiments/locality_probes.json)

## What Is Withheld

This repo does not publish:

- the full family discovery frontier
- support-source tracing
- rejected candidate families
- full route token inventories for every accepted block

That omission is deliberate. Those assets are much closer to the private training moat than the public method contract is.
