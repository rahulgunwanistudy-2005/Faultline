# Product Requirements Document

## Product statement

Faultline helps a middle-school math teacher turn a stack of fraction worksheets into a class-level map of the procedures students are actually using, including uncertainty and the next best questions to ask.

## Primary persona

A teacher with multiple sections and roughly 150 students who has enough time to identify wrong answers but not enough time to reverse-engineer the reasoning behind each one.

## Job to be done

> “After a test or exit ticket, help me decide whether to re-explain the concept, assign procedural practice, or check whether wording is blocking a student—and show me the evidence.”

## Core user story

1. The teacher opens a demo class or uploads a stack.
2. Faultline detects pages and problem regions.
3. The teacher quickly reviews low-confidence readings.
4. Faultline groups students by the procedure best reproducing their work.
5. The teacher opens one student and sees item-level evidence.
6. For an ambiguous case, Faultline proposes three diagnostic questions.
7. The teacher exports a one-page “tomorrow plan.”

## Functional requirements

### Ingest

- Accept JPG, PNG, or PDF.
- Use a known worksheet template in the winning demo.
- Return per-problem crops, answer candidates, and OCR confidence.
- Allow one-click correction before diagnosis.

### Diagnosis

- Execute all eligible hypotheses on every item.
- Include correct procedure, known malrules, no-consistent-procedure, and OCR-uncertain mass.
- Show the full posterior, not only the top label.
- Gate output if evidence is weak.

### Evidence

- For each hypothesis, display predicted vs observed answer by item.
- Highlight intermediate-step features that support or contradict the rule.
- Generate a held-out prediction without seeing the held-out answer.

### Diagnostic item selection

- Rank a parameterized item bank by expected information gain.
- Return three diverse, teacher-printable questions.
- Explain which hypotheses each question separates.

### Action layer

- Consistent malrule → “Re-explain the idea before more repetition.”
- No consistent procedure → “Use short guided practice; no stable wrong habit is visible.”
- Matched computation/wording split → “The procedure looks intact; check wording or context.”
- Ambiguous/low confidence → “Collect more evidence first.”

### Judge Mode

- Deterministic 30-second automatic tour.
- No network dependency after initial load.
- Captions, pause, restart, skip, and progress indicator.
- Route or query parameter that launches directly into the tour.

## Non-functional requirements

- First meaningful screen under 2 seconds on demo deployment.
- Seeded demo completes without external API dependency.
- Live OCR retries once and then offers manual entry.
- No student names required; demo uses pseudonyms.
- No uploaded image content in logs.
- Keyboard-accessible controls and readable captions.
- All outputs use plain language.

## Success measures

Do not use unsupported educational effect sizes. Measure:

- time from upload to teacher-ready class map;
- OCR exact-expression accuracy;
- engine hypothesis identification accuracy on exact transcriptions;
- end-to-end diagnosis accuracy in a controlled assigned-rule pilot;
- confidence calibration/coverage;
- demo completion and test pass rate.
