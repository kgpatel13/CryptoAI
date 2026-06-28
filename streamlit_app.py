from __future__ import annotations

import runpy
import sys
from pathlib import Path

# Streamlit Cloud should run this root wrapper.
# Locally, `app/dashboard/main_dashboard.py` works directly.
# This wrapper executes the same file with the repo root on sys.path.

ROOT_DIR = Path(__file__).resolve().parent
DASHBOARD_FILE = ROOT_DIR / "app" / "dashboard" / "main_dashboard.py"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if not DASHBOARD_FILE.exists():
    raise FileNotFoundError(f"Dashboard file not found: {DASHBOARD_FILE}")

runpy.run_path(str(DASHBOARD_FILE), run_name="__main__")
