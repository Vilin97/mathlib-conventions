# Comparison with botbaki

A comparison of the 792 conventions mined in this project against the
conventions used by [botbaki](https://github.com/kim-em/botbaki/tree/master/prompts/mathlib4),
a Mathlib PR review bot.

Botbaki's convention knowledge lives in two reference files (`naming.md` and
`style.md`) plus a handful of inline rules in its prompt. This document
catalogues the high-frequency conventions from our dataset that botbaki
does not cover.

## Overview

| Dimension | This project | Botbaki |
|---|---|---|
| Number of rules | 792 | ~50–60 |
| Categories | 14 | 5 (Correctness, Style, Naming, Docs, Proofs) |
| Sources | 94k PR comments + 165k Zulip messages | Hand-curated |
| Evidence | Frequency-ranked (33k+ citations) | No frequency data |
| Format | Standalone knowledge base (md / json / csv) | LLM system prompts |

Botbaki's rules are concentrated on **surface-level review**: naming
conventions, formatting, docstrings, and basic proof tactics (`omega`,
`simp` squeezing). The mined data shows the Mathlib community spends most
of its review energy on deeper structural concerns that botbaki does not
address at all.

## High-frequency conventions absent from botbaki

Every convention listed below has **100+ mentions** across the source data
and has no counterpart in botbaki's prompts.

### File organization

| Freq | Convention |
|---:|---|
| 730 | **Put declarations in their canonical home.** Place each new definition, theorem, or instance in the existing Mathlib file whose mathematical topic, abstraction level, and dependencies best match it. Use `#find_home` or `#find_home!` first. |
| 185 | **Place declarations near the API they belong to.** Put a theorem, simp lemma, alias, or instance immediately after the definition or core lemma it elaborates. |
| 141 | **Prefer the earliest appropriate file in the hierarchy.** If a result is broadly useful and does not depend on later theory, move it upstream. |
| 112 | **Do not rely on transitive imports.** Import modules directly for declarations your file uses. |
| 108 | **Minimize imports aggressively.** Import only the modules actually needed; remove unused or "just in case" imports. |

The single highest-frequency convention in the entire dataset (730 mentions)
is about file placement. Botbaki does not address where things should live.

### Generalization

| Freq | Convention |
|---:|---|
| 453 | **State results under the weakest assumptions actually used.** Use the minimal typeclasses and hypotheses required by the proof. Prefer `Semiring` over `Ring`, `Preorder` over `LinearOrder`, `Finite` over `Fintype`, `Injective` over `Bijective`, etc. |
| 318 | **Generalize to the most natural useful form, but not speculatively.** Generalize over types, parameters, indices, domains, codomains, filters, and measures when the proof supports it. Do not introduce extra abstraction merely for its own sake. |
| 265 | **Prove the general theorem first; derive special cases afterward.** Do not duplicate the proof for the special case. |
| 146 | **Make non-inferable key parameters explicit; inferable ones implicit.** |
| 141 | **Extract reusable intermediate facts, but inline one-off helpers.** |
| 124 | **Reuse existing API; do not add redundant declarations.** |
| 106 | **Add the expected symmetric, dual, and parallel variants.** Provide the corresponding left/right, dual, additive/multiplicative, or similar variants when natural. |
| 105 | **Use one canonical representation; avoid duplicate APIs.** |

The second-highest-frequency convention overall (453 mentions) is about
weakening hypotheses. The entire generalization category (59 rules, ~3000
total mentions) has no counterpart in botbaki.

### Typeclass design

| Freq | Convention |
|---:|---|
| 302 | **Use the weakest sufficient typeclass assumptions.** State lemmas and instances with the minimal algebraic, order, topological, or categorical assumptions actually used. |
| 143 | **Use explicit type ascriptions or `inferInstanceAs` to guide inference.** Prefer this to strengthening theorem assumptions or relying on ambiguous elaboration. |
| 137 | **Declare something as an `instance` only if typeclass search should use it.** Otherwise declare it as a `lemma` or `def`. |
| 124 | **Prefer `Type*`/`Sort*` by default.** Add explicit universe binders only when necessary. |
| 116 | **Use typeclass arguments only for assumptions meant to be inferred.** Write `[P]` only if instance search is expected to supply it. |
| 109 | **Prefer standard bundled assumptions when they already exist.** Use the canonical Mathlib class rather than ad hoc combinations of hypotheses. |

