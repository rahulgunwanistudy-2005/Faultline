# Privacy, Safety, and Responsible Use

## Product boundaries

Faultline supports teacher judgment; it does not make grades, placement decisions, disability determinations, or disciplinary decisions.

## Data minimization

- Student names are optional and should default to anonymous labels.
- Demo data uses pseudonyms.
- Raw worksheet images are deleted after a configurable retention window.
- Logs contain job IDs, timings, confidence, and error codes—not page images or recognized student text.
- Provide a “Delete this analysis” control.

## Human review

- Low-confidence OCR must be corrected before diagnosis.
- Every diagnosis has item-level evidence.
- A teacher can override or mark a result as “not useful.”
- The “wording may be the barrier” output requires matched computation and word-problem items and must be phrased as a signal, not a student identity claim.

## LLM containment

- LLM outputs are schema-validated.
- The novel-rule path uses a restricted JSON expression DSL.
- No `eval`, generated Python, shell execution, or network tool access.
- A proposal is shown only if it reproduces enough observed items and passes complexity limits.
- Generated teacher wording is derived from a verified rule identifier, not the reverse.

## Honest limitations to display

- Handwriting recognition can fail, especially on crossed-out work.
- The current build covers one fraction skill.
- Controlled assigned-rule evaluation is not a classroom clinical validation.
- A matched word-problem gap can indicate wording/context difficulty but cannot identify its cause.
- The system cannot estimate how much a student will improve.
