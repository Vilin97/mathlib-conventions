# Mathlib Conventions

Mining and categorizing coding conventions for [Mathlib](https://github.com/leanprover-community/mathlib4) PRs from maintainer and reviewer feedback.

## Goal

Mathlib has many unwritten conventions that contributors learn through PR reviews. This project systematically collects reviewer comments from maintainers and prominent contributors, then categorizes them into actionable convention rules.

For example, from a [PR-reviews discussion](https://leanprover.zulipchat.com/#narrow/channel/144837-PR-reviews/topic/.2335753.20and.20.2335755.3A.20forward.20Euler.20method.20for.20ODEs/with/584104398), Yan noted: *"the use of superfluous have's is generally avoided prior to a calc"*. The goal is to discover and catalog hundreds of such conventions.

## Data sources

- **GitHub PR reviews**: ~36k pull requests from [leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4/pulls?q=sort%3Aupdated-desc+is%3Apr) — issue comments and review comments
- **Zulip PR-reviews channel**: [#PR-reviews](https://leanprover.zulipchat.com/#narrow/channel/144837-PR-reviews) on the Lean Zulip

## Whose comments we collect

- **Mathlib maintainers** ([full list](https://leanprover-community.github.io/teams/maintainers.html)): ~28 people
- **Prominent contributors**: top contributors by commit count and review activity

Comments are collected from everyone (API doesn't support per-author filtering), then filtered locally to the target set.

## Pipeline

1. **Scrape** (`scrape_github.py`, `scrape_zulip.py`) — fetch all comments/messages, save to CSV
2. **Filter** — keep only comments from maintainers and prominent contributors
3. **Categorize** — group conventions by topic (naming, style, proof structure, API design, etc.)

## Setup

```bash
pip install -r requirements.txt
# .env must contain ZULIP_API_KEY, ZULIP_EMAIL, ZULIP_SITE, GITHUB_TOKEN
```

## Output

- `data/github_issue_comments.csv` — all issue comments on mathlib4 PRs
- `data/github_review_comments.csv` — all inline review comments on mathlib4 PRs
- `data/zulip_pr_reviews.csv` — all messages from the Zulip #PR-reviews channel
