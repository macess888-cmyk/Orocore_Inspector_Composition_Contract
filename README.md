# Orocore Inspector Composition Contract

Status: bounded integration experiment.

This is not DELTA-006.

## Question

Can multiple bounded inspector outputs be composed without:

- merging their semantics;
- inheriting authority;
- masking a required HOLD;
- converting local positive results into a global PASS;
- losing provenance between modules?

## Participating frozen inspectors

- DELTA-001 Authority Mutation
- DELTA-002 Transition Evidence Contract
- DELTA-003 Restriction Continuity
- DELTA-004 Model / Monitor Transfer
- DELTA-005 Witness Independence

## Core composition rules

local HOLD != global failure

required unresolved dependency -> downstream HOLD

positive local result != global PASS

all bounded positives != execution authority

one inspector may reference but never rewrite another inspector's state

## Candidate composition fields

- source_inspector
- subject_id
- observation_time
- state
- diagnostics
- scope
- provenance_reference
- required_dependencies
- unresolved_dependencies
- freshness
- non_claims

## Boundaries

Composition is observer-only.

Composition does not create execution authority.

Composition does not create claim truth.

Composition does not rewrite local inspector outputs.

Composition does not collapse HOLD into FAIL or PASS.

UNKNOWN -> HOLD remains local unless the unresolved result is a required dependency.