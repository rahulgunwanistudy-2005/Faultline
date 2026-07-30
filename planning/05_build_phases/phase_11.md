# Phase 11: Judge Mode and Deployment

## Objective

Implement timeline-driven Judge Mode, preload fixtures, deploy web/API, add health checks, structured logs and a one-command smoke test.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `apps/web/app/judge`
- `public/demo`
- `scripts/smoke_test.sh`
- `docs/deployment.md`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] 30-second mode works offline after load.
- [ ] Incognito deployment succeeds.
- [ ] Demo does not depend on a live model call.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
