"""Overnight runner: wait for scraper, re-filter, submit batch.

Usage: python run_overnight.py
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

DATA_DIR = Path("data")


def wait_for_scraper():
    """Wait for scrape_github.py to finish."""
    print("Checking if GitHub scraper is still running...")
    while True:
        result = subprocess.run(
            ["pgrep", "-f", "scrape_github.py"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print("  Scraper finished (or not running).")
            return
        print(f"  Scraper still running at {time.strftime('%H:%M:%S')}. "
              f"Checking again in 60s...")
        time.sleep(60)


def run_filter():
    """Run filter_comments.py."""
    print("\nRunning filter_comments.py...")
    result = subprocess.run([sys.executable, "filter_comments.py"],
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)


def submit_batch():
    """Run classify_batch.py to submit the batch."""
    print("\nSubmitting batch job...")
    result = subprocess.run([sys.executable, "classify_batch.py"],
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)


def poll_batch():
    """Poll all batch jobs until complete."""
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    batch_job = DATA_DIR / "batch_job.json"
    with open(batch_job) as f:
        meta = json.load(f)

    batches = meta.get("batches", [])
    if not batches and "batch_id" in meta:
        batches = [{"batch_id": meta["batch_id"]}]

    print(f"\nPolling {len(batches)} batch(es)...")

    while True:
        all_done = True
        any_failed = False
        for i, b in enumerate(batches):
            batch = client.batches.retrieve(b["batch_id"])
            status = batch.status

            progress = ""
            if hasattr(batch, 'request_counts') and batch.request_counts:
                rc = batch.request_counts
                progress = f" ({rc.completed}/{rc.total} done, {rc.failed} failed)"

            print(f"  [{time.strftime('%H:%M:%S')}] Batch {i+1}: {status}{progress}")

            if status in ("failed", "expired", "cancelled"):
                any_failed = True
                if hasattr(batch, 'errors'):
                    print(f"    Errors: {batch.errors}")
            elif status != "completed":
                all_done = False

        if all_done:
            print("\nAll batches completed!")
            return True
        if any_failed:
            print("\nSome batches failed!")
            return False

        time.sleep(120)  # check every 2 minutes


def collect():
    """Run collect_results.py."""
    print("\nCollecting results...")
    result = subprocess.run([sys.executable, "collect_results.py", "--collect"],
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")


def main():
    print(f"=== Overnight runner started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    wait_for_scraper()
    run_filter()
    submit_batch()

    if poll_batch():
        collect()

    print(f"\n=== Done at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")


if __name__ == "__main__":
    main()
