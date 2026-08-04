# Public handwriting benchmark subset (HASYv2)

This is a **small public benchmark subset** for evaluating the local vision
model's symbol transcription. **It is not classroom outcome evidence.**

## What this is (and is not)

- **Source:** HASYv2 — 168k handwritten mathematical symbols, Martin Thoma (2017).
  DOI [10.5281/zenodo.259444](https://doi.org/10.5281/zenodo.259444).
- **License:** ODC Open Database License v1.0 (ODbL). Attribution required.
- **Content:** 28 single handwritten symbols (digits and `+ - = /`), 32×32 PNGs.
- **Evaluates:** transcription / symbol recognition **only**. These are single
  symbols, not full student worksheets, so they carry **no** procedure-level
  ground truth and are `usable_for_end_to_end_diagnosis = false`.
- The deterministic engine's regression metrics come from the **synthetic**
  fixture (`data/demo_class.json`), which is labelled separately as synthetic.

## Privacy

The source records only a pseudonymous integer `user_id`. There are **no** names,
faces, or school identifiers. `contains_real_student_information = false`.

## Files

- `provenance.json` — source, license, retrieval date, archive MD5, per-image SHA-256.
- `labels.csv` — one row per image; `expected_symbol` is the ground-truth LaTeX.
- `images/` — the 28 retained PNGs.

## Reproduce / verify / remove

```bash
python scripts/fetch_public_handwriting_subset.py          # re-fetch (idempotent)
python scripts/fetch_public_handwriting_subset.py --check  # verify checksums
rm -rf data/evaluation/public_handwriting_subset/images    # remove the images
```

## Redistribution

ODbL permits redistribution with attribution and share-alike. To avoid any
mis-licensing of the competition package, the `images/` directory is **excluded
from the public release ZIP** (`scripts/release.sh`); the fetch script, labels,
and provenance remain so the subset can be regenerated on demand.
