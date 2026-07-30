# Worksheet and Handwriting Pipeline

## Winning choice: constrain the page

Use a branded Faultline demo worksheet with fixed problem boxes and QR/template ID. This turns page segmentation from a computer-vision research problem into reliable product engineering.

## Pipeline

1. Normalize orientation and contrast.
2. Detect template using QR or corner anchors.
3. Apply stored crop coordinates for each problem.
4. Send each crop to a Featherless vision-capable model with the problem statement and a strict schema.
5. Request:
   - final answer candidates;
   - confidence per candidate;
   - normalized intermediate expressions;
   - step features from an allow-list;
   - unreadable-region flags.
6. Validate the response.
7. Route low-confidence crops to teacher review.
8. Persist only normalized structured readings needed by the engine.

## Example response schema

```json
{
  "problem_id": "p04",
  "answer_candidates": [
    {"value": "5/9", "confidence": 0.88},
    {"value": "5/18", "confidence": 0.09}
  ],
  "step_features": [
    "numerators_added",
    "denominators_added"
  ],
  "unreadable_regions": [],
  "notes": ""
}
```

## Prompt principle

The vision model must transcribe, not diagnose. Never ask “What misconception does this show?” in the OCR prompt. Diagnosis belongs to the executable engine.

## Fallbacks

- Teacher correction UI.
- Stylus/manual answer entry.
- Seeded demo fixture using real pre-verified crops.
- API timeout converts to review state, not a failed class analysis.

## Evaluation

Measure exact normalized-expression match by crop. Separately measure step-feature precision and recall. Do not blend OCR and diagnostic accuracy into one number.
