"""
pytest configuration for alkemist-server tests.
"""

import sys
from pathlib import Path

# Ensure alkemist-server root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
