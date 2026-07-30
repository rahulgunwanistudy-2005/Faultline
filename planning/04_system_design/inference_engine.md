# Inference Engine Design

## Domain model

Each item contains:

- the fraction operation and operands;
- whether it is bare computation or a matched word problem;
- top-k recognized answer candidates with confidence;
- optional intermediate-step features;
- a held-out flag used only for evaluation/reveal.

Each hypothesis contains:

- a stable identifier;
- eligibility conditions;
- an executable prediction function;
- an optional expected step signature;
- a plain-language description;
- an action category.

## Initial hypothesis library

The winning build should support only a high-quality set:

1. `correct_common_denominator`
2. `add_across` — add numerators and denominators separately
3. `keep_first_denominator` — add numerators but retain the first denominator
4. `denominator_only_common` — create a common denominator but fail to scale numerators
5. `multiply_all` — multiply numerators and denominators despite an addition sign
6. `scale_first_only` — scale the first fraction to the common denominator but leave the second numerator unchanged
7. `no_consistent_procedure`
8. `ocr_uncertain`

Do not claim a rule is literature-derived unless the bibliography supports that exact pattern. Mark rules as literature-grounded, teacher-observed, or pilot-generated.

## Likelihood

For hypothesis `h`, items `i`, and OCR candidate readings `k`:

```text
P(observation_i | h)
  = Σ_k P(OCR candidate k) × P(candidate k | predicted answer under h)
```

Use an explicit response-error model. A simple calibrated implementation is sufficient:

- equivalent answer match: high likelihood;
- mismatch: low likelihood;
- unreadable/invalid: neutral likelihood weighted by OCR uncertainty;
- step-signature match: multiplicative boost;
- step-signature contradiction: penalty.

Then:

```text
P(h | observations) ∝ P(h) × ∏_i P(observation_i | h)
```

Compute in log space and normalize with log-sum-exp.

## Confidence gate

Show a named diagnosis only when all are true:

- at least 5 scorable items;
- mean OCR confidence ≥ 0.85 after review;
- top posterior ≥ 0.70;
- top-to-second posterior ratio ≥ 3;
- the top rule reproduces at least 70% of scorable items.

Otherwise show an ambiguous or insufficient-evidence state and route to diagnostic item selection.

## Matched wording signal

Do not classify “language, not math” from arbitrary failures. Require at least three isomorphic pairs:

- same numerical structure;
- one bare computation item;
- one word problem;
- bare items consistently correct;
- word items consistently incorrect or left blank;
- acceptable OCR confidence.

Output: “The procedure looks intact on bare computation; wording or context may be the barrier.”

## Exact information gain

For candidate item `x`, every executable hypothesis predicts a deterministic answer. Group hypotheses by predicted answer.

```text
IG(x) = H(current posterior)
        - Σ_a P(a | x) H(posterior conditioned on answer a)
```

Choose the highest-IG items with diversity constraints:

- no repeated denominator pair;
- include one visual or word form only when relevant;
- avoid arithmetic complexity that introduces a new skill;
- keep completion under four minutes total.

## Held-out prediction

The held-out item and its recognized answer must never enter the diagnosis input. The server stores it in a separate reveal payload. The prediction endpoint receives only the problem. This separation should be tested.

## Novel-rule synthesis

Trigger only when no known rule reproduces at least 70% of valid items.

1. Send the structured item set and allowed DSL grammar to the Featherless text model.
2. Request up to three candidate JSON expressions and a short description.
3. Parse and validate the JSON.
4. Execute candidates in a safe interpreter.
5. Reject candidates above a complexity threshold.
6. Score reproduction on observed items.
7. Test on generated counterexamples to reject item-specific lookup behavior.
8. Show a candidate only if it meets thresholds; label it “new pattern candidate,” not a confirmed misconception.

The LLM proposes. The verifier decides.
