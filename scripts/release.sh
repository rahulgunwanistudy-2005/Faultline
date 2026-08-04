#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="packages/faultline_core:apps/api${PYTHONPATH:+:$PYTHONPATH}"

VERSION="${FAULTLINE_RELEASE_VERSION:-0.3.0}"
BUILD_DIR="build/release"
STAGE="${BUILD_DIR}/faultline-${VERSION}"
ZIP_PATH="${BUILD_DIR}/faultline-${VERSION}.zip"

echo "== Faultline release ${VERSION} =="

echo "[1/11] Confirm derived assets are current (frozen frontend is not rewritten)"
python scripts/generate_demo_asset.py --check

echo "[2/11] Read-only verification gates"
./scripts/verify_submission.sh

echo "[3/11] Regenerate release manifest"
python scripts/build_manifest.py

echo "[4/11] Re-validate manifest"
python scripts/build_manifest.py --check

echo "[5/11] Confirm frontend freeze"
python scripts/check_frontend_freeze.py

echo "[6/11] Build clean release directory"
rm -rf "$BUILD_DIR"
mkdir -p "$STAGE"
rsync -a \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  --exclude 'node_modules/' \
  --exclude 'build/' \
  --exclude 'dist/' \
  --exclude '.env' \
  --exclude '*.log' \
  --exclude '.DS_Store' \
  --exclude 'data/evaluation/results/' \
  --exclude 'data/evaluation/public_handwriting_subset/images/' \
  ./ "$STAGE/"

echo "[7/11] Verify no secrets or private data leaked into the stage"
if grep -rqiE 'FAULTLINE_PROOF_SECRET=.+[A-Za-z0-9]{16}' "$STAGE" 2>/dev/null; then
  echo "Refusing to package: a concrete proof secret is present." >&2
  exit 1
fi
if [ -d "$STAGE/data/evaluation/public_handwriting_subset/images" ]; then
  echo "Refusing to package: licensed dataset images were not excluded." >&2
  exit 1
fi

echo "[8/11] Create ZIP"
( cd "$BUILD_DIR" && zip -qr "faultline-${VERSION}.zip" "faultline-${VERSION}" )

echo "[9/11] Extract to a temporary directory"
VERIFY_DIR="$(mktemp -d)"
unzip -q "$ZIP_PATH" -d "$VERIFY_DIR"

echo "[10/11] Verify the extracted release"
(
  cd "$VERIFY_DIR/faultline-${VERSION}"
  export PYTHONPATH="packages/faultline_core:apps/api"
  python -m compileall -q packages/faultline_core apps/api scripts
  python scripts/check_frontend_freeze.py
  python scripts/build_manifest.py --check
)
rm -rf "$VERIFY_DIR"

echo "[11/11] SHA-256"
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$ZIP_PATH"
else
  sha256sum "$ZIP_PATH"
fi

echo "Release ready: ${ZIP_PATH}"
