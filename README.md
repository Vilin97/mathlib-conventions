# Mathlib Conventions

792 unwritten coding conventions for [Mathlib](https://github.com/leanprover-community/mathlib4), systematically mined from PR reviews and Zulip discussions.

## Motivation

Mathlib has extensive [official style](https://leanprover-community.github.io/contribute/style.html), [naming](https://leanprover-community.github.io/contribute/naming.html), and [documentation](https://leanprover-community.github.io/contribute/doc.html) guides, but the majority of conventions that reviewers enforce are unwritten. Contributors learn them through PR feedback, one correction at a time.

This project extracts those unwritten rules at scale. The intended use is:
- **AI-assisted PR review**: feed the conventions to an LLM agent that reviews Mathlib PRs
- **PR improvement skill**: a tool that checks and improves PRs against known conventions before submission

For example, from a [PR-reviews discussion](https://leanprover.zulipchat.com/#narrow/channel/144837-PR-reviews/topic/.2335753.20and.20.2335755.3A.20forward.20Euler.20method.20for.20ODEs/with/584104398), a reviewer noted *"the use of superfluous have's is generally avoided prior to a calc"* — one of hundreds of conventions that exist only in reviewers' heads.

## Results

792 conventions across 14 categories, each with frequency data and provenance:

| Category | Rules | Total mentions | Top convention |
|---|---|---|---|
| proof style | 90 | 2866 | Factor repeated arguments into helper lemmas (228) |
| simp usage | 77 | 3314 | Use `simp only [...]` when exact control matters (287) |
| tactic usage | 76 | 2019 | Keep automation focused and curated (120) |
| code style | 71 | 3397 | Make inferable arguments implicit (220) |
| naming | 64 | 4096 | Prefer standard mathematical terminology (367) |
| documentation | 52 | 3637 | Keep docstrings about the result, not the proof (329) |
| module structure | 59 | 1764 | Use the most specific existing namespace (135) |
| generalization | 59 | 2995 | State results under weakest assumptions (453) |
| typeclass design | 57 | 2470 | Use weakest sufficient typeclass assumptions (302) |
| api design | 54 | 2861 | Reuse existing abstractions (284) |
| existing api | 50 | 1497 | Reuse existing theorems and definitions (323) |
| file organization | 42 | 2458 | Put declarations in their canonical home (730) |
| other | 23 | 34 | Name lemmas from outermost to innermost structure (3) |
| performance | 10 | 12 | Cache typeclass synthesis outside hot paths (2) |

Comparison with official Mathlib documentation:
- **58% NEW**: not covered by any official guide
- **27% EXTENDS**: adds actionable detail beyond official docs
- **15% COVERED**: already documented officially

88% of conventions are corroborated by both PR reviews and Zulip channel discussions.

## Output files

- [`conventions_FINAL.md`](conventions_FINAL.md) — all 792 conventions in markdown, sorted by frequency within each category
- [`conventions_enriched.json`](conventions_enriched.json) — same data in structured JSON with per-convention metadata:
  - `frequency_total` / `frequency_pr_reviews` / `frequency_mathlib4`: how many raw reviewer comments expressed this convention
  - `source`: whether it was found in PR reviews, Zulip #mathlib4, or both
  - `doc_status`: NEW, EXTENDS, or COVERED relative to official Mathlib docs

## Methodology

### 1. Data collection

Scraped ~259k comments from three sources:
- **GitHub PR reviews** (~94k): issue comments and inline review comments from [leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) via the GitHub API
- **Zulip #PR-reviews** (~32k): all messages from the [PR reviews channel](https://leanprover.zulipchat.com/#narrow/channel/144837-PR-reviews)
- **Zulip #mathlib4** (~133k): all messages from the [mathlib4 channel](https://leanprover.zulipchat.com/#narrow/channel/287929-mathlib4)

Filtered to comments from 28 Mathlib maintainers and 20 prominent contributors (top reviewers by review comment count).

### 2. Convention extraction

Filtered ~155k target-member comments (removing short acks, bare code suggestions, bot messages), then classified each via OpenAI GPT-5.4-nano batch API, asking whether it contains a generalizable coding convention and if so, extracting the rule and category.

Result: ~46k raw conventions.

### 3. Deduplication (three-model consensus)

For each category, sent all raw conventions independently to three LLMs:
- GPT-5.4
- Gemini 3.1 Pro
- Claude Opus 4.6

Each produced a deduplicated list of 40-100 conventions. Then GPT-5.4 merged all three lists into one final canonical list per category, keeping conventions that appeared in 2+ models as high-confidence.

### 4. Validation

- **Outdatedness check**: compared against Lean 3-to-4 migration guides to flag conventions referencing deprecated syntax or removed features. Removed 8 outdated conventions.
- **Official docs comparison**: compared each convention against the three official Mathlib guides (style, naming, documentation) to classify as COVERED, EXTENDS, or NEW.
- **Contradiction check**: identified and removed 2 conventions that conflicted with official guidance.

### 5. Frequency estimation

Used Qwen3-Embedding-8B to embed all raw conventions and final conventions per category, retrieved top-5 candidates per raw convention, then used GPT-5.4-nano to pick the best match (or no match). This gives an approximate count of how many independent reviewer comments expressed each convention.

## Whose conventions are these?

28 Mathlib maintainers and top 20 non-maintainer reviewers by review comment count. See [`members.py`](members.py) for the full list with GitHub usernames and Zulip IDs.

## Reproducing

```bash
pip install -r requirements.txt
# .env must contain: ZULIP_API_KEY, ZULIP_EMAIL, ZULIP_SITE, GITHUB_TOKEN,
#                     OPENAI_API_KEY, GEMINI_API_KEY, NEBIUS_API_KEY

# 1. Scrape
python scrape_github.py
python scrape_zulip.py  # scrapes #PR-reviews; modify for #mathlib4

# 2. Filter and classify
python filter_comments.py
python classify_batch.py  # submits OpenAI batch job

# 3. Collect and deduplicate
python collect_results.py --collect
python dedup_final.py  # runs GPT + Gemini; Claude agents launched separately

# 4. Validate
python validate_conventions.py data/conventions_FINAL.md
```
