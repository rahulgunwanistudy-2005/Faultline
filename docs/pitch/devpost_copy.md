# Devpost Submission Copy — Honest v0.2.0 Draft

## Project name

Faultline

## One-line tagline

Find the wrong procedure beneath the score.

## Inspiration

A teacher wrote that her students seemed to understand fractions during lessons, yet more than half failed the test even after reteaching and review. The signal available to her—participation, scaffolded practice, and final scores—could show that something was wrong, but not what repeatable procedure was producing the answers.

## What it does

Faultline turns a controlled fraction-work fixture into a class-level map of executable student procedures. It does not grade work or invent a mastery score. It identifies which procedure best reproduces each visible answer pattern, shows competing hypotheses and item-level evidence, refuses low-confidence diagnoses, locks a prediction before revealing held-out work, and selects the next diagnostic questions by exact expected information gain.

The teacher receives four possible next moves: re-explain the concept, use short guided practice, inspect a matched wording/context gap, or collect more evidence before deciding.

## How we built it

A zero-build HTML/CSS/JavaScript interface and 30-second Judge Mode are served by FastAPI from one container. A dependency-light Python package executes six fraction procedures, incorporates reading confidence and step evidence, computes a posterior over procedures, applies explicit confidence gates, and forward-simulates candidate questions to calculate information gain.

The held-out centerpiece is server-gated: public class payloads and browser assets contain neither the actual held-out answer nor a precomputed prediction. The prediction endpoint creates an expiring HMAC-signed token; a separate POST reveal verifies that token before returning the server-held answer.

The repository also contains a restricted JSON expression verifier for future model-proposed rules. It has no imports, strings, item identifiers, conditionals, file access, network access, or Python evaluation. A model could propose; only the deterministic verifier could accept.

## Current prototype boundary

The upload route securely validates, normalizes, and crops a known PNG/JPEG worksheet template, but **live handwriting transcription is not enabled in this release**. After demonstrating the upload boundary, the interface clearly labels and uses a deterministic synthetic regression fixture. We report its 12/12 top-rank result only as a software regression check—not as classroom accuracy.

## Challenges

The hardest problem was preserving trust across uncertain readings and ambiguous procedures. We separated transcription from diagnosis, retained a correction path, built a full posterior rather than a single label, and made “insufficient evidence” a first-class output. A security audit also caught and removed held-out values that had leaked into the original browser fixture.

## Accomplishments

- executable, unit-tested procedure library rather than prompt-only classification;
- exact information-gain question selection;
- confidence gating and item-level evidence replay;
- signed prediction-then-reveal flow with tamper tests;
- bounded and verified image ingestion;
- restricted verifier for future proposal models;
- deterministic 30-second Judge Mode;
- explicit separation between fixture regression, OCR accuracy, classroom accuracy, and learning impact.

## What we learned

Educational AI becomes more useful when it is willing to say less. The most credible feature was not another prediction; it was an explicit “insufficient evidence” state and the ability to ask the smallest set of questions needed to decide.

## What’s next

Wire and evaluate a privacy-reviewed transcription provider, run the included controlled handwritten pilot, add authentication and student-data governance, expand the procedure library, and then study whether procedure-level grouping improves intervention choices. These are roadmap milestones, not claims made by this prototype.

## Built with

Python, FastAPI, Pydantic, Pillow, vanilla HTML/CSS/JavaScript, deterministic fraction-program inference, HMAC proof tokens, and a restricted JSON expression interpreter.
