"""Scrape all PR comments from leanprover-community/mathlib4.

Uses repo-level endpoints for efficiency:
  - GET /repos/{owner}/{repo}/issues/comments  (issue comments on PRs)
  - GET /repos/{owner}/{repo}/pulls/comments    (inline review comments)

Both are paginated at 100/page, sorted by updated_at desc (most recent first).
Results are saved to CSV incrementally so progress isn't lost on interruption.
"""

import csv
import os
import sys
import time
from pathlib import Path

csv.field_size_limit(sys.maxsize)

import requests
from dotenv import load_dotenv

load_dotenv()

REPO = "leanprover-community/mathlib4"
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Rate limit handling
def api_get(url, params=None, max_retries=5):
    """Make a GET request with rate-limit and transient error handling."""
    for attempt in range(max_retries):
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 1) + 5
            print(f"  Rate limited. Waiting {wait}s until reset...")
            time.sleep(wait)
            continue
        if resp.status_code in (500, 502, 503, 504):
            wait = 2 ** attempt * 5
            print(f"  Server error {resp.status_code}. Retry {attempt+1}/{max_retries} in {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def scrape_endpoint(endpoint, csv_path, fields, description):
    """Scrape a paginated GitHub API endpoint to CSV.

    Appends to existing CSV if it exists (for resumption).
    """
    url = f"https://api.github.com/repos/{REPO}/{endpoint}"
    params = {
        "sort": "updated",
        "direction": "desc",
        "per_page": 100,
    }

    # Check existing progress
    existing_ids = set()
    if csv_path.exists():
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row["id"])
        print(f"  Found {len(existing_ids)} existing records in {csv_path}")

    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    outfile = open(csv_path, "a", newline="")
    writer = csv.DictWriter(outfile, fieldnames=fields)
    if write_header:
        writer.writeheader()

    page = 1
    total_new = 0
    consecutive_existing = 0

    print(f"Scraping {description}...")
    while True:
        params["page"] = page
        resp = api_get(url, params)
        items = resp.json()

        if not items:
            print(f"  Page {page}: empty — done.")
            break

        new_on_page = 0
        for item in items:
            item_id = str(item["id"])
            if item_id in existing_ids:
                consecutive_existing += 1
                continue

            consecutive_existing = 0
            row = extract_row(item, endpoint)
            writer.writerow(row)
            new_on_page += 1
            total_new += 1

        outfile.flush()

        # Status update
        remaining = resp.headers.get("X-RateLimit-Remaining", "?")
        print(f"  Page {page}: {new_on_page} new, {len(items)} total on page. "
              f"API calls remaining: {remaining}")

        # Check for next page via Link header
        if 'rel="next"' not in resp.headers.get("Link", ""):
            print(f"  No next page — done.")
            break

        page += 1

    outfile.close()
    print(f"  Total new records: {total_new}")


def extract_row(item, endpoint):
    """Extract a flat dict from a GitHub API comment object."""
    user = item.get("user") or {}
    # Extract PR number from URLs
    # issue_comment: html_url contains /issues/NNN or /pull/NNN
    # review_comment: pull_request_url contains /pulls/NNN
    pr_number = ""
    if "pull_request_url" in item:
        pr_number = item["pull_request_url"].rstrip("/").split("/")[-1]
    elif "issue_url" in item:
        pr_number = item["issue_url"].rstrip("/").split("/")[-1]
    elif "html_url" in item:
        parts = item["html_url"].split("/")
        for i, p in enumerate(parts):
            if p in ("pull", "issues") and i + 1 < len(parts):
                pr_number = parts[i + 1].split("#")[0]
                break

    row = {
        "id": str(item["id"]),
        "pr_number": pr_number,
        "author": user.get("login", ""),
        "author_id": str(user.get("id", "")),
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "body": item.get("body", "") or "",
        "html_url": item.get("html_url", ""),
    }

    # Review-comment-specific fields
    if endpoint == "pulls/comments":
        row["path"] = item.get("path", "")
        row["diff_hunk"] = item.get("diff_hunk", "") or ""

    return row


ISSUE_COMMENT_FIELDS = [
    "id", "pr_number", "author", "author_id",
    "created_at", "updated_at", "body", "html_url",
]

REVIEW_COMMENT_FIELDS = [
    "id", "pr_number", "author", "author_id",
    "created_at", "updated_at", "body", "html_url",
    "path", "diff_hunk",
]


def main():
    print(f"GitHub token: ...{TOKEN[-4:]}")

    # Check rate limit
    resp = api_get("https://api.github.com/rate_limit")
    rl = resp.json()["rate"]
    print(f"Rate limit: {rl['remaining']}/{rl['limit']} "
          f"(resets at {time.strftime('%H:%M:%S', time.localtime(rl['reset']))})")

    scrape_endpoint(
        "issues/comments",
        DATA_DIR / "github_issue_comments.csv",
        ISSUE_COMMENT_FIELDS,
        "issue comments (PR discussion threads)",
    )

    scrape_endpoint(
        "pulls/comments",
        DATA_DIR / "github_review_comments.csv",
        REVIEW_COMMENT_FIELDS,
        "review comments (inline code review)",
    )

    print("\nDone!")


if __name__ == "__main__":
    main()
