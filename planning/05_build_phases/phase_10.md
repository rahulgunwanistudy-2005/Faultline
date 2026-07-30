# Phase 10: Evaluation Lab

## Objective

Create controlled assigned-rule pilot scripts, metric separation, confusion matrix generation, calibration/coverage report and UI panel.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `scripts/evaluate.py`
- `data/evaluation`
- `docs/evaluation_report.md`
- `components/evidence-lab`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] OCR, engine and end-to-end metrics are separate.
- [ ] Dataset type is visible.
- [ ] Results are reproducible from repo commands.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
