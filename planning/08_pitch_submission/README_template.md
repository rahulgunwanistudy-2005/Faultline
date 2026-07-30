# Faultline

**Find the wrong procedure beneath the score.**

Faultline reads a fixed-template stack of fraction work, tests executable candidate procedures against each student’s answers, shows the evidence and uncertainty, predicts a held-out response, and chooses the next diagnostic questions by exact information gain.

## Why this is not AI grading

A grader maps work to a score. Faultline infers the latent procedure that could generate the pattern and refuses to decide when the evidence is insufficient.

## Demo

- Live app:
- Two-minute video:
- 30-second Judge Mode:

## Core proof

```bash
pytest packages/faultline_core/tests -q
python scripts/evaluate.py --dataset data/evaluation/controlled_pilot.csv
```

Include a GIF of the prediction-then-reveal flow and a labeled confusion matrix.

## Architecture

Insert `docs/architecture/architecture.svg` and explain the deterministic boundary.

## Evaluation disclosure

Report OCR, exact-transcription engine, and end-to-end controlled assigned-procedure results separately. State limitations.

## Local setup

Provide copy-paste commands, `.env.example`, and a fixture mode requiring no API key.

## Responsible use

No grades, placements, disability determinations, or autonomous teaching decisions. Low-confidence work is reviewed. Model-generated rules are verifier-gated.

## Team

Solo builder with AI-assisted engineering. Describe your own design, implementation, evaluation and presentation responsibilities accurately.
