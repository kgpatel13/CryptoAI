from __future__ import annotations

import sys
from pathlib import Path

# Streamlit Cloud may execute the app from a nested script context.
# Ensure the repository root is importable so `from app...` imports work.
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import app.dashboard.main_dashboard  # noqa: E402,F401
