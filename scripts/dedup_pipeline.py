"""Two-stage deduplication pipeline.

Stage 1: Use GPT-5.4-nano to reduce each chunk of ~500 rules to ~50-80 distinct rules.
Stage 2: Merge all chunk results per category into a final deduplicated list.

Usage:
  python dedup_pipeline.py                  # run full pipeline
  python dedup_pipeline.py --stage1-only    # just run stage 1
  python dedup_pipeline.py --stage2-only    # just run stage 2 (assumes stage 1 done)
"""

import argparse
import glob
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DATA = Path("data")
MODEL = "gpt-5.4-nano"

STAGE1_PROMPT = """You are an expert in Lean 4 / Mathlib conventions. You are given a batch of raw conventions about {category} extracted from PR review comments. Many are duplicates or near-duplicates.

Deduplicate aggressively: merge rules that express the same underlying principle, even if worded differently. Special cases should be merged into the general rule.

For each distinct convention, output:
## [short title]
[Clear, concise, imperative rule. 1-3 sentences. Include Lean code examples where helpful.]
Frequency: ~[N] (how many of the input rules express this)

Target: reduce to the MINIMAL set of truly distinct conventions. Quality over quantity."""

STAGE2_PROMPT = """You are an expert in Lean 4 / Mathlib conventions. You are given deduplicated conventions about {category} from multiple chunks. There is still redundancy across chunks.

Do a FINAL aggressive merge:
1. Merge any conventions that express the same underlying principle
2. Remove any that are too vague or not actionable for an AI PR reviewer
3. Keep conventions that are specific enough to check in code

Output format:
## [N]. [short title]
[Clear imperative rule. 1-3 sentences. Include Lean examples where helpful.]
Confidence: [high/medium/low] based on how many independent sources support this

Target: the MINIMAL complete set. Every rule should be something an AI reviewing a Mathlib PR could concretely check for."""


def get_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_categories():
    """Find all category chunk files."""
    cats = {}
    for path in sorted(DATA.glob("rules_*_chunk*.txt")):
        cat = path.stem.rsplit("_chunk", 1)[0].replace("rules_", "")
        cats.setdefault(cat, []).append(path)
    # Also include single-chunk categories
    for path in sorted(DATA.glob("rules_*.txt")):
        if "_chunk" in path.stem or "_dedup" in path.stem:
            continue
        cat = path.stem.replace("rules_", "")
        if cat not in cats:
            cats[cat] = [path]
    return cats


def stage1_chunk(client, cat, chunk_path):
    """Deduplicate a single chunk."""
    output_path = DATA / f"{chunk_path.stem}_dedup.txt"
    if output_path.exists() and output_path.stat().st_size > 100:
        print(f"    {chunk_path.name} -> already done, skipping")
        return output_path

    with open(chunk_path) as f:
        rules = f.read()

    n_rules = rules.count("\n")
    print(f"    {chunk_path.name} ({n_rules} rules)...", end=" ", flush=True)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": STAGE1_PROMPT.format(category=cat)},
            {"role": "user", "content": rules},
        ],
        max_completion_tokens=8000,
        temperature=0.1,
    )

    result = resp.choices[0].message.content or ""
    n_deduped = result.count("## ")
    print(f"-> {n_deduped} conventions")

    with open(output_path, "w") as f:
        f.write(result)

    return output_path


def stage1(client, categories):
    """Run stage 1: deduplicate each chunk."""
    print("=== STAGE 1: Chunk deduplication ===\n")
    for cat, chunks in sorted(categories.items()):
        print(f"  {cat} ({len(chunks)} chunks):")
        for chunk_path in chunks:
            stage1_chunk(client, cat, chunk_path)
        print()


def stage2_category(client, cat):
    """Merge all deduplicated chunks for a category."""
    output_path = DATA / f"deduped_{cat}.txt"
    if output_path.exists() and output_path.stat().st_size > 100:
        print(f"  {cat} -> already done, skipping")
        return output_path

    # Collect all chunk dedup results
    chunk_results = []
    for path in sorted(DATA.glob(f"rules_{cat}_chunk*_dedup.txt")):
        with open(path) as f:
            chunk_results.append(f.read())

    # Also check for single-file categories that were deduped
    single = DATA / f"rules_{cat}_dedup.txt"
    if single.exists():
        with open(single) as f:
            chunk_results.append(f.read())

    if not chunk_results:
        # Category had only one chunk, dedup it directly
        single_path = DATA / f"rules_{cat}.txt"
        if single_path.exists():
            result = stage1_chunk(client, cat, single_path)
            # Copy as final
            import shutil
            shutil.copy(result, output_path)
            return output_path
        print(f"  {cat} -> no chunk results found")
        return None

    combined = "\n\n---\n\n".join(chunk_results)
    n_conventions = sum(r.count("## ") for r in chunk_results)

    print(f"  {cat}: merging {n_conventions} conventions from {len(chunk_results)} chunks...",
          end=" ", flush=True)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": STAGE2_PROMPT.format(category=cat)},
            {"role": "user", "content": combined},
        ],
        max_completion_tokens=16000,
        temperature=0.1,
    )

    result = resp.choices[0].message.content or ""
    n_final = result.count("## ")
    print(f"-> {n_final} final conventions")

    with open(output_path, "w") as f:
        f.write(result)

    return output_path


def stage2(client, categories):
    """Run stage 2: merge chunks per category."""
    print("=== STAGE 2: Cross-chunk merge ===\n")
    totals = {}
    for cat in sorted(categories.keys()):
        path = stage2_category(client, cat)
        if path and path.exists():
            with open(path) as f:
                n = f.read().count("## ")
            totals[cat] = n

    print(f"\n=== FINAL SUMMARY ===")
    grand = 0
    for cat, n in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"  {cat:25s} {n:>4} conventions")
        grand += n
    print(f"  {'TOTAL':25s} {grand:>4} conventions")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-only", action="store_true")
    parser.add_argument("--stage2-only", action="store_true")
    args = parser.parse_args()

    client = get_client()
    categories = get_categories()

    print(f"Categories: {len(categories)}")
    for cat, chunks in sorted(categories.items()):
        print(f"  {cat}: {len(chunks)} chunk(s)")
    print()

    if not args.stage2_only:
        stage1(client, categories)

    if not args.stage1_only:
        stage2(client, categories)


if __name__ == "__main__":
    main()
