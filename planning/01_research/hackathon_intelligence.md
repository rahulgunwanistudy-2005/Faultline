# Hackathon Intelligence

## Official brief

The Prometheus July AI Challenge asks participants to build an educational tool using AI or ML to improve how people learn, teach, or absorb information. It is student-only, allows solo participation or teams of up to four, requires source code and a working prototype, and requires a demo video no longer than two minutes.

### Official judging criteria

| Criterion | Weight | What the official wording rewards | Faultline proof |
|---|---:|---|---|
| Educational Impact | 25 | A real educational problem and genuine help for learning or teaching | Real teacher pain; class-level grouping by procedure; actionable next step |
| Creative Use of AI/ML | 25 | AI must be clever, meaningful, and core | Vision extraction + latent-procedure inference + exact information gain + verifier-gated synthesis |
| Technical Execution | 25 | Functional, stable, intuitive; code, UI and UX quality | Tested isolated engine; confidence gating; OCR correction; deployed deterministic demo |
| Pitch & Demo | 25 | Clear, concise, engaging two-minute explanation of why and how | Hook, upload, prediction reveal, ambiguity refusal, actionable close |

## Competition density

The public page showed roughly 900+ registered participants near the deadline. Registration does not equal completed submissions, but it means the project must be legible in seconds and differentiated from common AI tutors, quiz generators, summarizers, flashcard tools, and generic “personalized learning” dashboards.

## Sponsor signal

Featherless.ai is the listed sponsor. Its API is OpenAI-compatible and supports vision-capable models. Use Featherless in two places where it is genuinely useful:

1. **Vision extraction:** convert a worksheet crop into structured candidate answers and intermediate-step features.
2. **Novel-rule proposal:** propose a small JSON expression only after the known malrule library fails; the deterministic verifier decides whether the proposal survives.

Do not turn the architecture into “many agents” merely to advertise an AI stack. The strongest sponsor integration is visible, bounded, and testable.

## Rule risks

- The Devpost banner displays 11:45 PM EDT; the text rules say 11:59 PM. Submit by the earlier time.
- The overview says the challenge begins July 17; the originality rule says code must be written July 8–30. Preserve Git history and a build log.
- Anything after two minutes will not be watched. Target 1:55–1:59.
- A repository link alone is insufficient; judges must see a complete, understandable result in the video and Devpost media.

## No direct historical winners

This appears to be the first publicly indexed Prometheus July AI Challenge. The current project gallery was unpublished during research, so there are no same-event historical winners to analyze. The correct methodology is therefore:

- use the official rubric as the primary source;
- examine the public judge backgrounds as directional signals, not personal targeting;
- use comparable winning education-AI projects as proxy evidence;
- avoid pretending proxy competitions had identical rubrics.

## Strategic conclusion

Faultline is already better positioned than a generic educational chatbot because it solves a teacher workflow, not a broad learning aspiration. To win, the implementation must preserve that specificity. The enemy is not insufficient features; it is losing the idea’s credibility through weak OCR, unsupported “impact” numbers, generic visual design, or an opaque LLM diagnosis.
