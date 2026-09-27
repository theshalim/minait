"""Vercel serverless entrypoint.

Vercel's Python runtime detects the `app` ASGI application exported here and
routes every request configured in vercel.json's rewrites to it.
"""
import sys
from pathlib import Path

# Make the project root importable (so `import app...` works when this file
# runs as an isolated serverless function).
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402
