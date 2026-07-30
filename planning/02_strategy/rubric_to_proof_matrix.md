# Rubric-to-Proof Matrix

The project is not optimized by adding features. It is optimized by ensuring every rubric point has a visible proof artifact.

| Rubric | Judge question | Product proof | Repository proof | Video proof | Failure to avoid |
|---|---|---|---|---|---|
| Educational Impact | Does this solve a painful education problem? | One stack becomes three actionable groups | Persona, workflow and matched-item design | Teacher quote → class map → Monday action | “Personalized learning” claims without a concrete decision |
| Educational Impact | Does the output change what a teacher does? | Re-explain / practice / check wording | Transparent decision table | Three groups receive three different next actions | Only describing errors or assigning grades |
| Creative AI/ML | Is AI essential? | Handwriting extraction and latent procedure inference | Model adapter, posterior scorer, executable malrules | Show raw work become a procedure hypothesis | Chatbot wrapper or prompt-only diagnosis |
| Creative AI/ML | Is the approach clever? | Next-best diagnostic questions | Exact information-gain implementation | Ambiguous case gets three high-value items | Random worksheet generation |
| Creative AI/ML | Is generation trustworthy? | Novel-rule candidate appears only after verification | Safe JSON DSL and verifier tests | “The model proposes; the program decides” | Executing model-generated Python or trusting free text |
| Technical Execution | Is it functional? | Deterministic upload-to-result flow | Fixtures, integration tests, seeded demo | Zero cuts during the main interaction | Figma-only flow or hidden manual steps |
| Technical Execution | Is it stable? | OCR review and confidence gate | Retry policy, typed schemas, job status | Demonstrate “insufficient evidence” | Confidently wrong result on unreadable work |
| Technical Execution | Is the UI intuitive? | Class map, evidence drawer, tomorrow card | Component storybook or screenshots | Cursor path is obvious and uncluttered | Dense analytics dashboard |
| Pitch & Demo | Can I understand it fast? | Judge Mode | Script and storyboard | Hook in first 8 seconds | Spending 40 seconds on architecture |
| Pitch & Demo | Is the project real? | Held-out prediction reveal | Evaluation fixtures and test output | Prediction shown before answer reveal | Narrating features without proof |

## Target score

| Category | Target | Required condition |
|---|---:|---|
| Educational Impact | 25/25 | Teacher workflow and decision visibly change |
| Creative AI/ML | 25/25 | Core inference, information gain and verifier are clearly real |
| Technical Execution | 24/25 | Deployed, tested, polished, with honest OCR fallback |
| Pitch & Demo | 25/25 | 1:55–1:59, captions, prediction reveal, memorable close |
| **Target** | **99/100** | No major happy-path failure |

A realistic win does not require literal perfection, but building to a 99-point internal standard prevents avoidable losses.
