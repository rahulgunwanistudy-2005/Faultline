#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"

# One-shot local-AI setup helper. Detects macOS/Linux, verifies Ollama and the
# configured model, and runs a structured-output smoke test. No API key required.

VISION_MODEL="${FAULTLINE_VISION_MODEL:-qwen3-vl:4b}"
BASE_URL="${FAULTLINE_OLLAMA_BASE_URL:-http://127.0.0.1:11434}"

case "$(uname -s)" in
  Darwin) PLATFORM="macOS" ;;
  Linux)  PLATFORM="Linux" ;;
  *)      PLATFORM="$(uname -s)" ;;
esac
echo "Platform: ${PLATFORM}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed." >&2
  echo "  macOS: download from https://ollama.com/download" >&2
  echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh" >&2
  exit 1
fi
echo "Ollama found: $(command -v ollama)"

# Verify the server is up (do not start it for the user).
if ! curl -fsS "${BASE_URL}/api/tags" >/dev/null 2>&1; then
  echo "The Ollama server is not responding at ${BASE_URL}." >&2
  echo "Start it in another terminal:  ollama serve" >&2
  exit 2
fi
echo "Ollama server is reachable at ${BASE_URL}"

# Verify the model is present; offer the exact pull command.
if ! ollama list 2>/dev/null | awk '{print $1}' | grep -q "^${VISION_MODEL}$"; then
  echo "Model '${VISION_MODEL}' is not installed." >&2
  echo "Install it:  ollama pull ${VISION_MODEL}" >&2
  exit 3
fi
echo "Model '${VISION_MODEL}' is installed."

echo "Running capability + structured-output smoke test…"
FAULTLINE_RUNTIME_MODE=local_ai python scripts/check_local_model.py

cat <<EOF

Local AI is ready. Start Faultline with:

  export FAULTLINE_RUNTIME_MODE=local_ai
  export FAULTLINE_PROOF_SECRET="\$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
  ./start.sh
EOF
