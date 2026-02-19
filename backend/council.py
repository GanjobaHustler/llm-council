"""3-stage LLM Council orchestration with alias mapping and token cap enforcement."""

import asyncio
from typing import List, Dict, Any, Tuple

from .openrouter import query_models_parallel, query_model, health_check_model
from .config import COUNCIL_MODELS, CHAIRMAN, TOKEN_CAPS


#  Helpers 

def _slugs() -> List[str]:
    return [m["slug"] for m in COUNCIL_MODELS]


def _alias(slug: str) -> str:
    """Return the human alias for a model slug, or the slug itself as fallback."""
    for m in COUNCIL_MODELS:
        if m["slug"] == slug:
            return m["alias"]
    if slug == CHAIRMAN["slug"]:
        return CHAIRMAN["alias"]
    return slug


def _phase1_caps() -> Dict[str, int]:
    return {m["slug"]: m["max_tokens_phase1"] for m in COUNCIL_MODELS}


def _phase2_caps() -> Dict[str, int]:
    return {m["slug"]: m["max_tokens_phase2"] for m in COUNCIL_MODELS}


#  Bootstrap 

async def bootstrap_council() -> Dict[str, bool]:
    """
    Health-check every council member + chairman in parallel,
    then print the council manifest to stdout.
    Returns dict mapping slug -> online (bool).
    """
    all_models = COUNCIL_MODELS + [CHAIRMAN]
    tasks = [health_check_model(m["slug"]) for m in all_models]
    results = await asyncio.gather(*tasks)

    status: Dict[str, bool] = {}
    for model, online in zip(all_models, results):
        status[model["slug"]] = online
        icon = "" if online else ""
        note = "ONLINE" if online else "UNREACHABLE  skipped"
        print(f'  {icon} {model["alias"]}  {model["slug"]} ({note})')

    print("  A-Team Council is live. Awaiting first query.")
    return status


#  Stage 1 

async def stage1_collect_responses(user_query: str, system_prompt: str = "") -> List[Dict[str, Any]]:
    """
    Phase 1: Send user prompt to all COUNCIL_MODELS in parallel.
    Token cap: max_tokens_phase1 per model.
    If system_prompt is provided, it is prepended as a system message.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_query})
    caps = _phase1_caps()
    responses = await query_models_parallel(_slugs(), messages, max_tokens_per_model=caps)

    results = []
    for slug, response in responses.items():
        if response is not None:
            results.append({
                "model":    _alias(slug),
                "slug":     slug,
                "response": response.get("content", ""),
            })
    return results


#  Stage 2 

async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Phase 2: Each council member ranks the anonymised Phase-1 responses.
    Token cap: max_tokens_phase2 per model.
    """
    labels = [chr(65 + i) for i in range(len(stage1_results))]

    label_to_model = {
        f"Response {label}": result["model"]
        for label, result in zip(labels, stage1_results)
    }

    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. Evaluate each response individually  what it does well and what it misses.
2. At the very end, provide a FINAL RANKING.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- List responses from best to worst as a numbered list
- Each line: number, period, space, then ONLY the label (e.g. "1. Response A")

FINAL RANKING:
1. Response A
2. Response B

Now provide your evaluation and ranking:"""

    messages = [{"role": "user", "content": ranking_prompt}]
    caps = _phase2_caps()
    responses = await query_models_parallel(_slugs(), messages, max_tokens_per_model=caps)

    results = []
    for slug, response in responses.items():
        if response is not None:
            full_text = response.get("content", "")
            results.append({
                "model":          _alias(slug),
                "slug":           slug,
                "ranking":        full_text,
                "parsed_ranking": parse_ranking_from_text(full_text),
            })

    return results, label_to_model


#  Stage 3 

async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    system_prompt: str = "",
) -> Dict[str, Any]:
    """Phase 3: CHAIRMAN synthesises the final answer."""
    stage1_text = "\n\n".join([
        f"{r['model']}:\n{r['response']}" for r in stage1_results
    ])
    stage2_text = "\n\n".join([
        f"{r['model']} ranking:\n{r['ranking']}" for r in stage2_results
    ])

    chairman_prompt = f"""You are {CHAIRMAN['alias']}, Chairman of the LLM Council. Multiple AI models have responded to a user question, then ranked each other.

Original Question: {user_query}

PHASE 1  Individual Responses:
{stage1_text}

PHASE 2  Peer Rankings:
{stage2_text}

Synthesise all of this into a single, comprehensive, accurate final answer. Consider the individual responses, peer rankings, and patterns of agreement. Deliver the council verdict:"""

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": chairman_prompt})
    response = await query_model(CHAIRMAN["slug"], messages, max_tokens=CHAIRMAN["max_tokens"])

    if response is None:
        return {
            "model":    CHAIRMAN["alias"],
            "slug":     CHAIRMAN["slug"],
            "response": "Error: Chairman was unable to generate a synthesis.",
        }

    return {
        "model":    CHAIRMAN["alias"],
        "slug":     CHAIRMAN["slug"],
        "response": response.get("content", ""),
    }


#  Ranking helpers 

def parse_ranking_from_text(ranking_text: str) -> List[str]:
    import re
    if "FINAL RANKING:" in ranking_text:
        section = ranking_text.split("FINAL RANKING:", 1)[1]
        numbered = re.findall(r'\d+\.\s*Response [A-Z]', section)
        if numbered:
            return [re.search(r'Response [A-Z]', m).group() for m in numbered]
        return re.findall(r'Response [A-Z]', section)
    return re.findall(r'Response [A-Z]', ranking_text)


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str],
) -> List[Dict[str, Any]]:
    from collections import defaultdict
    model_positions: Dict[str, List[int]] = defaultdict(list)

    for ranking in stage2_results:
        for position, label in enumerate(parse_ranking_from_text(ranking["ranking"]), start=1):
            if label in label_to_model:
                model_positions[label_to_model[label]].append(position)

    aggregate = [
        {
            "model":          model,
            "average_rank":   round(sum(pos) / len(pos), 2),
            "rankings_count": len(pos),
        }
        for model, pos in model_positions.items() if pos
    ]
    aggregate.sort(key=lambda x: x["average_rank"])
    return aggregate


#  Title generation 

async def generate_conversation_title(user_query: str) -> str:
    prompt = (
        "Generate a very short title (3-5 words max) summarising the question. "
        "No quotes or punctuation.\n\n"
        f"Question: {user_query}\n\nTitle:"
    )
    slug = COUNCIL_MODELS[0]["slug"]
    response = await query_model(slug, [{"role": "user", "content": prompt}], timeout=30.0, max_tokens=20)
    if response is None:
        return "New Conversation"
    title = response.get("content", "New Conversation").strip().strip("\"'")
    return title[:47] + "..." if len(title) > 50 else title


#  Full pipeline 

async def run_full_council(user_query: str, system_prompt: str = "") -> Tuple[List, List, Dict, Dict]:
    stage1_results = await stage1_collect_responses(user_query, system_prompt=system_prompt)

    if not stage1_results:
        return [], [], {
            "model":    CHAIRMAN["alias"],
            "response": "All council members failed to respond. Please try again.",
        }, {}

    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)
    stage3_result = await stage3_synthesize_final(user_query, stage1_results, stage2_results, system_prompt=system_prompt)

    return stage1_results, stage2_results, stage3_result, {
        "label_to_model":     label_to_model,
        "aggregate_rankings": aggregate_rankings,
    }
