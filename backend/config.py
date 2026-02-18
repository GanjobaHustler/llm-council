"""Configuration for the LLM Council — sourced from council_config.py."""

import sys
import os
from pathlib import Path

# Make the project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from council_config import (  # noqa: E402
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    COUNCIL_MODELS,
    CHAIRMAN,
    TOKEN_CAPS,
    AGENT_BOOTSTRAP_PROMPT,
)

# Legacy compat: some code still references CHAIRMAN_MODEL as a string
CHAIRMAN_MODEL = CHAIRMAN["slug"]

# Data directory for conversation storage
DATA_DIR = os.getenv("DATA_DIR", "data/conversations")
