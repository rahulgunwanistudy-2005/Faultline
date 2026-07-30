# Claims Register

This register separates implemented behavior, synthetic regression evidence, and work that has **not** been validated.

| Claim | Status | Reproducible evidence |
|---|---|---|
| Candidate fraction procedures are executable programs, not free-form model labels | Implemented | `packages/faultline_core/faultline_core/malrules.py`; core tests |
| Candidate procedures are scored against every visible observation | Implemented | `inference.py`; evidence rows returned by `/v1/demo/classes/period-3` |
| Recognition confidence can suppress a named diagnosis | Implemented | `confidence_gate`; low-confidence Jai fixture and tests |
| The public class payload and bundled browser fixture contain no held-out answer or predicted answer | Implemented | API/privacy tests and `scripts/generate_demo_asset.py --check` |
| A prediction is signed before the held-out answer is revealed | Implemented for the deterministic demo | HMAC proof-token service; tamper and cross-student tests |
| Diagnostic questions are ranked by exact expected information gain over executable hypotheses | Implemented | `information_gain.py`; ranking tests |
| Model-proposed rules cannot execute Python, import modules, access I/O, or inspect item IDs | Implemented | restricted expression DSL and verifier tests |
| Uploaded images are bounded, decoded as real PNG/JPEG images, normalized, segmented, and not persisted | Implemented | raw-body endpoint, Pillow verification, segmentation tests, upload metadata |
| Uploaded handwriting is transcribed by a live model | **Not implemented** | live vision adapter is intentionally disabled |
| Uploaded work drives the displayed diagnoses | **Not implemented in this release** | the upload is validated/segmented, then the UI clearly switches to the synthetic regression fixture |
| Assigned procedure ranks first for 12/12 synthetic students | Synthetic fixture regression only | `python scripts/evaluate.py` |
| Named-diagnosis coverage is 11/12 on the synthetic fixture | Synthetic fixture regression only | `python scripts/evaluate.py` |
| General handwriting/OCR accuracy | **Not measured** | controlled handwritten pilot required |
| Accuracy on real students | **Not measured** | consented, independently reviewed evaluation required |
| Classroom learning improvement or causal impact | **Not claimed** | would require an intervention study |

Never convert the synthetic 12/12 result into a classroom accuracy percentage or improvement claim.
