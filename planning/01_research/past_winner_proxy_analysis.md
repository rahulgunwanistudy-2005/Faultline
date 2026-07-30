# Past-Winner Proxy Analysis

There are no same-event past winners available, so this analysis uses public education-AI winners from other Devpost competitions. These are proxies, not a claim that the judging was identical.

## Proxy projects and transferable patterns

### Zazu — TreeHacks Education Grand Prize

- Began from a specific lived frustration during live lectures.
- Embedded AI inside an existing workflow rather than presenting a detached chatbot.
- Had an immediate real-time “wow” interaction: a spoken command generated a quiz for the class.
- Delivered an end-to-end product, not only a model notebook.

**Transfer to Faultline:** start from Friday-night grading, keep the teacher in the workflow, and make the held-out prediction reveal the magic moment.

### Edu.AI — Google ADK Latin America Regional Winner

- Combined OCR, a full-stack application, persisted history, and structured outputs.
- Made the architecture visible and described implementation challenges honestly.
- Presented a complete experience with a clean UI and real interactions.

**Transfer:** show the worksheet extraction, schema validation, and full pipeline—but do not imitate its many-agent structure unless every component has a real architectural role.

### Nexora — Google ADK EMEA Regional Winner

- Emphasized production readiness, a deployed app, interactive visual learning, and validation.
- Explicitly treated UX as essential to technical innovation.

**Transfer:** the class map and evidence drawer must be visually memorable and fully deployed; the engine alone cannot carry the submission.

### Aspectus — Boost Hacks II First Place

- Used an immersive visual environment rather than a standard form-and-chat interface.
- Connected technical novelty to adaptive education.

**Transfer:** use the “faultline” visual metaphor sparingly to make patterns visible, not as decorative animation.

### AI Courses — FutureHacks Junior Grand Prize

- A solo builder shipped database, API, frontend, Docker, and a live deployment.
- Completeness and visible execution mattered more than research complexity alone.

**Transfer:** as a solo participant, prioritize a complete narrow flow over an ambitious half-built platform.

## What winners consistently signal

1. A problem that can be explained in one sentence.
2. A visible moment where AI changes the interaction.
3. A complete workflow, not a collection of disconnected features.
4. A live or convincingly deployed product.
5. Technical choices tied to the user experience.
6. A story grounded in a person, not “education is broken.”
7. Media and UI that make the result understandable without reading the code.

## Where Faultline can surpass them

Most education-AI projects generate content, tutoring, summaries, or recommendations. Faultline can win by proving an inference. Its competitive sentence is:

> “We do not ask an LLM why a student is wrong. We execute every candidate wrong procedure against the student’s actual problems, show the evidence, and refuse to decide when the evidence is insufficient.”

That sentence should appear in the README, Devpost page, and judge defense.
