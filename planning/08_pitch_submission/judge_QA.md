# Judge Q&A

## “Isn’t this just AI grading homework?”

No. Grading maps work to a score. Faultline maps a pattern of work to the executable procedure that could have generated it, shows competing hypotheses, and predicts a response on a new item.

## “Where is the machine learning?”

The image input requires vision inference, and the latent-procedure inference combines uncertain transcriptions across items. The next-question selector performs exact Bayesian experimental design over executable hypotheses. The final teacher action is deliberately transparent rather than learned from nonexistent outcome data.

## “How do you know the rule is correct?”

We do not claim certainty. We score every eligible rule, show the posterior and item-level reproduction, require a confidence gate, and evaluate on held-out responses. Ambiguous cases receive diagnostic questions instead of a label.

## “Could two rules give the same answers?”

Yes. That is why Faultline reports a distribution rather than only the maximum and uses information gain to choose an item where the rules disagree.

## “What if OCR is wrong?”

The vision stage returns candidates and confidence. Low-confidence readings are reviewed. OCR uncertainty is marginalized into the posterior, and the seeded demo remains independent of external model availability.

## “Are you diagnosing English-language learners?”

No. The system only flags a matched pattern: correct on isomorphic bare computation and difficulty on word problems. The UI says wording or context may be the barrier. It does not infer a student identity or cause.

## “Does the LLM invent misconceptions?”

It may propose a restricted JSON expression only after known rules fail. A safe interpreter executes the proposal, checks reproduction and complexity, and rejects it unless it passes. It is shown as a provisional new-pattern candidate.

## “Why not use a seven-agent system?”

Agents would add labels, not evidence. The core problem needs a deterministic inference loop and a verifier. We use model calls only where perception or proposal generation is genuinely needed.

## “What does your accuracy number mean?”

We show three numbers separately: OCR transcription accuracy, engine identification on exact transcriptions, and end-to-end accuracy in a controlled assigned-procedure handwriting pilot. The pilot does not claim classroom learning impact.

## “Why fractions?”

Fractions contain well-documented systematic errors and provide a constrained domain where different procedures make different predictions. That lets us prove the approach deeply rather than demo a shallow all-subject chatbot.

## “How does this help Monday morning?”

The class map routes students into distinct actions and the tomorrow card provides the few questions needed for unresolved cases. The result is a teaching decision, not another analytics screen.

## “What is your biggest limitation?”

Handwriting and crossed-out work remain difficult. The product exposes that uncertainty, supports correction, and limits the current build to a fixed worksheet template and one skill.
