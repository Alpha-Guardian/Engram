# Why Tiny Experts

Cloud LLMs are powerful, but many edge deployments do not need or cannot afford a general remote model.

The hard constraints are physical:

- memory is often measured in `KB` to low `MB`
- power is often measured in `mW`
- connectivity is unreliable or unavailable
- many deployments require deterministic behavior and postmortem auditability

For those environments, the question changes from:

- `How do we run a full assistant everywhere?`

to:

- `How do we distill one useful task capability into a tiny, stable, offline expert?`

That is the motivation for Engram.

## What makes this line different

This project is not a simple “shrink a larger transformer” exercise.

The working pattern is:

1. identify residual error families on the target task
2. materialize target-local corrections
3. compress the resulting capability into flash-resident tables and compiled board paths
4. publish an audit stack that makes the boundary explicit

The runtime is therefore closer to:

- a crystallized task expert
- a structured execution substrate
- a hardware-friendly capability endpoint

than to a miniature general-purpose chatbot.

## Why that matters industrially

In many industrial environments, the most valuable properties are:

- offline survival
- deterministic deployment
- bounded memory and power
- auditable execution
- task-specific reliability

That is why a Tiny Expert can be more practical than a far larger, far more general model.

## What this repo demonstrates

This repository demonstrates one concrete instance of that idea:

- a current host-side scientific surface with official and external benchmark evidence
- a real `ESP32-C3` board proof line aligned to fixed-batch host-full decisions
- a public trust layer that includes replay, integrity, overfitting, and hidden-family forensic evidence

## What this repo does not claim

It does not claim:

- a universal edge AI stack
- unrestricted native LLM inference on MCU
- proof of general reasoning

The point is narrower and more useful:

- show that a benchmark-relevant reasoning capability can be distilled into a tiny, auditable, offline expert line under extreme edge constraints
