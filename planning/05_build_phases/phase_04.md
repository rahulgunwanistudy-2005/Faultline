# Phase 4: Information Gain

## Objective

Build a candidate item bank, exact entropy calculation, answer grouping, diversity constraints, and teacher-readable separation explanations.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `information_gain.py`
- `data/item_bank.json`
- `tests/test_information_gain.py`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] Zero-value items rank below separating items.
- [ ] Top three are diverse.
- [ ] Output is deterministic for a seed.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
