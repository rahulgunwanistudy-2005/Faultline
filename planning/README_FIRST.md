# Faultline — First-Place Build Blueprint

> **Winning thesis:** Faultline must not look like another AI tutor. It must look like a small scientific instrument for teachers: upload student work, infer the repeated wrong procedure, prove the inference on a held-out problem, and recommend the next diagnostic action without inventing learning gains.

This package converts the supplied Faultline concept into a complete build program for a solo builder using GPT-5.6 in chat. It includes competition intelligence, a rubric-backed product strategy, architecture diagrams, the inference design, a safe LLM synthesis protocol, UI/UX specifications, staged implementation prompts, evaluation fixtures, pitch copy, submission copy, and an executable reference core with tests.

## The five non-negotiables

1. **One narrow domain, executed deeply:** adding fractions with unlike denominators. Do not dilute the demo with every subject or every fraction operation.
2. **One undeniable magic moment:** diagnose from several worked answers, predict the student's answer on an unseen problem, then reveal the held-out work.
3. **Evidence before claims:** separate OCR accuracy, engine identification accuracy, and end-to-end controlled-pilot accuracy. Never claim classroom learning impact without a real study.
4. **Beautiful restraint:** one upload flow, one class map, one evidence drawer, one “tomorrow” card. No dashboard soup and no ed-tech jargon.
5. **The video is part of the product:** a deterministic 30-second Judge Mode is built into the app and reused inside the required two-minute submission video.

## Competition reality

The official Devpost page lists four equally weighted criteria: Educational Impact, Creative Use of AI/ML, Technical Execution, and Pitch & Demo. A working prototype, source repository, and video of no more than two minutes are required. The displayed Devpost deadline is **July 30, 2026 at 11:45 PM EDT**, which is **July 31, 2026 at 9:15 AM IST**. The rules separately mention 11:59 PM, so use the earlier Devpost timestamp as the safe cutoff.

The rules also contain a date inconsistency: the event overview says July 17–30, while the originality clause names July 8–30. Keep a build log and commit history proving that the core application logic was created during the allowed period.

## Package map

- `01_research/` — official rules, judge lenses, winner proxies, source index
- `02_strategy/` — rubric map, moat, scope, scoring plan, emergency ordering
- `03_product/` — PRD, user journey, visual system, Judge Mode, privacy
- `04_system_design/` — architecture, data model, API, inference math, OCR, DSL
- `05_build_phases/` — phase-by-phase implementation and acceptance gates
- `06_agent_prompts/` — ready-to-paste GPT-5.6 chat prompts
- `07_evaluation/` — controlled pilot, datasets, score templates, test cases
- `08_pitch_submission/` — exact video script, shot list, Devpost copy, judge Q&A
- `09_reference_implementation/` — executable Python core and tests
- `10_checklists/` — winning gate, technical QA, submission and red-team lists

## Recommended execution order

Read these first:

1. `01_research/hackathon_intelligence.md`
2. `02_strategy/rubric_to_proof_matrix.md`
3. `02_strategy/winning_moat.md`
4. `03_product/product_requirements.md`
5. `04_system_design/inference_engine.md`
6. `05_build_phases/PHASE_INDEX.md`
7. `06_agent_prompts/MASTER_CONTEXT.md`
8. `08_pitch_submission/demo_script_120s.md`

## What “done” means

Faultline is submission-ready only when:

- the app completes a deterministic demo from upload to class map;
- the held-out prediction reveal works without manual intervention;
- every diagnosis shows supporting item evidence;
- ambiguous cases visibly refuse to guess;
- the core engine tests pass;
- a controlled-pilot confusion matrix is shown with honest labels;
- the public deployment and repository both work in incognito mode;
- the video is 1:55–1:59 long, captioned, and understandable without audio.
