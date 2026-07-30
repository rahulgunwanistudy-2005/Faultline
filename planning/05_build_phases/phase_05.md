# Phase 5: Worksheet and Vision

## Objective

Create a fixed demo worksheet template, crop map, image normalization, Featherless vision adapter, structured output validation, and manual correction UI.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `apps/api/faultline_api/adapters/vision.py`
- `services/segmentation.py`
- `apps/web/components/reading-review`
- `data/templates`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] Vision prompt transcribes only.
- [ ] Timeout/error becomes review state.
- [ ] Seed fixture works without API key.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
