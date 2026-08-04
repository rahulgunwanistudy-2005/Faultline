#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"

echo "[1/12] Python compile and source sweeps"
python -m compileall -q packages/faultline_core apps/api scripts
python scripts/audit_surface.py

echo "[2/12] JavaScript syntax"
node --check apps/web-static/assets/app.js
node --check apps/web-static/assets/judge.js

echo "[3/12] Frontend freeze verification"
python scripts/check_frontend_freeze.py

echo "[4/12] Generated-asset integrity"
python scripts/generate_demo_asset.py --check

echo "[5/12] Core, API, neural, symbolic, Bayesian, and freeze tests"
pytest -q packages/faultline_core/tests apps/api/tests tests

echo "[6/12] Project dependency consistency"
python scripts/check_dependencies.py

echo "[7/12] Reproducible fixture evaluation"
python scripts/evaluate.py >/dev/null

echo "[8/12] Deterministic Bayesian + neuro-symbolic evaluation"
python scripts/evaluate_bayesian_engine.py >/dev/null
python scripts/evaluate_neuro_symbolic_proposals.py >/dev/null

echo "[9/12] Dataset provenance and checksums (if fetched)"
if [ -f data/evaluation/public_handwriting_subset/provenance.json ]; then
  python scripts/fetch_public_handwriting_subset.py --check
else
  echo "  (skipped: run scripts/fetch_public_handwriting_subset.py to enable)"
fi

echo "[10/12] Live HTTP and signed-proof smoke test"
./scripts/smoke_test.sh

echo "[11/12] Optional local-AI smoke test"
if [ "${FAULTLINE_LOCAL_AI_SMOKE:-0}" = "1" ]; then
  FAULTLINE_RUNTIME_MODE=local_ai python scripts/check_local_model.py
else
  echo "  (skipped: set FAULTLINE_LOCAL_AI_SMOKE=1 with a running model to enable)"
fi

echo "[12/12] Release manifest"
python scripts/build_manifest.py --check

echo "All verified submission gates passed."
