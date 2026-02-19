"""
Per-conversation system prompt templates for the LLM Council.

Each template defines a system prompt that gets injected into every
council phase (Phase 1 responses, Phase 2 rankings, Phase 3 synthesis).
"""

from typing import Dict, List, Optional
from pathlib import Path

# Where markdown prompt files live
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_md(filename: str) -> str:
    """Load a .md file from the prompts/ directory."""
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ── TEMPLATE REGISTRY ─────────────────────────────────────────

TEMPLATES: List[Dict[str, str]] = [
    {
        "id":          "blank",
        "name":        "Blank",
        "description": "No system prompt — raw council mode.",
        "prompt":      "",
    },
    {
        "id":          "fanvue_copilot",
        "name":        "Fanvue Copilot Engineering",
        "description": "Full-stack engineering copilot for the Fanvue platform. "
                       "9 problem domains, 3-layer classification, 40-point metrics.",
        "prompt":      "LAZY_LOAD:fanvue_copilot.md",
    },
    {
        "id":          "architecture",
        "name":        "Architecture Review",
        "description": "System design and architecture evaluation. "
                       "Trade-off analysis, scalability, maintainability.",
        "prompt": (
            "You are a senior systems architect on a review council. "
            "Evaluate all proposals through these lenses:\n"
            "1. SCALABILITY — Will it handle 10x/100x growth?\n"
            "2. MAINTAINABILITY — Can a new engineer understand this in a day?\n"
            "3. COST — What are the infrastructure and operational costs?\n"
            "4. SECURITY — What attack surface does this create?\n"
            "5. TRADE-OFFS — Explicitly state what you're sacrificing for each gain.\n\n"
            "Be specific. Reference concrete technologies, patterns, and failure modes. "
            "No hand-waving. If you don't know, say so."
        ),
    },
    {
        "id":          "pivot",
        "name":        "Strategic Pivot Analysis",
        "description": "Product strategy and pivot evaluation. "
                       "Market fit, risk, execution feasibility.",
        "prompt": (
            "You are a strategic advisor on a product council. "
            "Evaluate all proposals through these lenses:\n"
            "1. MARKET FIT — Is there validated demand? What's the TAM?\n"
            "2. COMPETITIVE MOAT — What stops incumbents from copying this?\n"
            "3. EXECUTION RISK — What could kill this in the next 90 days?\n"
            "4. UNIT ECONOMICS — Does the math work at scale?\n"
            "5. TEAM-FIT — Can the current team actually build this?\n\n"
            "Be brutally honest. Founders need truth, not encouragement. "
            "Quantify where possible."
        ),
    },
    {
        "id":          "code_review",
        "name":        "Code Review",
        "description": "Deep code review with focus on correctness, "
                       "performance, and security.",
        "prompt": (
            "You are a principal engineer conducting a code review. "
            "Evaluate all code through these criteria:\n"
            "1. CORRECTNESS — Does it do what it claims? Edge cases?\n"
            "2. PERFORMANCE — Time/space complexity, hot paths, allocations\n"
            "3. SECURITY — Injection, auth bypass, data exposure, SSRF\n"
            "4. READABILITY — Could a mid-level dev maintain this?\n"
            "5. TESTING — What tests are missing? What mocks are needed?\n"
            "6. IDIOMATIC — Does it follow language/framework conventions?\n\n"
            "Cite specific line numbers. Suggest concrete fixes, not vague improvements. "
            "Severity: 🔴 blocker / 🟡 should-fix / 🟢 nit."
        ),
    },
    {
        "id":          "data_pipeline",
        "name":        "Data Pipeline Review",
        "description": "ETL/ELT pipeline design and reliability analysis.",
        "prompt": (
            "You are a data engineering lead reviewing pipeline designs. "
            "Evaluate through these dimensions:\n"
            "1. RELIABILITY — Exactly-once? At-least-once? Idempotency?\n"
            "2. LATENCY — Batch windows, streaming lag, SLA compliance\n"
            "3. SCHEMA EVOLUTION — How do you handle breaking changes?\n"
            "4. OBSERVABILITY — Lineage, data quality checks, alerting\n"
            "5. COST — Compute, storage, egress at projected volumes\n"
            "6. RECOVERY — Backfill strategy, point-in-time replay\n\n"
            "Name specific tools (Spark, Flink, dbt, Airflow, etc.) and explain "
            "why they fit or don't. No generic advice."
        ),
    },
]


def get_template_list() -> List[Dict[str, str]]:
    """Return all templates (id, name, description only — no prompt text)."""
    return [
        {"id": t["id"], "name": t["name"], "description": t["description"]}
        for t in TEMPLATES
    ]


def get_template_prompt(template_id: str) -> Optional[str]:
    """Resolve a template ID to its full prompt text."""
    for t in TEMPLATES:
        if t["id"] == template_id:
            prompt = t["prompt"]
            # Lazy-load from .md file if needed
            if prompt.startswith("LAZY_LOAD:"):
                filename = prompt.split(":", 1)[1]
                prompt = _load_md(filename)
                t["prompt"] = prompt  # Cache it
            return prompt
    return None
