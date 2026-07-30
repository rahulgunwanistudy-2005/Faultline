# Phase 2: Executable Malrule Engine

## Objective

Implement normalized fraction problems, answer representation, six initial procedures, traces, eligibility and exhaustive unit tests.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `packages/faultline_core/faultline_core/domain.py`
- `malrules.py`
- `tests/test_malrules.py`
- `data/malrules.json`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] No dynamic eval.
- [ ] Every rule predicts across a parameterized item set.
- [ ] Descriptions and actions are metadata, not model output.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
