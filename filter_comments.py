"""Filter comments to target members and remove obvious noise.

Reads from:
  - data/github_issue_comments.csv
  - data/github_review_comments.csv
  - data/zulip_pr_reviews.csv

Writes to:
  - data/filtered_for_classification.jsonl

Each output line is a JSON object ready for the classification prompt.
"""

import csv
import json
import re
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

from members import ALL_GITHUB_USERNAMES, ZULIP_USER_IDS

DATA_DIR = Path("data")
OUTPUT = DATA_DIR / "filtered_for_classification.jsonl"

# Short responses that contain no convention
TRIVIAL_PATTERNS = {
    "done", "done.", "fixed", "fixed.", "thanks", "thanks!", "thank you",
    "lgtm", "lgtm!", "ok", "ok.", "sure", "sure.", "agreed", "agreed.",
    "yes", "no", "right", "right.", "correct", "will do", "will fix",
    "pushed", "updated", "rebased", "addressed", "resolved",
}


def is_trivial(text):
    """Check if a comment is too short/trivial to contain a convention."""
    stripped = text.strip().lower().rstrip(".")
    if stripped in TRIVIAL_PATTERNS:
        return True
    if len(text.strip()) < 25:
        return True
    return False


def is_bare_suggestion(text):
    """Check if comment is ONLY a code suggestion block with no explanation."""
    stripped = text.strip()
    # Remove all ```suggestion...``` blocks
    without_suggestions = re.sub(
        r'```suggestion\s*\n.*?```', '', stripped, flags=re.DOTALL
    ).strip()
    # If nothing meaningful remains, it's a bare suggestion
    return len(without_suggestions) < 20 and '```suggestion' in stripped


def is_bot_like(text):
    """Check for bot-generated content."""
    lower = text.lower()
    return any(p in lower for p in [
        "### pr summary",
        "bors r+",
        "bors merge",
        "merge conflict",
        "please rebase",
        "ci status:",
    ])


def strip_html(text):
    """Rough HTML tag stripping for Zulip content."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&quot;', '"')
    return text.strip()


def process_github_review_comments():
    """Process inline review comments (richest source)."""
    path = DATA_DIR / "github_review_comments.csv"
    if not path.exists():
        print(f"  {path} not found, skipping")
        return []

    records = []
    with open(path, "r") as f:
        for row in csv.DictReader(f):
            if row["author"] not in ALL_GITHUB_USERNAMES:
                continue
            body = row["body"].strip()
            if is_trivial(body) or is_bare_suggestion(body) or is_bot_like(body):
                continue
            records.append({
                "id": f"gh_review_{row['id']}",
                "source": "github_review",
                "author": row["author"],
                "pr_number": row["pr_number"],
                "file_path": row.get("path", ""),
                "diff_context": (row.get("diff_hunk", "") or "")[:500],
                "comment": body[:2000],  # cap length for API
                "url": row.get("html_url", ""),
            })
    return records


def process_github_issue_comments():
    """Process PR conversation comments."""
    path = DATA_DIR / "github_issue_comments.csv"
    if not path.exists():
        print(f"  {path} not found, skipping")
        return []

    records = []
    with open(path, "r") as f:
        for row in csv.DictReader(f):
            if row["author"] not in ALL_GITHUB_USERNAMES:
                continue
            body = row["body"].strip()
            if is_trivial(body) or is_bot_like(body):
                continue
            records.append({
                "id": f"gh_issue_{row['id']}",
                "source": "github_issue",
                "author": row["author"],
                "pr_number": row["pr_number"],
                "diff_context": "",
                "file_path": "",
                "comment": body[:2000],
                "url": row.get("html_url", ""),
            })
    return records


def process_zulip():
    """Process Zulip PR-reviews messages."""
    path = DATA_DIR / "zulip_pr_reviews.csv"
    if not path.exists():
        print(f"  {path} not found, skipping")
        return []

    records = []
    with open(path, "r") as f:
        for row in csv.DictReader(f):
            if int(row["sender_id"]) not in ZULIP_USER_IDS:
                continue
            text = strip_html(row["content"].strip())
            if is_trivial(text) or is_bot_like(text):
                continue
            records.append({
                "id": f"zulip_{row['id']}",
                "source": "zulip",
                "author": row["sender_full_name"],
                "pr_number": "",
                "file_path": "",
                "diff_context": "",
                "comment": text[:2000],
                "topic": row.get("topic", ""),
                "url": row.get("url", ""),
            })
    return records


def main():
    print("Filtering comments...")

    review = process_github_review_comments()
    print(f"  GitHub review comments: {len(review)}")

    issue = process_github_issue_comments()
    print(f"  GitHub issue comments:  {len(issue)}")

    zulip = process_zulip()
    print(f"  Zulip messages:         {len(zulip)}")

    all_records = review + issue + zulip
    print(f"  Total filtered:         {len(all_records)}")

    with open(OUTPUT, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")

    print(f"  Written to: {OUTPUT}")


if __name__ == "__main__":
    main()
