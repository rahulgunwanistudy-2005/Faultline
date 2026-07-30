# Faultline

**A teacher photographs a stack of student work and gets back the wrong procedure each student is actually running — not a grade, not an unvalidated prediction, and never a made-up improvement number.**

Prometheus July AI Challenge — build spec and pitch, v2 (revised after judge-lens critique + teacher-community source material)

---

## The problem, in a teacher's own words

> "During the lessons they all seem to get it, but test day comes and most of them fail."

> "Over half my class failed their fractions test last week after I doubled up on multiple lessons to reteach, sent the parents the exact test to study from a week in advance, and went over the entire test beforehand with them."

> "I've been teaching for 6 years and this happens so often I truly feel like I just have no actual teaching skills."

These aren't hypothetical. A teacher who did everything conventional practice recommends — reteach, pre-brief, walk through the material — still watched over half her class fail. The in-lesson signal she was using to decide "they've got it, move on" was false. Scaffolded practice makes a student running a wrong procedure look identical to a student who understands. That gap — between what a lesson *looks* like it taught and what a student's work actually *shows* they're doing — is the failure Faultline targets. It is an instrumentation problem, not a teaching-skill problem.

**The persona:** a middle-school math teacher, five sections, ~150 students, one grading pass on a Friday night, then reteaching Monday to the whole class because she can only see who got it wrong, not why.

---

## Why this is not "AI grades homework"

A grader maps *work → score*. Faultline maps *work → the latent procedure that generated the work* — a harder inverse problem, and one where the output is never a mark on a page. It's a class-level breakdown: which students are running which wrong procedure, which have no consistent procedure at all, and which have a language problem rather than a math problem.

Faultline never outputs a fabricated number. No predicted mastery percentage, no simulated "+31% improvement," no digital twin, no forecast of "algebra will decline." Every one of those would require identifying a causal effect from data the system doesn't have — one worksheet, one sitting, ~11 items. A working data scientist judge will ask where the number came from, and manufacturing an answer is a worse failure than not having the feature. Faultline says only what its evidence supports, and says so explicitly in the demo.

---

## Core mechanism

**1. Ingest.** Photo (or stylus capture, as a lower-risk fallback) of a stack of work → page segmentation → per-problem crop → handwriting recognition that preserves *intermediate work lines*, not just final answers. The intermediate steps are the diagnostic signal; reading only final answers throws away most of the evidence.

**2. Hypothesis space, not a single label.** A library of malrules — grounded in the buggy-procedure/cognitive-diagnosis literature (Brown & Burton; VanLehn) — encoded as *executable programs*. Each hypothesis, run against a student's actual item set, predicts specific answers. Two additional non-malrule hypothesis classes matter as much as the malrules themselves:
   - **No consistent procedure** — errors don't fit any executable rule. Not a misconception; an absence of one. Calls for a different intervention than any malrule does.
   - **Language, not math** — correct on bare computation, fails word problems. Directly discriminable from the item set, and it's the exact failure mode ELL students face that gets missed when everything is scored as "wrong."

   Plus a recognition-uncertainty term, so a shaky handwriting read suppresses the diagnosis instead of producing a confident wrong one.

**3. Posterior, not MAP.** Score every hypothesis by how well it reproduces the student's actual answers and intermediate steps across all items. Report the full distribution — e.g. malrule A 42%, malrule B 37%, guessing 14%, OCR uncertainty 7% — not just the top label. This is nearly free given the likelihood scoring already required for step 2, and it's what makes step 4 possible.

**4. Next-best diagnostic question, via information gain.** Because every hypothesis is executable and deterministic, it predicts an exact answer for any candidate item. Expected information gain for item *i* is `H(posterior) − E[H(posterior | answer)]`. Items where all surviving hypotheses agree buy zero bits; items that split the posterior buy the most. This is computed exactly — no training data, no model, just forward simulation of programs that already exist. Output: *"Give these three problems tomorrow — four minutes, and it resolves which of the two things Diego might be doing."*

**5. Novel-bug synthesis, verifier-gated.** When no library rule explains ≥70% of a student's items, an LLM proposes a candidate transformation. That proposal is compiled and executed against the student's actual data and kept **only if it reproduces it**. The LLM is a proposal distribution inside a search loop with a hard executable verifier — it never gets to assert a diagnosis on its own authority.

**6. Decision layer — a transparent rule, not a simulated effect size.** This answers the exact question teachers ask each other: *drill the procedure until it sticks, or re-explain the concept?* The answer is a direct function of the diagnosis, with no invented percentage attached:
   - **Consistent malrule** → don't drill. Practicing a wrong procedure makes it faster, not correct. Re-anchor the concept.
   - **No consistent procedure** → drill is appropriate. There's no wrong habit to entrench.
   - **Language, not math** → neither. The math is fine; the problem is elsewhere.

**Why this needs ML, in one sentence:** the input is handwriting, which isn't machine-readable, and the target is a latent generative procedure that must be inferred from its outputs — the same wrong answer can come from three different bugs, and the same bug produces different wrong answers on different items, so no lookup table can do this.

