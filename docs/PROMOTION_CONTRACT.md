# Promotion Contract

This page explains the public acceptance rule for promoted repairs.

## Core Idea

A local repair is not accepted only because it wins on one slice. It must survive a coupled promotion contract.

Publicly visible parts of that contract include:

- replay against the frozen authoritative parent
- external non-regression
- leakage and deep-pretrain audit status
- runtime and shadow cleanliness
- overfit and hidden-family boundary disclosure

## Current Public Surface Status

Current public reference:

- official `IFEval = 0.780037`
- official `LogiQA = 0.392523`
- `external_dev = 0.308908`
- `external_blind = 0.425072`
- `runtime_pass = true`
- `shadow_pass = true`

Sources:

- [../results/research_line/current_host_surface_reference_status.json](../results/research_line/current_host_surface_reference_status.json)
- [../results/research_line/current_host_surface_guard_bundle_status.json](../results/research_line/current_host_surface_guard_bundle_status.json)

## Publicly Relevant Gate Layers

### 1. Frozen Parent Comparison

All public gains are read against the same authoritative parent boundary.

### 2. Strict Multi-Route Acceptance Gate

The formal mainline behind the current surface is not a single-benchmark contract. It requires multiple benchmark routes, including:

- `LogiQA`
- `GSM8K`
- a narrow instruction-following benchmark

This matters because the accepted host surface is not supposed to be interpreted as a one-benchmark trick.

### 3. External Dev And External Blind

The formal mainline treats external dev and external blind as required multi-route checks, not optional receipts.

### 4. Leakage, Deep Audit, Shadow, Runtime

The public bundle exposes the resulting status, including:

- leakage pass
- deep-pretrain audit pass
- shadow pass
- structured execution pass
- research runtime ready

### 5. Overfit And Hidden-Family Boundary

Even after a surface is published, the repo keeps negative evidence visible:

- clean `holdout2 = 0.400000`
- `blind_remainder = 0.448133`
- hidden-family `0 / 85`

## Why The Public Guard Bundle Is Conservative

The public guard bundle is intentionally conservative:

- `bundle_pass = true`
- `promotion_recommended = false`

This is not a contradiction. It means the public wrappers reproduce the accepted research surface, but the repo is still positioned as a research line rather than a commercial freeze replacement.

See:

- [../results/research_line/current_host_surface_guard_bundle_status.json](../results/research_line/current_host_surface_guard_bundle_status.json)

## What Is Not Published

This repo does not expose:

- full gate history for rejected candidates
- all threshold tuning history
- full protected-win bookkeeping
- the private candidate-generation workflow

The goal is to publish the acceptance contract and its evidence without giving away the internal search and training pipeline.
