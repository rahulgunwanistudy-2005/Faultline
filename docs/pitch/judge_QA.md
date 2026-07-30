# Judge Q&A — v0.2.0

## “Isn’t this just AI grading homework?”

No. Grading maps work to a score. Faultline maps a pattern of work to the executable procedure that could have generated it, shows competing hypotheses, and tests that inference on a held-out response.

## “Where is the AI in the current build?”

The verified runtime performs probabilistic latent-procedure inference and exact Bayesian experimental design over executable hypotheses. The repository contains bounded interfaces for future vision transcription and rule proposals, but live model calls are deliberately disabled until their contracts and accuracy are tested. Do not claim live OCR in this release.

## “How do you know the rule is correct?”

We do not claim certainty. We score every eligible rule, show the posterior and item-level reproduction, require a confidence gate, and test a locked prediction against separately revealed demo work. Ambiguous cases receive diagnostic questions instead of a label.

## “Could two rules give the same answers?”

Yes. That is why Faultline reports a distribution and uses information gain to choose an item where the surviving rules disagree.

## “What if handwriting recognition is wrong?”

That is the next evaluation gate. The architecture accepts candidate readings and confidence, supports reviewed corrections, and can suppress diagnosis when confidence is low. The present release does not report a handwriting metric because live OCR is not enabled.

## “Are you diagnosing English-language learners?”

No. The system only reports an observable matched pattern: correct on bare computation and difficulty on word problems. The UI says wording or context may be the barrier. It does not infer identity, language proficiency, disability, or cause.

## “Does an LLM invent misconceptions?”

Not in the verified runtime. A future model may propose a restricted JSON expression only. The interpreter has no imports, I/O, item IDs, Python evaluation, or network access, and the verifier rejects proposals that fail reproduction or counterexample checks.

## “Why not use a seven-agent system?”

Agents would add labels, not evidence. The central problem needs executable hypotheses, calibrated uncertainty, and a verifier.

## “What does the 12/12 number mean?”

Only that the assigned executable procedure ranks first for all 12 synthetic fixture records. It is a regression check for the engine. It is not OCR accuracy, real-student accuracy, or a learning-outcome claim.

## “Why fractions?”

Fractions contain systematic errors and provide a constrained domain where different procedures make different predictions. That lets the project demonstrate a deep, falsifiable mechanism rather than a shallow all-subject chatbot.

## “How does this help Monday morning?”

The class map routes students into different next actions, and unresolved cases receive the few questions with the highest expected information gain. The result is a teacher decision, not another score dashboard.

## “What is your biggest limitation?”

The project currently uses a fixed template and synthetic readings. Real handwriting, crossed-out work, authentication, student-data governance, and classroom validation remain incomplete and are stated openly.
