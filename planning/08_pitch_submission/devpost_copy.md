# Devpost Submission Copy

## Project name

Faultline

## One-line tagline

Find the wrong procedure beneath the score.

## Inspiration

A teacher wrote that her students seemed to understand fractions during lessons, yet more than half failed the test even after reteaching and review. The signal available to her—participation, correct scaffolded practice, and final scores—could show that something was wrong, but not what procedure each student was actually using.

## What it does

Faultline turns a stack of fraction worksheets into a class-level map of student procedures. It does not grade work or invent a mastery score. It identifies which executable procedure best reproduces each student’s answers, shows competing hypotheses and evidence, refuses low-confidence diagnoses, predicts responses on held-out problems, and selects the next diagnostic questions by information gain.

The teacher receives four possible outcomes:

- re-explain the concept before more repetition;
- use short procedural practice;
- inspect a matched wording/context gap;
- collect more evidence before deciding.

## How we built it

A Next.js interface handles upload, OCR review, the class map, evidence views, and a deterministic Judge Mode. A FastAPI backend coordinates page processing and result APIs. Featherless vision models transcribe problem crops into structured answer candidates and step features. The central Python package executes a library of fraction malrules, marginalizes OCR uncertainty, computes a posterior over procedures, applies confidence gates, and selects diagnostic items using exact expected information gain.

When the known library fails, a Featherless text model may propose a candidate rule in a restricted JSON expression language. The candidate is executed in a safe interpreter and appears only if it reproduces the work and passes complexity checks. The LLM proposes; the verifier decides.

## Challenges

The hardest problem was preserving trust across two uncertainties: handwriting recognition and ambiguity between procedures. We separated OCR from diagnosis, added a correction path, and built a full posterior rather than a single label. We also created a server-enforced held-out flow so the strongest demo proof—a predicted unseen response—cannot leak into the inference.

## Accomplishments

- Executable, tested procedure library rather than prompt-only classification
- Exact information-gain question selection
- Confidence gating and evidence-level explanations
- Controlled assigned-procedure handwriting evaluation with separated metrics
- Safe verifier-gated new-pattern proposal
- Thirty-second deterministic Judge Mode

## What we learned

Educational AI becomes more useful when it is willing to say less. The most credible feature was not another prediction; it was an explicit “insufficient evidence” state and the ability to ask the smallest set of questions needed to decide.

## What’s next

Expand the malrule library to subtraction and fraction magnitude, validate with consented classroom data, support teacher-authored worksheet templates, and study whether procedure-level grouping improves intervention choice. Those are research and product milestones—not claims made by this prototype.

## Built with

Next.js, TypeScript, FastAPI, Python, PostgreSQL, Featherless.ai vision and text inference, structured JSON schemas, and a dependency-light executable malrule engine.
