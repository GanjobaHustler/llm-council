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


# ── STARTER QUESTIONS ─────────────────────────────────────────

STARTER_QUESTIONS: List[Dict[str, str]] = [
    {
        "id":          "dunning",
        "title":       "Payment Recovery Pipeline",
        "domain":      "Payments & Billing",
        "severity":    "P1-URGENT",
        "preview":     "Our Stripe dunning flow loses 12% of subscribers with valid cards. Design a smart recovery pipeline with per-decline-type retry logic.",
        "prompt": (
            "Our Stripe subscription dunning flow is losing 12% of churned subscribers who had valid cards that temporarily declined. "
            "We retry 3 times over 7 days, then cancel. Competitors recover 60% of these.\n\n"
            "Design a smart dunning pipeline that:\n"
            "1. Classifies decline reasons (insufficient funds vs. card expired vs. fraud)\n"
            "2. Picks optimal retry timing per decline type\n"
            "3. Sends targeted win-back emails/push notifications\n"
            "4. Integrates with Stripe's Smart Retries but adds our own logic layer\n"
            "5. Tracks recovery rate per cohort in our analytics warehouse\n\n"
            "Constraints: Must work with Stripe Connect (creators are connected accounts), "
            "must not violate card network retry rules, budget < $200/mo in additional infra."
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "moderation",
        "title":       "Content Moderation at Scale",
        "domain":      "Content Delivery + Compliance",
        "severity":    "P2-NORMAL",
        "preview":     "50K media uploads/day, 15% false positive rate, need CSAM detection via PhotoDNA. Reduce human review queue by 50%.",
        "prompt": (
            "Fanvue processes ~50,000 media uploads per day (images + video). Currently, moderation is a bottleneck:\n"
            "- AI auto-mod (AWS Rekognition) catches ~70% of violations\n"
            "- Human reviewers handle the rest (8-person team, 4-hour SLA)\n"
            "- False positive rate is 15%, causing creator frustration\n"
            "- We need to add CSAM detection (PhotoDNA hash matching) as a legal requirement\n\n"
            "Design a moderation pipeline that:\n"
            "1. Reduces human review queue by 50%\n"
            "2. Brings false positive rate below 5%\n"
            "3. Maintains <2 hour SLA for content going live\n"
            "4. Integrates PhotoDNA/NCMEC reporting as a hard gate\n"
            "5. Gives creators transparency into why content was flagged\n\n"
            "Consider: multi-model ensemble (Rekognition + custom model), confidence thresholds, "
            "appeal workflow, audit trail for legal."
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "realtime_analytics",
        "title":       "Real-Time Creator Analytics",
        "domain":      "Data & Analytics + Creator Tools",
        "severity":    "P2-NORMAL",
        "preview":     "6-hour analytics lag from nightly dbt/Snowflake jobs. Creators want subscriber count and revenue within 30 seconds.",
        "prompt": (
            "Creators want real-time analytics (subscriber count, revenue, top content, engagement rate) "
            "but our current pipeline has 6-hour lag because it runs through nightly dbt jobs in Snowflake.\n\n"
            "Design a real-time analytics system that:\n"
            "1. Shows subscriber count and revenue within 30 seconds of an event\n"
            "2. Updates engagement metrics (likes, comments, tips) in near-real-time\n"
            "3. Maintains historical accuracy (eventual consistency OK for real-time, but daily rollups must be exact)\n"
            "4. Doesn't break our existing Snowflake/dbt warehouse\n"
            "5. Serves the creator dashboard API at <100ms p99\n\n"
            "Budget: <$1,500/mo additional infrastructure. Current stack: PostgreSQL (primary), Snowflake (warehouse), Redis (cache), Next.js frontend.\n\n"
            "Key question: Do we stream from Postgres CDC, or does the application emit events? Or both?"
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "strangler_fig",
        "title":       "Monolith to Service Mesh Migration",
        "domain":      "Infrastructure & DevOps + API",
        "severity":    "P2-NORMAL",
        "preview":     "Node.js monolith: 4-min deploys, DB connection contention, 18 engineers stepping on each other. Plan a strangler-fig extraction.",
        "prompt": (
            "Fanvue's Node.js monolith is hitting scaling walls:\n"
            "- 4-minute deploy times (full restart)\n"
            "- Payment code changes risk breaking content delivery\n"
            "- Single Postgres connection pool contention at peak hours\n"
            "- Team of 18 engineers stepping on each other's PRs\n\n"
            "Plan a phased migration that:\n"
            "1. Extracts Payments as the first service (highest risk, highest value)\n"
            "2. Defines the service boundary and API contract\n"
            "3. Handles the distributed transaction problem (subscription created \u2192 access granted \u2192 content unlocked)\n"
            "4. Maintains zero-downtime during migration\n"
            "5. Doesn't require rewriting the monolith \u2014 strangler fig pattern\n\n"
            "Include: service mesh choice (Istio vs. Linkerd vs. none), database per service strategy, "
            "shared auth/session handling, observability across services, and a realistic timeline for an 18-person team."
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "geo_compliance",
        "title":       "Geo-Expansion Compliance Architecture",
        "domain":      "Identity & Compliance + Payments + Infra",
        "severity":    "P1-URGENT",
        "preview":     "Expanding to EU (GDPR), Australia (eSafety), Brazil (LGPD). Design N-jurisdiction compliance architecture without N codepaths.",
        "prompt": (
            "Fanvue is expanding from UK/US to EU (GDPR), Australia (eSafety), and Brazil (LGPD). "
            "Each jurisdiction has different rules for:\n"
            "- Age verification (UK: mandatory, AU: upcoming, EU: varies by country)\n"
            "- Data residency (EU: must store PII in EU, Brazil: similar requirements)\n"
            "- Content rules (AU eSafety: specific prohibited categories, Germany: NetzDG)\n"
            "- Tax (EU VAT MOSS, Brazil: IOF + ISS, AU: GST)\n"
            "- Payout (different banking rails, FX conversion, tax withholding)\n\n"
            "Design the compliance architecture that:\n"
            "1. Detects user jurisdiction reliably (IP + billing address + ID document)\n"
            "2. Enforces per-jurisdiction content rules without duplicating business logic\n"
            "3. Routes PII storage to correct region (multi-region Postgres or separate clusters?)\n"
            "4. Handles tax calculation and reporting per jurisdiction\n"
            "5. Manages creator payouts with correct withholding per country\n\n"
            "Constraint: Must be extensible \u2014 we'll add 5 more countries in the next 12 months. "
            "Architecture should handle N jurisdictions without N codepaths."
        ),
        "template_id": "fanvue_copilot",
    },
]


def get_starter_questions() -> List[Dict[str, str]]:
    """Return all starter questions (without full prompt text)."""
    return [
        {
            "id":       q["id"],
            "title":    q["title"],
            "domain":   q["domain"],
            "severity": q["severity"],
            "preview":  q["preview"],
            "template_id": q["template_id"],
        }
        for q in STARTER_QUESTIONS
    ]


def get_starter_question_prompt(question_id: str) -> Optional[str]:
    """Return the full prompt for a starter question."""
    for q in STARTER_QUESTIONS:
        if q["id"] == question_id:
            return q["prompt"]
    return None
