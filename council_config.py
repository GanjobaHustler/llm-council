# ============================================================
#  LLM COUNCIL — AGENT CONFIGURATION
#  The agent will handle API key injection and model routing.
#  Fill in your OpenRouter key below. Touch nothing else.
# ============================================================

import os

# ── API KEY ─────────────────────────────────────────────────
# Prefer environment variable (set in Railway) over hardcoded value
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "REDACTED"
)

# ── BASE CONFIG ──────────────────────────────────────────────
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_URL  = f"{OPENROUTER_BASE_URL}/chat/completions"

# ── COUNCIL MEMBERS (LOCKED) ─────────────────────────────────
COUNCIL_MODELS = [
    {
        "slug":              "anthropic/claude-sonnet-4-6",
        "alias":             "B.A. — Strategist",
        "max_tokens_phase1": 600,
        "max_tokens_phase2": 300,
    },
    {
        "slug":              "openai/gpt-5.2",
        "alias":             "Face — Analyst",
        "max_tokens_phase1": 600,
        "max_tokens_phase2": 300,
    },
    {
        "slug":              "x-ai/grok-4.1",
        "alias":             "Murdock — Intel",
        "max_tokens_phase1": 600,
        "max_tokens_phase2": 300,
    },
    {
        "slug":              "moonshotai/kimi-k2-5",
        "alias":             "H.M. — Specialist",
        "max_tokens_phase1": 600,
        "max_tokens_phase2": 300,
    },
]

# ── CHAIRMAN (LOCKED) ────────────────────────────────────────
CHAIRMAN = {
    "slug":       "google/gemini-3-pro",
    "alias":      "Hannibal — Chairman",
    "max_tokens": 1000,
}

# ── AGENT PROMPT ─────────────────────────────────────────────
AGENT_BOOTSTRAP_PROMPT = """
You are the Council Coordinator agent. Your job is to wire up and
validate the LLM Council before any session begins.

On startup, execute the following steps in order:

STEP 1 — INJECT API KEY
  Set the OPENROUTER_API_KEY from council_config.py as the bearer
  token in the Authorization header for all outgoing requests.
  Base URL: https://openrouter.ai/api/v1

STEP 2 — VALIDATE MODELS
  Ping each model slug in COUNCIL_MODELS + CHAIRMAN via a 1-token
  health check. If a model returns a non-200, log the slug, skip it,
  and continue. Do not halt the session over a single model failure.

STEP 3 — REGISTER ALIASES
  Map each slug to its alias. All internal logs and UI labels must
  use the alias (e.g. "B.A. — Strategist"), never the raw slug.

STEP 4 — ENFORCE TOKEN CAPS
  Attach max_tokens from each model's config block to every API call.
  Under no circumstances exceed these caps, regardless of prompt size.

STEP 5 — CONFIRM READY STATE
  Print a council manifest to console:
    ✅ [alias] → [slug] (ONLINE)
    ❌ [alias] → [slug] (UNREACHABLE — skipped)
  Then print: "⚔️  A-Team Council is live. Awaiting first query."

PHASE ROUTING RULES:
  Phase 1 → send user prompt to all COUNCIL_MODELS in parallel
  Phase 2 → send all Phase 1 responses to each model for peer review
  Phase 3 → send all Phase 1 + Phase 2 outputs to CHAIRMAN for synthesis

The CHAIRMAN speaks last and always delivers the final verdict.
You do not add commentary. You route, enforce caps, and report status.
"""

# ── TOKEN CAP SUMMARY ────────────────────────────────────────
TOKEN_CAPS = {
    "phase1_input":   700,
    "phase1_output":  600,
    "phase2_input":  3100,
    "phase2_output":  300,
    "phase3_input":  4400,
    "phase3_output": 1000,
}
