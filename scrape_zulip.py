"""Scrape all messages from the Zulip #PR-reviews channel.

Uses the Zulip API GET /messages endpoint with narrow to the PR-reviews stream.
Messages are fetched in batches of 1000 (max allowed), oldest first.
Results are saved to CSV incrementally.
"""

import csv
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ZULIP_SITE = os.environ["ZULIP_SITE"]
ZULIP_EMAIL = os.environ["ZULIP_EMAIL"]
ZULIP_API_KEY = os.environ["ZULIP_API_KEY"]
AUTH = (ZULIP_EMAIL, ZULIP_API_KEY)

STREAM_NAME = "PR reviews"
STREAM_ID = 144837

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "zulip_pr_reviews.csv"

FIELDS = [
    "id", "sender_id", "sender_full_name", "sender_email",
    "timestamp", "topic", "content", "url",
]

BATCH_SIZE = 1000  # Zulip max


def zulip_get(endpoint, params=None):
    """Make a GET request to the Zulip API."""
    url = f"{ZULIP_SITE}/api/v1/{endpoint}"
    while True:
        resp = requests.get(url, auth=AUTH, params=params)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            print(f"  Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        result = resp.json()
        if result.get("result") != "success":
            print(f"  API error: {result.get('msg', result)}")
            sys.exit(1)
        return result


def get_existing_ids():
    """Load existing message IDs from CSV to support resumption."""
    existing = set()
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
        with open(CSV_PATH, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(int(row["id"]))
    return existing


def main():
    print(f"Zulip site: {ZULIP_SITE}")
    print(f"Stream: {STREAM_NAME} (id={STREAM_ID})")

    existing_ids = get_existing_ids()
    max_existing_id = max(existing_ids) if existing_ids else 0
    print(f"Existing messages: {len(existing_ids)} (max id: {max_existing_id})")

    # Start from after the last message we have
    anchor = max_existing_id if max_existing_id > 0 else "oldest"

    write_header = not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0
    outfile = open(CSV_PATH, "a", newline="")
    writer = csv.DictWriter(outfile, fieldnames=FIELDS)
    if write_header:
        writer.writeheader()

    total_new = 0
    batch_num = 0

    narrow = [
        {"operator": "channel", "operand": STREAM_NAME},
    ]

    print("Scraping messages...")
    while True:
        params = {
            "narrow": str(narrow).replace("'", '"'),
            "anchor": anchor,
            "num_before": 0,
            "num_after": BATCH_SIZE,
        }

        result = zulip_get("messages", params)
        messages = result.get("messages", [])

        if not messages:
            print(f"  Batch {batch_num}: no messages — done.")
            break

        new_count = 0
        for msg in messages:
            if msg["id"] in existing_ids:
                continue
            if msg["id"] == anchor:
                continue  # skip the anchor message itself on resumption

            row = {
                "id": msg["id"],
                "sender_id": msg["sender_id"],
                "sender_full_name": msg["sender_full_name"],
                "sender_email": msg.get("sender_email", ""),
                "timestamp": msg["timestamp"],
                "topic": msg.get("subject", msg.get("topic", "")),
                "content": msg["content"],
                "url": f"{ZULIP_SITE}/#narrow/channel/{STREAM_ID}-PR-reviews/topic/{msg.get('subject', '')}/near/{msg['id']}",
            }
            writer.writerow(row)
            new_count += 1
            total_new += 1

        outfile.flush()
        batch_num += 1

        last_id = messages[-1]["id"]
        print(f"  Batch {batch_num}: {new_count} new / {len(messages)} fetched. "
              f"Last id: {last_id}")

        # If we got fewer than requested, we've reached the end
        if len(messages) < BATCH_SIZE:
            print("  Reached end of stream.")
            break

        # Move anchor to last message for next batch
        anchor = last_id

        # Small delay to be polite
        time.sleep(0.5)

    outfile.close()
    print(f"\nTotal new messages: {total_new}")
    print(f"Saved to: {CSV_PATH}")


if __name__ == "__main__":
    main()
