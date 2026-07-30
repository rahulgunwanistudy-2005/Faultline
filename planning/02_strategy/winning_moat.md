# Winning Moat

## Positioning

**Faultline is not an AI grader, tutor, quiz generator, or mastery dashboard.** It is a procedure-level diagnostic instrument for teachers.

## The three-layer moat

### 1. Scientific moat: executable hypotheses

Each misconception is a program that predicts an answer for any item. This allows Faultline to do something a descriptive classifier cannot: predict what the student will do next.

### 2. Trust moat: uncertainty is a product feature

Faultline exposes a posterior distribution, OCR uncertainty, item-level evidence, and an “insufficient evidence” state. It earns credibility by refusing to guess.

### 3. Demo moat: prediction before reveal

The video shows the system predict a response to an unseen problem and then reveals the actual held-out page. This compresses technical credibility into fifteen seconds.

## One-sentence explanation

> “Faultline reads the steps in student work, executes every plausible wrong procedure against the same problems, and tells the teacher which procedure best reproduces the pattern—or which three questions will resolve the ambiguity.”

## The anti-generic checklist

Faultline loses its moat if it adds any of the following to the core demo:

- general-purpose student chat;
- lesson-plan generation;
- flashcards or summaries;
- broad “mastery” percentages;
- seven named agents;
- unsupported future-performance predictions;
- badges, streaks, or gamification;
- every subject and grade level;
- a dense admin dashboard.

## Strategic use of the sponsor

Featherless should be visible but bounded:

- use a vision model to return top-k structured readings per crop;
- use an open model to propose a JSON malrule expression when known rules fail;
- show the selected model and latency in an “Evidence Lab” panel;
- keep deterministic scoring and verification outside the model.

This communicates both sponsor relevance and engineering judgment.
