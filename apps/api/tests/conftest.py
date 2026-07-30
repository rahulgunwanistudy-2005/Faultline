import os
import sys
from pathlib import Path

os.environ.setdefault("FAULTLINE_PROOF_SECRET", "test-secret-that-is-long-enough-for-hmac")
os.environ.setdefault("FAULTLINE_DEMO_STAGE_MS", "20")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "faultline_core"))
sys.path.insert(0, str(ROOT / "apps" / "api"))