---

## Interface constraint: no eduspeak

Teachers are openly hostile to jargon like "mastery," "rigor," and acronym soup that drifts from what it originally meant. Faultline's output is written in plain description of what a student is doing — *"12 students are subtracting the numerators and denominators separately"* — never *"12 students demonstrate emerging proficiency in rational number operations."* State this explicitly in the demo. It's a cheap, concrete signal that the product was built from real teacher pain, not from an ed-tech deck.

---

## What was deliberately rejected, and why

| Rejected | Reason |
|---|---|
| Simulated intervention effect sizes ("+31% improvement") | No RCT, no identification strategy, no data to support a causal claim. Fabricating it is the single fastest way to lose credibility with a working data scientist judge. |
| Digital twin (working memory, decay, transfer, learning velocity) | Seven latent dimensions fit to ~11 observations from one sitting. Unidentifiable, and reads as inexperience rather than depth to anyone who checks. |
| Counterfactual mastery forecasting (46% → 81%) | Same problem, worse — compounds an unsupported causal claim with a specific number. |
| Multi-agent architecture (7 labeled "agents") | The stated justification for this was "it's easier to explain" — that's wrapping one model in extra labels, not real architecture. The verifier-gated search loop already in place is a stronger and more honest design. |
| Graph community detection replacing likelihood scoring | Class sizes (~30) are too small for this to add anything, and the existing verifier-gated synthesis already discovers novel bugs — better, because the result is executable and verified rather than an unlabeled cluster. |
| Temporal / longitudinal tracking across weeks | Requires data that doesn't exist from a single Friday worksheet. Roadmap item, not a build item. |

---

## Technical execution plan

**Stack:** React/Next front end, FastAPI backend, Postgres, background job queue for the OCR/handwriting stage so the UI never blocks on it.

**The malrule engine** lives as an isolated, dependency-free Python module. Every malrule ships with a unit test asserting it reproduces a known response pattern from the published cognitive-diagnosis literature. This test suite, visible in the repo, is the strongest available signal that the core is real inference rather than vibes.

**Two things that make this read as production software, not a hackathon hack:**
- **Confidence gating.** Below a threshold, the system reports "insufficient evidence — 3 more items needed on this skill" and shows nothing further. Engineered restraint reads as maturity.
- **A stated diagnostic accuracy number.** Collect ~25 hand-written responses under assigned malrules for ground truth, and show a confusion matrix. Almost no team in a large field will have one.

**Risk to plan around:** handwriting recognition variance. Mitigate with a stylus/tablet capture path alongside photo upload, and a fully verified demo set.

---

## Demo narrative (2:00)

**0:00–0:12** — On screen, read aloud: *"She did everything right. Over half failed."*

**0:12–0:30** — "Here's why. During the lesson, they all seemed to get it." Show a scaffolded practice problem going fine. "That signal is false."

**0:30–0:55** — Real photo of a real stack. Upload. A few seconds later, a class heatmap appears — three groups, plain-English labels, zero jargon.

**0:55–1:15** — Zoom to one student. Show the reconstructed posterior and the leading hypothesis. Then Faultline **predicts his answer to a problem he hasn't done yet** — cut to a held-out page showing his actual answer. It matches. This is the single strongest fifteen seconds available: it proves the model is real rather than decorative, without a word of jargon.

**1:15–1:35** — The ambiguous case: two hypotheses near-tied. "We don't guess. Here are the three problems that separate them — four minutes tomorrow."

**1:35–1:50** — The decision layer: one group shouldn't drill, one should, one doesn't have a math problem at all.

**1:50–2:00** — Close: *"We don't predict how much she'll improve. We won't invent that number. We tell her which of the two things she was already choosing between is the right one."*

---

## Projected score (out of 100, four judges' lenses)

| Category | Score | Driver |
|---|---|---|
| Educational Impact | 25/25 | Real teacher language, the language-vs-math split, a direct answer to the question teachers actually ask each other |
| Creative Use of AI/ML | 24/25 | Full inference story — posterior, exact information gain via forward simulation, verifier-gated synthesis — with zero unsupported claims |
| Technical Execution | 22/25 | Deterministic, tested core; confidence gating and a confusion matrix as polish signals; handwriting recognition is the residual risk |
| Pitch and Demo | 24/25 | Sharper hook from real teacher testimony, prediction-then-reveal as the centerpiece, honest close |
| **Total** | **95** | |

---

## Defend list — prepared answers for judge questions

**"Your decision layer is a rule, not a model — where's the ML?"**
Correct, and deliberate. The ML is in the inverse inference (recovering a latent procedure from handwritten work) and the experimental design (information-gain question selection). The decision layer is a transparent rule because the effect-size data needed to *learn* it doesn't exist from one worksheet — and manufacturing that data would have been the easier, and worse, choice.

**"What about tracking students over time?"**
Deliberately out of scope for this build, and stated as a roadmap item with the reason given openly: one worksheet is what a teacher actually has on a Friday night. Building for longitudinal data she doesn't have is how ed-tech tools end up unused.