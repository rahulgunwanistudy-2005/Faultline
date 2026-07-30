# Faultline

**Find the wrong procedure beneath the score.**

Faultline tests executable fraction procedures against visible work, shows the evidence and uncertainty, locks a held-out prediction before reveal, and chooses the next diagnostic questions by exact information gain.

## Prototype boundary

The v0.2.0 upload path verifies and segments one known PNG/JPEG template. Live handwriting recognition is not enabled; the displayed diagnoses use a prominently disclosed synthetic regression fixture.

## Why this is not AI grading

A grader maps work to a score. Faultline infers the executable procedure that could generate a pattern and refuses to decide when the evidence is insufficient.

## Demo

- Live app:
- Two-minute video:
- 30-second Judge Mode: `/judge`

## Reproduce the current evidence

```bash
./scripts/verify_submission.sh
python scripts/evaluate.py
```

Include a capture of the signed prediction-then-reveal flow. Label the matrix and 12/12 result as synthetic fixture regression evidence.

## Evaluation disclosure

Report these separately:

1. engine behavior on exact synthetic fixture readings;
2. OCR/transcription accuracy on a controlled handwritten pilot;
3. end-to-end diagnosis accuracy on that pilot;
4. any future classroom or intervention outcome.

Only item 1 exists in this release.

## Responsible use

No grades, placements, disability determinations, or autonomous teaching decisions. Low-confidence work is withheld for review. Future model-proposed rules remain verifier-gated.

## Team

Solo builder with AI-assisted engineering. Describe design, implementation, evaluation, and presentation responsibilities accurately.
