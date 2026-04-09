"""Submit filtered comments to OpenAI Batch API for convention extraction.

Reads:  data/filtered_for_classification.jsonl
Writes: data/batch_input.jsonl (the JSONL for OpenAI)
        data/batch_job.json   (batch job metadata for later retrieval)

Usage:
  python classify_batch.py              # submit full batch
  python classify_batch.py --test 20    # test with 20 comments, print results inline
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DATA_DIR = Path("data")
INPUT = DATA_DIR / "filtered_for_classification.jsonl"
BATCH_INPUT = DATA_DIR / "batch_input.jsonl"
BATCH_JOB = DATA_DIR / "batch_job.json"

MODEL = "gpt-5.4-nano"

SYSTEM_PROMPT = """\
You are an expert analyst of Lean 4 / Mathlib code review comments. Your job is to extract \
generalizable coding conventions, rules, and best practices from reviewer feedback on pull requests.

A comment contains a CONVENTION if it expresses a general rule or preference about how \
Lean/Mathlib code should be written — something that would apply to future PRs, not just the \
specific code under review.

Examples of conventions:
- "Non-terminal simp should be avoided; use simp only [...] or close the goal"
- "The naming convention is: if the statement is `Monotone foo`, the lemma should be named `foo_monotone`"
- "Parameters appearing in the conclusion should be explicit, not in square brackets"
- "Use `#find_home` to determine the correct file for a new lemma"
- "Prefer `exacts [...]` over separate `exact` calls when closing multiple goals"
- "Docstrings on definitions should describe the mathematical concept; docstrings on lemmas can describe related lemmas"

NOT conventions (skip these):
- Pure code suggestions without explanation of the underlying principle
- Status updates ("Done", "Fixed", "Will merge")
- Mathematical discussion with no coding advice
- PR-specific feedback that doesn't generalize ("This proof is wrong because X")
- Questions without an implied convention

Respond with a JSON object (no markdown fencing):
{
  "has_convention": true or false,
  "conventions": [
    {
      "rule": "The convention stated as a concise imperative rule that an AI agent could follow when reviewing or writing Lean/Mathlib code",
      "category": "one of: proof_style, naming, api_design, code_style, documentation, file_organization, typeclass_design, simp_usage, tactic_usage, existing_api, generalization, module_structure, other",
      "source_quote": "The key phrase from the comment that states or implies this convention"
    }
  ]
}

If has_convention is false, set conventions to an empty list.
A single comment may contain multiple conventions — list them all.
Write each rule as a clear imperative that an AI code reviewer could apply to new PRs.\
"""


def make_user_message(record):
    """Build the user message from a filtered record."""
    parts = [f"**Author**: {record['author']}"]

    if record.get("pr_number"):
        parts.append(f"**PR**: #{record['pr_number']}")
    if record.get("topic"):
        parts.append(f"**Zulip topic**: {record['topic']}")
    if record.get("file_path"):
        parts.append(f"**File**: {record['file_path']}")
    if record.get("diff_context"):
        parts.append(f"**Code context**:\n```\n{record['diff_context']}\n```")

    parts.append(f"**Comment**:\n{record['comment']}")
    return "\n".join(parts)


def make_batch_line(record):
    """Create one line of the batch JSONL."""
    return json.dumps({
        "custom_id": record["id"],
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": make_user_message(record)},
            ],
            "max_completion_tokens": 500,
            "temperature": 0.1,
        },
    })


def test_mode(n):
    """Run N comments synchronously and print results."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    records = []
    with open(INPUT) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            records.append(json.loads(line))

    print(f"Testing with {len(records)} comments...\n")

    for rec in records:
        print(f"{'='*70}")
        print(f"[{rec['id']}] {rec['author']} | {rec['source']}")
        print(f"Comment: {rec['comment'][:200]}...")
        print()

        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": make_user_message(rec)},
            ],
            max_completion_tokens=500,
            temperature=0.1,
        )

        text = resp.choices[0].message.content.strip()
        try:
            result = json.loads(text)
            if result.get("has_convention") and result.get("conventions"):
                for conv in result["conventions"]:
                    print(f"  CONVENTION [{conv['category']}]:")
                    print(f"    Rule: {conv['rule']}")
                    print(f"    Quote: {conv.get('source_quote', 'N/A')}")
            else:
                print(f"  (no convention)")
        except json.JSONDecodeError:
            print(f"  RAW: {text[:300]}")
        print()

    # Print token usage estimate
    print(f"\nEstimated cost for full batch:")
    total_records = sum(1 for _ in open(INPUT))
    est_input = total_records * 700 / 1_000_000
    est_output = total_records * 150 / 1_000_000
    cost = est_input * 0.10 + est_output * 0.625  # batch pricing
    print(f"  Records: {total_records}")
    print(f"  Est. input: {est_input:.1f}M tokens (${est_input * 0.10:.2f})")
    print(f"  Est. output: {est_output:.1f}M tokens (${est_output * 0.625:.2f})")
    print(f"  Est. total: ${cost:.2f}")


def submit_batch():
    """Create and submit batch job(s). Splits into chunks of 50k if needed."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    MAX_PER_BATCH = 50000

    # Build full batch JSONL
    print("Building batch input...")
    all_lines = []
    with open(INPUT) as fin:
        for line in fin:
            record = json.loads(line)
            all_lines.append(make_batch_line(record))
    print(f"  {len(all_lines)} total requests")

    # Split into chunks
    chunks = [all_lines[i:i + MAX_PER_BATCH]
              for i in range(0, len(all_lines), MAX_PER_BATCH)]
    print(f"  Splitting into {len(chunks)} batch(es)")

    batch_ids = []
    for ci, chunk in enumerate(chunks):
        chunk_path = DATA_DIR / f"batch_input_{ci}.jsonl"
        with open(chunk_path, "w") as f:
            for ln in chunk:
                f.write(ln + "\n")
        print(f"\n  Batch {ci+1}/{len(chunks)}: {len(chunk)} requests")

        # Upload
        print(f"  Uploading {chunk_path}...")
        with open(chunk_path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="batch")
        print(f"  File ID: {file_obj.id}")

        # Create batch
        print(f"  Creating batch job...")
        batch = client.batches.create(
            input_file_id=file_obj.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        print(f"  Batch ID: {batch.id}, Status: {batch.status}")
        batch_ids.append({
            "batch_id": batch.id,
            "file_id": file_obj.id,
            "count": len(chunk),
        })

    # Save metadata
    meta = {
        "batches": batch_ids,
        "total_count": len(all_lines),
        "model": MODEL,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(BATCH_JOB, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\n  Metadata saved to {BATCH_JOB}")
    print(f"\n{len(chunks)} batch(es) submitted! Check status with: python collect_results.py --status")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=int, help="Test with N comments (synchronous)")
    args = parser.parse_args()

    if not INPUT.exists():
        print(f"Error: {INPUT} not found. Run filter_comments.py first.")
        sys.exit(1)

    if args.test:
        test_mode(args.test)
    else:
        submit_batch()


if __name__ == "__main__":
    main()
