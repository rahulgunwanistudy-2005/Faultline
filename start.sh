#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
MODE="${FAULTLINE_RUNTIME_MODE:-fixture}"

# Refuse to start on a busy port and show what is holding it (no process is killed).
if command -v lsof >/dev/null 2>&1; then
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $PORT is already in use by:" >&2
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >&2 || true
    echo "Set PORT=<free port> and retry." >&2
    exit 1
  fi
fi

# In local-AI mode, check the model is reachable and print exact setup commands.
if [ "$MODE" = "local_ai" ]; then
  echo "Runtime mode: local_ai — checking the local model…"
  if ! python scripts/check_local_model.py; then
    cat >&2 <<'EOF'

The local model is not ready. Set it up with:

  ollama serve                       # terminal 1
  ollama pull "${FAULTLINE_VISION_MODEL:-qwen3-vl:4b}"   # terminal 2
  ./scripts/setup_local_ai.sh

Or run the deterministic fixture instead:

  FAULTLINE_RUNTIME_MODE=fixture ./start.sh
EOF
    exit 1
  fi
else
  echo "Runtime mode: fixture (deterministic, no model required)."
fi

echo "Starting Faultline on http://${HOST}:${PORT}  (mode: ${MODE})"
echo "  App:    http://localhost:${PORT}"
echo "  Judge:  http://localhost:${PORT}/judge"
echo "  Health: http://localhost:${PORT}/health"
echo "  Runtime: http://localhost:${PORT}/v1/runtime"

exec python -m uvicorn faultline_api.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --workers "${UVICORN_WORKERS:-1}" \
  --proxy-headers \
  --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-127.0.0.1}"
