import sys
import os

# ──────────────────────────────────────────────
# conftest.py — Project-level pytest configuration
# ──────────────────────────────────────────────
#
# This file is automatically loaded by pytest before any tests run.
# Its most important job here is to make sure Python can find our
# `app` package when tests try to do `from app.main import ...`
#
# The Problem:
#   When pytest runs from the project root, Python's import system
#   doesn't automatically know where to look for `app/`.
#   So `from app.main import Matcher` fails with ModuleNotFoundError.
#
# The Fix:
#   We manually add the project root directory to sys.path —
#   the list of places Python searches when you do an import.
#
# sys.path  →  a list of folder paths Python scans during imports
# __file__  →  the absolute path to THIS file (conftest.py)
# os.path.dirname(__file__)  →  the folder containing conftest.py
#                               which is the project root


# Get the absolute path to the project root (the folder this file lives in)
PROJECT_ROOT: str = os.path.dirname(os.path.abspath(__file__))

# Insert the project root at the front of sys.path so it's checked first
# This lets Python resolve `from app.main import ...` correctly
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)