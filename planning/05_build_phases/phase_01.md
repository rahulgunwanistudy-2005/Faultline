# Phase 1: Scaffold and CI

## Objective

Create the Next.js web app, FastAPI API, dependency-light Python core package, shared schemas, formatting, linting, tests, and CI.

## Required inputs

- `06_agent_prompts/MASTER_CONTEXT.md`
- `02_strategy/rubric_to_proof_matrix.md`
- Relevant files in `04_system_design/`
- Current repository tree and latest test output

## Deliverables

- `apps/web`
- `apps/api`
- `packages/faultline_core`
- `.github/workflows/ci.yml`
- `docker-compose.yml`

## Working method

1. Inspect the current repository before changing files.
2. State the implementation contract and failure cases.
3. Implement the smallest complete vertical slice for this phase.
4. Add or update tests before declaring success.
5. Run lint, type checks, unit tests, and the phase-specific smoke test.
6. Update `BUILD_LOG.md` with decisions and evidence.
7. Stop at the phase boundary; do not add roadmap features.

## Acceptance gates

- [ ] Web and API boot locally.
- [ ] Core tests run independently.
- [ ] One command runs lint and tests.

## Completion report format

- Files changed
- Commands run and exact results
- Acceptance gates passed/failed
- Known limitations
- Single best next phase
