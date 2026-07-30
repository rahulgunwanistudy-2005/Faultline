# Phase 0: Evidence Lock and Repository

## Objective

Freeze the winning claim, record sources, create the repository, build log, issue board, and non-goals. Do not write application features yet.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `README.md`
- `BUILD_LOG.md`
- `docs/claims.md`
- `docs/sources.md`
- `docs/non_goals.md`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] Every numeric claim has a measurement plan or is removed.
- [ ] The domain is adding unlike-denominator fractions only.
- [ ] The repository history begins inside the allowed competition window.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
