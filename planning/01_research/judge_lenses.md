# Judge Lenses

The event lists a mixed panel. Several public profile matches suggest experience in data science, Azure OpenAI, production software, responsible AI, agent systems, and trustworthy AI. These matches are public-web signals and are **not guaranteed to be organizer-verified identities**. Use them only to anticipate reasonable technical questions.

## Likely lenses

| Lens | What earns trust | What loses trust | Faultline response |
|---|---|---|---|
| Data scientist | Defined ground truth, held-out tests, confusion matrix, separated metrics | A made-up “31% improvement” or one blended accuracy number | Controlled protocol; OCR, engine, and end-to-end metrics shown separately |
| AI platform engineer | Structured outputs, retries, model adapter, clear AI boundary | Raw free-form model text driving the UI | JSON schema, candidate list, validation, manual correction |
| Production engineer | Stable demo, failure states, tests, observability, idempotent jobs | A happy-path mock and broken upload | Deterministic demo mode, job status, fixtures, core unit tests |
| Responsible-AI builder | Uncertainty, human review, privacy, scope limits | Confident labels from weak handwriting evidence | Confidence gate, “insufficient evidence,” no student names required |
| Product/UX judge | Immediate value and an intuitive flow | Dense dashboards and abstract ed-tech language | Plain-English class map and a single “tomorrow” action |
| Student organizer/community educator | Accessibility, clarity, inspiration, practical reach | A research demo nobody can understand | Two-minute story and zero jargon in the teacher interface |

## Questions to design for

1. How do you know the detected rule is the one the student is using?
2. What happens when two rules explain the same answers?
3. What happens when OCR is wrong?
4. Is the “language barrier” claim actually supported?
5. Does the LLM invent new misconceptions?
6. Why is a rule-based decision layer still AI/ML?
7. What accuracy was measured and on what population?
8. Can I run this repository without private data?
9. What is real in the demo versus precomputed?
10. Why would a teacher use this instead of grading normally?

Every answer is prepared in `08_pitch_submission/judge_QA.md`.
