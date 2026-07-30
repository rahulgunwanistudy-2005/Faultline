# Faultline Evaluation Snapshot

> **Dataset:** synthetic deterministic fixture. These results are regression evidence, not a classroom accuracy or learning-impact claim.

- Assigned-procedure top-rank identification: **12/12**
- Named-diagnosis coverage after confidence gating: **11/12**
- Deliberate refusals: **1**
- Held-out leakage: enforced by API test; prediction payload excludes actual answer
- Core and API tests: run `./scripts/verify_submission.sh`

## Metric separation

1. **Engine-on-exact-fixture:** the executable procedure receiving the highest posterior.
2. **Confidence coverage:** how often Faultline allows a named diagnosis.
3. **End-to-end handwriting accuracy:** not claimed yet; use the controlled-pilot protocol before reporting it.
4. **Learning impact:** not claimed; would require a real intervention study.
