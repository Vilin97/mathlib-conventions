"""Three-model dedup pipeline: GPT-5.4 + Gemini + Claude sub-agent → GPT-5.4 merge.

For each category:
1. Send all raw rules to GPT-5.4, Gemini 3.1 Pro (in parallel)
2. Claude handled separately via sub-agent (must be launched externally)
3. Merge all three with GPT-5.4

Usage:
  python dedup_final.py                # run GPT + Gemini for all categories
  python dedup_final.py --merge-only   # just do the final merge (assumes all 3 done)
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv()

DATA = Path("data")
MODEL_GPT = "gpt-5.4"
MODEL_GEMINI = "gemini-3.1-pro-preview"

DEDUP_PROMPT = """You are an expert in Lean 4 / Mathlib conventions. You are given raw conventions about {category} extracted from PR review comments by mathlib maintainers and prominent contributors. Many are duplicates or near-duplicates expressing the same underlying rule in different words.

Your task: Deduplicate AGGRESSIVELY into the MINIMAL set of truly distinct, non-overlapping conventions.

Rules for merging:
- Two rules are duplicates if they express the same principle, even if about different specific APIs
- Special cases should be merged into the general rule
- Remove rules that are too vague to be actionable by an AI code reviewer
- Remove rules that are about specific mathematical content rather than general conventions

For each distinct convention, write:
## [N]. [short title]
[Clear, concise, imperative rule. 1-3 sentences. Include Lean code examples where helpful.]

Target: 40-100 truly distinct conventions. Every rule should be something an AI reviewing a Mathlib PR could concretely check for."""

MERGE_PROMPT = """You are an expert in Lean 4 / Mathlib conventions. You are given THREE independently-produced deduplicated lists of {category} conventions (from GPT-5.4, Gemini 3.1 Pro, and Claude Opus). Each list was derived from the same raw conventions.

Your task: produce the FINAL, canonical list by merging all three.

Rules:
1. If a convention appears in 2 or 3 lists, it's high-confidence — keep it
2. If it appears in only 1 list, include it only if it's genuinely distinct and actionable
3. Merge overlapping conventions across lists into a single clear rule
4. The final rule wording should be the best/clearest version from any of the three lists
5. Remove anything too vague or not actionable for an AI PR reviewer

Output format:
## [N]. [short title]
[Clear imperative rule. 1-3 sentences. Include Lean examples where helpful.]
Confidence: [high/medium/low] — high if in 2-3 lists, medium if in 1 list but clearly valid

This is the FINAL list that will be used by an AI agent to review Mathlib PRs."""


def get_categories():
    """Get categories with enough rules to process."""
    cats = {}
    with open(DATA / "conventions.csv", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cat = r["category"]
            cats.setdefault(cat, []).append(r["rule"])
    return {c: rules for c, rules in cats.items() if len(rules) >= 10}


def prepare_rules(cat, rules):
    """Write rules file and return the text."""
    path = DATA / f"rules_{cat}_full.txt"
    with open(path, "w") as f:
        for i, r in enumerate(rules, 1):
            f.write(f"{i}. {r}\n")
    with open(path) as f:
        return f.read()


def run_gpt(client, cat, rules_text):
    """Run GPT-5.4 dedup."""
    out = DATA / f"dedup_{cat}_gpt54.txt"
    if out.exists() and out.stat().st_size > 100:
        print(f"    GPT-5.4: already done, skipping")
        return

    prompt = DEDUP_PROMPT.format(category=cat)
    resp = client.chat.completions.create(
        model=MODEL_GPT,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": rules_text},
        ],
        max_completion_tokens=32000,
        temperature=0.1,
    )
    result = resp.choices[0].message.content or ""
    with open(out, "w") as f:
        f.write(result)
    n = result.count("## ")
    cost = resp.usage.prompt_tokens * 2.50 / 1e6 + resp.usage.completion_tokens * 10.0 / 1e6
    print(f"    GPT-5.4: {n} conventions (${cost:.2f})")


def run_gemini(client, cat, rules_text):
    """Run Gemini 3.1 Pro dedup."""
    out = DATA / f"dedup_{cat}_gemini.txt"
    if out.exists() and out.stat().st_size > 100:
        print(f"    Gemini: already done, skipping")
        return

    prompt = DEDUP_PROMPT.format(category=cat)
    resp = client.models.generate_content(
        model=MODEL_GEMINI,
        contents=f"{prompt}\n\nHere are the raw conventions:\n\n{rules_text}",
        config=genai.types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=32000,
        ),
    )
    result = resp.text or ""
    with open(out, "w") as f:
        f.write(result)
    n = result.count("## ")
    print(f"    Gemini:  {n} conventions")


def run_merge(gpt_client, cat):
    """Merge all three lists with GPT-5.4."""
    out = DATA / f"dedup_{cat}_FINAL.txt"

    gpt_path = DATA / f"dedup_{cat}_gpt54.txt"
    gem_path = DATA / f"dedup_{cat}_gemini.txt"
    claude_path = DATA / f"dedup_{cat}_claude.txt"

    missing = []
    for name, path in [("GPT-5.4", gpt_path), ("Gemini", gem_path), ("Claude", claude_path)]:
        if not path.exists() or path.stat().st_size < 100:
            missing.append(name)

    if missing:
        print(f"    Merge: waiting on {', '.join(missing)}")
        return False

    with open(gpt_path) as f:
        gpt = f.read()
    with open(gem_path) as f:
        gemini = f.read()
    with open(claude_path) as f:
        claude = f.read()

    n_gpt = gpt.count("## ")
    n_gem = gemini.count("## ")
    n_claude = claude.count("## ")

    combined = f"""=== LIST A (from GPT-5.4): {n_gpt} conventions ===

{gpt}

=== LIST B (from Gemini 3.1 Pro): {n_gem} conventions ===

{gemini}

=== LIST C (from Claude Opus): {n_claude} conventions ===

{claude}"""

    prompt = MERGE_PROMPT.format(category=cat)
    resp = gpt_client.chat.completions.create(
        model=MODEL_GPT,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": combined},
        ],
        max_completion_tokens=32000,
        temperature=0.1,
    )
    result = resp.choices[0].message.content or ""
    with open(out, "w") as f:
        f.write(result)
    n = result.count("## ")
    cost = resp.usage.prompt_tokens * 2.50 / 1e6 + resp.usage.completion_tokens * 10.0 / 1e6
    print(f"    FINAL: {n} conventions (${cost:.2f})")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--merge-only", action="store_true")
    args = parser.parse_args()

    gpt_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    gem_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    categories = get_categories()
    print(f"Categories: {len(categories)}\n")

    if not args.merge_only:
        for cat, rules in sorted(categories.items(), key=lambda x: -len(x[1])):
            print(f"{cat} ({len(rules)} rules):")
            rules_text = prepare_rules(cat, rules)
            run_gpt(gpt_client, cat, rules_text)
            run_gemini(gem_client, cat, rules_text)
            print()

    print("\n=== FINAL MERGE ===\n")
    total = 0
    for cat in sorted(categories.keys()):
        print(f"{cat}:")
        if run_merge(gpt_client, cat):
            with open(DATA / f"dedup_{cat}_FINAL.txt") as f:
                n = f.read().count("## ")
            total += n
    print(f"\nGRAND TOTAL: {total} conventions")


if __name__ == "__main__":
    main()
