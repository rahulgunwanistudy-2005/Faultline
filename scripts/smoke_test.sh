#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8127}"
LOG="${TMPDIR:-/tmp}/faultline-smoke.log"
cd "$ROOT"
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"
export FAULTLINE_PROOF_SECRET="${FAULTLINE_PROOF_SECRET:-smoke-test-proof-secret}"
python -m uvicorn faultline_api.main:app --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT
for _ in $(seq 1 40); do
  if curl -fs "http://127.0.0.1:$PORT/health" >/dev/null; then break; fi
  sleep .2
done
curl -fsS "http://127.0.0.1:$PORT/" | grep -q "See the procedure behind the error"
curl -fsS "http://127.0.0.1:$PORT/judge" | grep -q "30-second Judge Mode"
curl -fsS "http://127.0.0.1:$PORT/v1/demo/classes/period-3" > /tmp/faultline-class.json
python - <<'PY'
import json
p=json.load(open('/tmp/faultline-class.json'))
assert p['summary']['students']==12
assert p['summary']['withheld']==1
text=json.dumps(p)
assert 'actual_answer' not in text
assert 'predicted_answer' not in text
PY
PREDICTION="$(curl -fsS -X POST "http://127.0.0.1:$PORT/v1/students/bea/held-out-prediction")"
TOKEN="$(printf '%s' "$PREDICTION" | python -c 'import json,sys; p=json.load(sys.stdin); assert "actual_answer" not in p; print(p["proof_token"])')"
curl -fsS -X POST "http://127.0.0.1:$PORT/v1/students/bea/held-out-reveal" \
  -H 'Content-Type: application/json' \
  --data "{\"proof_token\":\"$TOKEN\"}" \
  | python -c 'import json,sys; p=json.load(sys.stdin); assert p["matched"] is True'
echo "Smoke test passed on port $PORT"