### API design

| Freq | Convention |
|---:|---|
| 284 | **Reuse existing Mathlib abstractions and keep one canonical API.** Do not create parallel APIs that differ only by naming, notation, or packaging. |
| 209 | **Make inferable parameters implicit and central parameters explicit.** |
| 179 | **Preserve backward compatibility when changing public API.** Keep a deprecated alias or wrapper so downstream code still compiles with a warning. |
| 175 | **Hide implementation details behind user-facing lemmas.** Public statements should use the intended mathematical interface, not quotient representatives or internal wrappers. |
| 141 | **Add reusable API lemmas when proofs repeatedly need awkward rewrites.** |
| 135 | **Mirror existing APIs when adding analogous constructions.** Copy the established naming pattern, assumptions, and companion lemmas. |
| 126 | **Prefer one canonical representation and bridge alternatives explicitly.** |
| 113 | **State definitions and lemmas at the greatest natural generality.** |
| 103 | **Give every new public definition a usable API immediately.** Also provide `_apply` lemmas, `*_iff` characterizations, identity/composition laws, extensionality, and key instances. |

### Existing API reuse

| Freq | Convention |
|---:|---|
| 323 | **Reuse existing theorems, definitions, constructors, and instances.** Prefer fixing imports or applying the existing constructor over creating a parallel definition. |
| 119 | **Adapt existing lemmas with rewriting instead of reproving variants.** Use `rw`, `simp`, `simpa`, `convert`, or argument reordering to apply what already exists. |
| 117 | **Search for existing API before adding anything new.** Use `exact?`, `apply?`, `#find`, Loogle, grep, etc. |

### Module structure

| Freq | Convention |
|---:|---|
| 135 | **Use the most specific existing namespace.** Prefer an existing namespace over inventing a new one. |
| 116 | **Reuse existing definitions and keep one canonical abstraction.** |
| 115 | **Place declarations in the most specific appropriate module.** |
| 110 | **Keep new declarations out of `_root_`.** Place them in the namespace of the main mathematical object or theory. |

### Proof style and tactic usage

Botbaki has minimal proof guidance (prefer `omega` for arithmetic, basic
`simp` advice). These high-frequency conventions are absent:

| Freq | Convention |
|---:|---|
| 228 | **Factor repeated or substantial arguments into helper lemmas.** |
| 174 | **Reuse existing lemmas and APIs before writing long proofs.** |
| 150 | **Prefer targeted rewriting and canonical normal forms.** |
| 133 | **Prefer explicit API lemmas over fragile definitional equality.** |
| 120 | **Keep automation focused and curated.** |
| 117 | **Prefer clear proof structure over golfing.** |
| 107 | **Use `rfl` only for genuine definitional equalities.** |

## What botbaki covers well

For completeness, botbaki's strengths relative to this dataset:

- **Naming symbol dictionary**: A complete table mapping symbols to name
  components (`or`, `and`, `imp`/`of`, `iff`, `mem`, `union`, etc.) that
  is more lookup-friendly than our prose-style naming conventions.
- **Formatting specifics**: Precise rules for `by` placement, focusing
  dots, `calc` alignment, 100-char lines, and 2-space indent.
- **Recent Lean features**: Mentions the `module` keyword, `public import`,
  `meta import`, `public section`, and `@[expose] public section` which
  may not yet appear frequently in our source data.
- **Operational guardrails**: Rules about verifying claims before making
  them, using GitHub suggestion syntax, and avoiding linter-duplicate
  comments — useful for bot behavior but not Mathlib conventions per se.

## Takeaway

Botbaki focuses on surface-level review (naming, formatting, docstrings).
The three highest-frequency conventions it misses — file placement (730),
hypothesis minimality (453), and weakest typeclasses (302) — are each cited
more often than any single rule in botbaki's reference files. A review bot
that incorporated the generalization, API design, typeclass design, and
file organization categories would catch the issues Mathlib reviewers
most frequently raise.
