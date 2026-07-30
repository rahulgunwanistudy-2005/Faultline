#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"
echo "[1/8] Python compile and source sweeps"
python -m compileall -q packages/faultline_core apps/api scripts
python scripts/audit_surface.py
echo "[2/8] JavaScript syntax"
node --check apps/web-static/assets/app.js
node --check apps/web-static/assets/judge.js
echo "[3/8] Generated-asset integrity"
python scripts/generate_demo_asset.py --check
echo "[4/8] Core and API tests"
pytest -q packages/faultline_core/tests apps/api/tests
echo "[5/8] Project dependency consistency"
python scripts/check_dependencies.py
echo "[6/8] Evaluation snapshot"
python scripts/evaluate.py >/dev/null
echo "[7/8] Live smoke test"
./scripts/smoke_test.sh
echo "[8/8] Release manifest"
python scripts/build_manifest.py --check
echo "All verified submission gates passed."
