"""Collect and process results from the OpenAI Batch API.

Supports multiple batches (when input exceeds 50k request limit).

Usage:
  python collect_results.py --status    # check batch status
  python collect_results.py --collect   # download and process results
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DATA_DIR = Path("data")
BATCH_JOB = DATA_DIR / "batch_job.json"
RAW_OUTPUT = DATA_DIR / "batch_output_raw.jsonl"
CONVENTIONS_CSV = DATA_DIR / "conventions.csv"


def get_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def load_meta():
    with open(BATCH_JOB) as f:
        meta = json.load(f)
    # Normalize old single-batch format to new multi-batch format
    if "batch_id" in meta and "batches" not in meta:
        meta["batches"] = [{
            "batch_id": meta["batch_id"],
            "file_id": meta.get("file_id", ""),
            "count": meta.get("count", 0),
        }]
    return meta


def check_status():
    """Check the status of all batch jobs."""
    meta = load_meta()
    client = get_client()

    print(f"Created:     {meta['created_at']}")
    print(f"Total:       {meta.get('total_count', 'N/A')} requests\n")

    all_done = True
    for i, b in enumerate(meta["batches"]):
        batch = client.batches.retrieve(b["batch_id"])
        progress = ""
        if hasattr(batch, 'request_counts') and batch.request_counts:
            rc = batch.request_counts
            progress = f" ({rc.completed}/{rc.total} done, {rc.failed} failed)"

        print(f"Batch {i+1}/{len(meta['batches'])}: {batch.id}")
        print(f"  Status: {batch.status}{progress}")

        if batch.status not in ("completed",):
            all_done = False
        if batch.status == "failed" and hasattr(batch, 'errors'):
            print(f"  Errors: {batch.errors}")

    if all_done:
        print("\nAll batches completed! Run: python collect_results.py --collect")
    return all_done


def all_batches_done():
    """Check if all batches are completed."""
    meta = load_meta()
    client = get_client()
    for b in meta["batches"]:
        batch = client.batches.retrieve(b["batch_id"])
        if batch.status != "completed":
            return False
    return True


def collect():
    """Download results from all batches and parse into conventions CSV."""
    meta = load_meta()
    client = get_client()

    # Download all outputs
    print("Downloading batch outputs...")
    with open(RAW_OUTPUT, "w") as out:
        for i, b in enumerate(meta["batches"]):
            batch = client.batches.retrieve(b["batch_id"])
            if batch.status != "completed":
                print(f"  Batch {i+1} not done (status: {batch.status}), skipping")
                continue
            print(f"  Batch {i+1}: downloading {batch.output_file_id}...")
            content = client.files.content(batch.output_file_id)
            for chunk in content.iter_bytes():
                out.write(chunk.decode("utf-8", errors="replace"))
    print(f"  Saved to {RAW_OUTPUT}")

    # Load input records for metadata
    input_records = {}
    input_path = DATA_DIR / "filtered_for_classification.jsonl"
    if input_path.exists():
        with open(input_path) as f:
            for line in f:
                rec = json.loads(line)
                input_records[rec["id"]] = rec

    # Parse and extract conventions
    conventions = []
    errors = 0
    no_convention = 0
    with_convention = 0

    with open(RAW_OUTPUT) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            result = json.loads(line)
            custom_id = result["custom_id"]
            resp = result.get("response", {})

            if resp.get("status_code") != 200:
                errors += 1
                continue

            body = resp.get("body", {})
            choices = body.get("choices", [])
            if not choices:
                errors += 1
                continue

            text = choices[0].get("message", {}).get("content", "").strip()
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                errors += 1
                continue

            if not parsed.get("has_convention") or not parsed.get("conventions"):
                no_convention += 1
                continue

            with_convention += 1
            input_rec = input_records.get(custom_id, {})

            for conv in parsed["conventions"]:
                conventions.append({
                    "id": custom_id,
                    "source": input_rec.get("source", ""),
                    "author": input_rec.get("author", ""),
                    "pr_number": input_rec.get("pr_number", ""),
                    "category": conv.get("category", ""),
                    "rule": conv.get("rule", ""),
                    "source_quote": conv.get("source_quote", ""),
                    "url": input_rec.get("url", ""),
                })

    print(f"\nResults:")
    print(f"  With convention:  {with_convention}")
    print(f"  No convention:    {no_convention}")
    print(f"  Errors:           {errors}")
    print(f"  Total conventions extracted: {len(conventions)}")

    # Write CSV
    if conventions:
        fieldnames = ["id", "source", "author", "pr_number", "category",
                      "rule", "source_quote", "url"]
        with open(CONVENTIONS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(conventions)
        print(f"  Written to: {CONVENTIONS_CSV}")

        # Category breakdown
        cats = {}
        for c in conventions:
            cats[c["category"]] = cats.get(c["category"], 0) + 1
        print(f"\n  Category breakdown:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"    {cat:25s} {count:>5}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="Check batch status")
    parser.add_argument("--collect", action="store_true", help="Download and process results")
    args = parser.parse_args()

    if not BATCH_JOB.exists():
        print(f"No batch job found. Run classify_batch.py first.")
        sys.exit(1)

    if args.status:
        check_status()
    elif args.collect:
        collect()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
