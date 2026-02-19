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
        "id":          "session1_sprint1",
        "title":       "Sprint 1: Voice, Prompt & Guardrails",
        "domain":      "P9 + P5 + P7 — Foundation Layer",
        "severity":    "P0-FIRE",
        "preview":     "Lock creator Voice DNA, design the 2000-token prompt assembly template, and spec the 3-tier guardrail engine. Nothing works without these three.",
        "prompt": (
            "We are building the Fanvue Copilot — a human-in-the-loop AI fan engagement system. "
            "Sprint 1 requires solving three foundational problems in dependency order. "
            "Answer all three in full.\n\n"

            "## QUESTION 1.1 — VOICE CALIBRATION ARCHITECTURE (P9)\n\n"
            "We need to lock a creator's personality into the inference model WITHOUT fine-tuning a separate model per creator. "
            "The solution must use prompt-engineering + RAG.\n\n"
            "Specifics:\n"
            "- Base model: Sao10K/L3.3-70B-Vulpecula (70B parameter, runs on our infra)\n"
            "- Each creator has: Tone (0-10 scale), Sentence length range, Emoji density (0-5), "
            "Vocabulary level (1-5), a 'Never-Say' list (up to 50 phrases), and 10 Signature Phrases\n"
            "- These parameters are stored as a 'Voice DNA' JSON object per creator\n"
            "- The model must NEVER break character across 10,000+ messages\n\n"
            "Define:\n"
            "1. The exact Voice DNA JSON schema with all fields and validation rules\n"
            "2. How Voice DNA gets injected into the prompt (position, format, token budget)\n"
            "3. A drift detection algorithm that fires an alert when output diverges from the creator's archetype "
            "— what metric quantifies 'drift' and what is the threshold?\n"
            "4. How do we handle the tension between Voice DNA consistency and the need for the AI to adapt its "
            "phrasing to match the fan's vocabulary level (a fan who writes 'yo whats good' vs. a fan who writes "
            "'I've been thinking about you all day')?\n\n"

            "## QUESTION 1.2 — PROMPT ASSEMBLY TEMPLATE (P5)\n\n"
            "The prompt sent to Vulpecula at inference time must contain ALL of the following within a 2000-token budget:\n"
            "- Creator Voice DNA (from P9)\n"
            "- Fan profile summary (Layer 1 + 2 + 3 classification)\n"
            "- Current conversation context (last N messages)\n"
            "- RAG-retrieved book knowledge (top 3-5 chunks from relevant CAT tags)\n"
            "- Strategy instruction (what the system wants the AI to do: hook, nurture, pitch, de-escalate)\n"
            "- Output format instruction (generate 3 variants: Safe / Balanced / Aggressive-Compliant)\n"
            "- Hard constraints (never-say list, guardrail rules)\n\n"
            "Design:\n"
            "1. The exact prompt template with placeholder tokens and character/token budgets per section\n"
            "2. The priority order for what gets CUT when context is too long "
            "(what gets summarized first? what gets dropped entirely?)\n"
            "3. The compression algorithm for conversation history — at what message count do you switch from "
            "full history to summary? What summarization method?\n"
            "4. How the 3 variants (Safe/Balanced/Aggressive) are generated — 3 separate API calls? "
            "One call with multi-output instruction? What are the tradeoffs?\n\n"

            "## QUESTION 1.3 — GUARDRAIL ARCHITECTURE (P7)\n\n"
            "The guardrail system must simultaneously:\n"
            "(a) Block genuinely dangerous outputs — meetup promises, real name reveals, financial advice, underage references\n"
            "(b) NOT block aggressive-but-legal monetization — scarcity plays, jealousy triggers, explicit PPV upsells, sexual escalation\n\n"
            "Design:\n"
            "1. The exact 3-tier classification system: Hard Block (output destroyed, operator sees error) / "
            "Soft Warning (output shown with flag, operator decides) / Override Queue (output held, requires admin approval)\n"
            "2. The rule engine — is this regex-based, classifier-based, or LLM-as-judge? "
            "What are the tradeoffs of each for <100ms latency?\n"
            "3. The specific rules for each tier with examples:\n"
            "   - 5 Hard Block rules with example triggers\n"
            "   - 5 Soft Warning rules with example triggers\n"
            "   - 3 Override Queue rules with example triggers\n"
            "4. How do guardrails interact with the 3 variants? If the Aggressive variant gets blocked, "
            "does the system auto-promote the Balanced variant, or show only 2 options?\n"
            "5. False positive handling — when an operator reports a false block, "
            "how does that feedback improve the system?"
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "session2_intelligence",
        "title":       "Sprint 2: Memory, Strategy & Sentiment",
        "domain":      "P1 + P2 + P8 — Intelligence Layer",
        "severity":    "P1-URGENT",
        "preview":     "Persistent fan memory across sessions, strategy ledger tracking what works per fan, and real-time sentiment + post-nut detection.",
        "prompt": (
            "Sprint 2 — Intelligence Layer. Answer all three problems in full.\n\n"

            "## QUESTION 2.1 — LONG-TERM MEMORY ARCHITECTURE (P1)\n\n"
            "A fan mentions his dog's name is Max, he works night shifts, he's going through a divorce, "
            "and his birthday is March 15. Six weeks later, the system must recall all of this without the operator remembering.\n\n"
            "Design:\n"
            "1. The memory storage schema — what data structure holds fan facts? Key-value? Graph? Document?\n"
            "2. The extraction pipeline — when a new transcript arrives, how does the system identify "
            "'memorable facts' vs. noise? What NLP method extracts structured facts from unstructured chat?\n"
            "3. Memory compression — after 500 messages, the full history is too large. "
            "What gets compressed? What stays verbatim? What algorithm decides?\n"
            "4. Memory injection into prompt — how do remembered facts get into the P5 prompt template "
            "without blowing the token budget? What's the max token allocation for memory?\n"
            "5. Contradiction handling — fan said he's single in January, mentions a girlfriend in March. "
            "How does the system resolve conflicting facts?\n"
            "6. Memory decay — should old facts fade? 'His dog is Max' is permanent. "
            "'He had a bad day at work' is temporary. What's the decay function?\n\n"

            "## QUESTION 2.2 — PERSISTENT STRATEGY PROFILE (P2)\n\n"
            "The system must track not just WHO the fan is, but WHAT WAS TRIED and WHAT WORKED.\n\n"
            "Example: 'Week 2: tried jealousy play → he went cold for 3 days. "
            "Week 4: tried scarcity on PPV → instant unlock. "
            "Week 6: tried price anchor at $75 → no response. Dropped to $50 → immediate purchase.'\n\n"
            "Design:\n"
            "1. The strategy ledger schema — what does each entry look like? "
            "Fields: timestamp, strategy_type, tactic_name, fan_response, outcome_grade, revenue_impact?\n"
            "2. How does the system auto-detect which strategy was used? The operator sends one of 3 variants "
            "— can the system infer the strategy category from the variant chosen?\n"
            "3. How does this ledger feed into P5 (Prompt Assembly)? When assembling the next prompt, "
            "how does the system say 'do NOT use jealousy play — it failed on Day 14'?\n"
            "4. Strategy cooldown rules — after a failed tactic, how long before the system considers "
            "trying it again? Is this time-based, interaction-count-based, or signal-based?\n"
            "5. Cross-fan strategy transfer — if jealousy plays fail on 80% of Avoidant-attachment fans, "
            "should that inform the prior for NEW Avoidant fans? How?\n\n"

            "## QUESTION 2.3 — REAL-TIME SENTIMENT ANALYSIS (P8)\n\n"
            "Every incoming fan message carries emotional state data. The system must classify in real-time:\n"
            "Happy / Frustrated / Lonely / Angry / Aroused / Post-Nut (low arousal, regret risk) / Anxious / Bored\n\n"
            "The critical sub-problem: POST-NUT DETECTION. A fan who just bought and consumed a PPV is in a "
            "completely different psychological state 5 minutes later. Sending another CTA at that moment "
            "= refund risk + relationship damage.\n\n"
            "Design:\n"
            "1. The sentiment classification model — fine-tuned classifier? Zero-shot LLM? Lexicon-based? "
            "What's the accuracy/latency tradeoff?\n"
            "2. The feature set — what signals beyond text content? "
            "(timestamp, time since last purchase, message length delta, response speed change)\n"
            "3. Post-nut detection specifically — what behavioral signature identifies this state? "
            "What's the system response? (cool-down timer? switch to nurture mode? specific CAT-03 retrieval?)\n"
            "4. State transition model — fan emotional states change mid-conversation. How does the system "
            "track state transitions and detect the MOMENT of shift?\n"
            "5. How does detected sentiment modify the P5 prompt? Does it change which variant is ranked first? "
            "Does it inject a specific instruction like 'FAN IS IN POST-NUT STATE — DO NOT PITCH'?"
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "session3_profiling",
        "title":       "Sprint 3: Personality & Whale Detection",
        "domain":      "P3 + P4 — Deep Profiling",
        "severity":    "P1-URGENT",
        "preview":     "Infer OCEAN + Attachment Style from 3-5 chat messages with no survey. Classify whale potential before they spend a dollar.",
        "prompt": (
            "Sprint 3 — Deep Profiling. Two of the hardest problems in the system. Answer both in full.\n\n"

            "## QUESTION 3.1 — PERSONALITY INFERENCE ENGINE (P3) ⚠️ HARDEST\n\n"
            "We must infer Big Five OCEAN scores + Attachment Style + Love Language from text alone. "
            "No survey. The text is short, informal, sexually-charged chat messages — NOT essays or forum posts.\n\n"
            "1. MINIMUM VIABLE SIGNAL: How many messages are needed for a statistically defensible first inference "
            "of Attachment Style (Anxious/Avoidant/Secure)? What behavioral features does the model look for in "
            "those messages? (Response time, message length, emoji usage, question frequency, emotional vocabulary "
            "density, vulnerability disclosure rate?)\n\n"
            "2. NLP METHOD: What specific model or approach infers Big Five from short chat? Options:\n"
            "   (a) Fine-tuned BERT/RoBERTa on personality-labeled chat data\n"
            "   (b) Zero-shot with Vulpecula using RAG-retrieved personality markers from the book corpus\n"
            "   (c) Hybrid — lightweight classifier for initial scores, LLM refinement with RAG grounding\n"
            "   Which one? Why?\n\n"
            "3. RAG GROUNDING: How does retrieval from CAT-01 (personality/attachment books) improve inference "
            "accuracy? The system retrieves chunks from Attached, Big Five, Emotional Intelligence describing "
            "behavioral signatures — then asks Vulpecula 'given these personality markers and this chat history, "
            "what is the most likely attachment style?' Does this actually work better than a trained classifier?\n\n"
            "4. PERFORMED PERSONA: A man who types 'I don't need anyone, I'm just here for fun' may be performing "
            "Avoidant while actually being Anxious. What signal reveals the gap between performed and actual "
            "personality? How many messages before the system detects it?\n\n"
            "5. INCREMENTAL UPDATE: Does each new transcript recalculate OCEAN scores from scratch across all "
            "history, or apply an incremental Bayesian update? What's the formula? "
            "What's the confidence interval at 10 / 50 / 200 messages?\n\n"
            "6. CONFIDENCE COMMUNICATION: What does the operator see when the system has only 4 messages? "
            "A grayed-out profile? A score with a wide error bar? A 'provisional' label? "
            "What's the UX of uncertainty?\n\n"

            "## QUESTION 3.2 — WHALE DETECTION (P4)\n\n"
            "The system must classify a fan's spending potential BEFORE they spend significantly. "
            "Early misclassification wastes operator attention on time-sinks or under-serves potential whales.\n\n"
            "Design:\n"
            "1. The early behavioral signals that predict whale potential — with NO purchase history. "
            "What can be inferred from: reply speed, message length, time of day, vocabulary complexity, "
            "emotional investment, question-asking rate?\n"
            "2. The Trajectory Score (0-100) — what formula combines these signals? How does it update? "
            "What's the minimum interaction count before the score is actionable?\n"
            "3. Tier boundaries: What score ranges map to Whale / Mid-Tier / Time-Sink? Are these fixed or "
            "calibrated per creator (a 'whale' for Creator A might be mid-tier for Creator B)?\n"
            "4. How does P4 interact with P3? If personality inference says 'High Neuroticism + Low "
            "Conscientiousness + Anxious Attachment' — does that DIRECTLY predict high spend? "
            "What's the correlation strength?\n"
            "5. The false-whale problem — what do you do when early signals suggest whale but the fan turns "
            "out to be broke? How quickly does the system correct?"
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "session4_bandit",
        "title":       "Sprint 4: Bandit Convergence Engine",
        "domain":      "P6 — Thompson Sampling Optimization",
        "severity":    "P1-URGENT",
        "preview":     "Thompson Sampling with 1-3 messages/day. Global → Creator → Segment → User prior hierarchy. How do you converge in 30 days without burning a whale?",
        "prompt": (
            "Sprint 4 — Optimization Engine. The hardest engineering problem in the system.\n\n"

            "## QUESTION 4.1 — BANDIT CONVERGENCE (P6) ⚠️ HARDEST\n\n"
            "The bandit must learn which strategy works on which fan archetype. But high-value fans interact "
            "1-3 times/day. At that rate, user-level convergence could take months. A wrong strategy choice "
            "early can permanently damage the relationship.\n\n"
            "1. PRIOR HIERARCHY: Global Prior → Creator-Specific → Segment-Specific → User-Specific. "
            "How exactly are these structured as Beta distributions? What are the initial alpha/beta values "
            "at each level? How does evidence propagate UP the hierarchy "
            "(a user-level outcome updating the segment prior)?\n\n"
            "2. EXPLORATION VS. EXPLOITATION: With only 1-3 signals per day per fan, how do you prevent "
            "the bandit from exploring a catastrophic strategy on a whale? Is there a 'safety ceiling' that "
            "restricts exploration to low-risk tactics when estimated fan value exceeds threshold X?\n\n"
            "3. OUTCOME GRADING: The operator grades outcomes as:\n"
            "   🟢 $SOLD (with amount) / 🔵 REPLY / 🔴 GHOSTED / 💀 REFUND-BAD\n"
            "   How do these map to reward values? Is $SOLD($100) ten times as valuable as $SOLD($10)? "
            "How do you handle delayed rewards (fan buys 2 days after the conversation)?\n\n"
            "4. ARCHETYPE-SPECIFIC ARMS: The bandit maintains separate strategy pools per archetype combination. "
            "But with 3 attachment styles × 3 economic tiers × 4 relational stages = 36 combinations — "
            "most will have near-zero data. How do you handle this combinatorial sparsity?\n\n"
            "5. CONVERGENCE ESTIMATE: Given the data rates described, how many days until the bandit's "
            "User-Specific posterior meaningfully deviates from the Global Prior? Show the math.\n\n"
            "6. THE COLD-START BRIDGE: Before the bandit has ANY data on a new fan, what strategy does it "
            "default to? How is that default selected — safest option? Highest global win rate? Something else?"
        ),
        "template_id": "fanvue_copilot",
    },
    {
        "id":          "session5_integration",
        "title":       "Sprint 5: Full Pipeline Integration & Metrics",
        "domain":      "P1–P9 — End-to-End Trace + 40-Point Dashboard",
        "severity":    "P2-NORMAL",
        "preview":     "Trace a brand-new fan's first message through every system layer end-to-end. Then spec which 10 of the 40 metrics are buildable in Sprint 1.",
        "prompt": (
            "Sprint 5 — Integration & Metrics. Two questions.\n\n"

            "## QUESTION 5.1 — FULL PIPELINE INTEGRATION TEST\n\n"
            "Walk through a complete interaction cycle, end to end:\n\n"
            "A brand new fan (zero history) sends his first message: "
            "'hey beautiful, just subscribed, you're so hot 🔥'\n"
            "The operator pastes this into the Copilot.\n\n"
            "Trace every system action in order:\n"
            "- What does the cold-start classifier output?\n"
            "- What Qdrant queries fire? Which CAT tags? What chunks come back?\n"
            "- What does the assembled prompt to Vulpecula look like "
            "(full template with this specific input)?\n"
            "- What do the 3 generated variants look like?\n"
            "- What does the guardrail check on each variant?\n"
            "- What does the operator's dashboard show?\n"
            "- The operator picks 'Balanced' and sends it. "
            "The fan replies 10 minutes later with a longer message. What updates?\n"
            "- After 8 exchanges, the fan unlocks a $15 PPV. "
            "The operator logs 🟢 $SOLD $15. What updates?\n\n"
            "Show actual data structures, actual Qdrant queries, actual prompt text — not descriptions.\n\n"

            "## QUESTION 5.2 — METRICS IMPLEMENTATION\n\n"
            "Of the 40 metrics in the God View dashboard, which 10 are implementable in Sprint 1 "
            "(with only P5 + P7 + P9 solved)?\n\n"
            "For each of those 10:\n"
            "1. Exact calculation formula\n"
            "2. Data source (what system component generates the input)\n"
            "3. Update frequency (real-time? daily? per-session?)\n"
            "4. Alert threshold (what value triggers a flag to the operator?)\n\n"
            "The 40 metrics for reference:\n"
            "REVENUE (1-5): LTV, Conversion Rate, Unlock Rate, AOV, Velocity ($/7d)\n"
            "RETENTION (6-9): Attachment Score, Churn Risk, Response Rate, Session Length\n"
            "CONNECTION (10-20): Intimacy Depth, Sexual Tension Index, Exclusivity Perception, "
            "Fantasy Reinforcement, Reciprocity, Jealousy Sensitivity, GFE Immersion, Persona Lock-In, "
            "TOFU Heat, Content Recall, 'Missing You' Frequency\n"
            "OPERATIONAL (21-24): Bandit Learning Speed, Strategy Win Rate, Chatter Throughput, Guardrail Block Rate\n"
            "INTELLIGENCE (25-28): Archetype Accuracy, NBA Precision, Probe Response Rate, Content Match\n"
            "PSYCHOMETRICS (29-31): OCEAN Profile, Attachment Style, Love Language\n"
            "MICRO-ECONOMICS (32-34): Price Elasticity, Impulse Ratio, Wallet Share\n"
            "BEHAVIORAL BIOMETRICS (35-37): Horny Clock, Post-Nut Drop-off, Device Fingerprint\n"
            "RISK (38-40): Refund Risk Score, Policy Violation Rate, Operator Override Rate"
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
