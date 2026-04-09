# Mathlib Conventions

792 coding conventions for Lean 4 / Mathlib, distilled from:
- ~94k GitHub PR review comments from leanprover-community/mathlib4
- ~32k messages from the Zulip #PR-reviews channel
- ~133k messages from the Zulip #mathlib4 channel

Extracted via GPT-5.4-nano classification, then deduplicated via three-model
consensus (GPT-5.4, Gemini 3.1 Pro, Claude Opus 4.6), validated for outdatedness.

## summary statistics

| stat | value |
|---|---|
| total conventions | 792 |
| total raw mentions | 33395 |
| mean frequency | 42.2 |
| median frequency | 23 |
| conventions with 100+ mentions | 85 |
| conventions with 50+ mentions | 196 |
| conventions with 10+ mentions | 620 |
| source: both channels | 704 |
| source: PR reviews only | 55 |
| source: mathlib4 only | 33 |
| doc status: NEW (not in official docs) | 462 |
| doc status: EXTENDS (adds detail) | 210 |
| doc status: COVERED (already documented) | 120 |

## conventions by category

| category | rules | total mentions | avg freq | top convention |
|---|---|---|---|---|
| proof style | 91 | 2866 | 31 | Factor repeated or substantial arguments into help (228) |
| simp usage | 77 | 3314 | 43 | Use `simp only [...]` when exact control matters (287) |
| tactic usage | 76 | 2019 | 27 | Keep automation focused and curated (120) |
| code style | 70 | 3374 | 48 | Make inferable arguments implicit and non-inferabl (220) |
| naming | 64 | 4096 | 64 | Prefer standard mathematical and Mathlib terminolo (367) |
| documentation | 61 | 3637 | 60 | Keep theorem docstrings about the result, not the  (329) |
| module structure | 59 | 1764 | 30 | Use the most specific existing namespace (135) |
| generalization | 59 | 2995 | 51 | State results under the weakest assumptions actual (453) |
| typeclass design | 57 | 2470 | 43 | Use the weakest sufficient typeclass assumptions (302) |
| api design | 54 | 2861 | 53 | Reuse existing Mathlib abstractions and keep one c (284) |
| existing api | 50 | 1497 | 30 | Reuse existing theorems, definitions, constructors (323) |
| file organization | 42 | 2458 | 59 | Put declarations in their canonical home (730) |
| other | 22 | 32 | 1 | Name lemmas from outermost to innermost structure (3) |
| performance | 10 | 12 | 1 | Cache typeclass synthesis outside hot paths (2) |
| total | 792 | 33395 | 42 | |

---

# proof style

1. Factor repeated or substantial arguments into helper lemmas

Extract repeated reasoning or nontrivial subproofs into helper lemmas, often `private` if they are not public API. But avoid ad hoc single-use lemmas unless they materially improve readability or reuse.

2. Reuse existing lemmas and APIs before writing long proofs

If a proof is longer than expected, first search for a theorem that already expresses the needed fact, perhaps after a small rewrite. Prefer `exact`, `apply`, `rw`, `simpa`, `.mp`, or `.mpr` over reproving standard facts.

3. Prefer targeted rewriting and canonical normal forms

Use focused `rw`, `simp only [...]`, or local simplification at the relevant hypothesis or goal rather than broad simplification. Rewrite into standard forms such as `mem_*_iff` or other canonical API shapes early.

4. Prefer explicit API lemmas over fragile definitional equality

Do not rely on accidental definitional equality across wrappers, coercions, or implementation details in library-facing proofs. Prove and use named lemmas about the abstraction instead.

5. Prefer clear proof structure over golfing

Write proofs so the main argument is easy to follow. Avoid dense one-liners, deep nesting, giant `exact` terms, or brittle automation when a clearer structured proof is available.

6. Use `rfl` only for genuine definitional equalities

If the goal is truly definitional, close it with `rfl` or `Iff.rfl`, preferably directly. Do not force “heavy `rfl`” on large terms when a small rewrite is clearer or more robust.

7. Prefer high-level domain-specific APIs over element-chasing

For algebraic, categorical, topological, set-theoretic, filter, and subobject arguments, use the standard library combinators, homomorphism lemmas, universal properties, basis lemmas, and extensionality principles rather than manual element-chasing.

8. Keep theorem hypotheses minimal

Remove unused assumptions. Do not require stronger hypotheses, extra typeclasses, or side conditions unless the proof genuinely needs them.

9. Prefer rewriting lemmas over `unfold`

Avoid broad `unfold` in proofs. Add and use named lemmas such as `foo_def` or `foo_apply` so rewriting is explicit and stable.

10. Use extensionality lemmas for equality of functions and structures

For equality of functions, morphisms, sets, or structures, use `ext`, `funext`, `SetLike.ext`, `LinearMap.ext`, and similar lemmas rather than unfolding definitions or doing indirect equality proofs.

11. Prefer `simpa`/`simpa using` for short adaptations

If a proof is just an existing lemma plus harmless rewriting, use `simpa` rather than a longer `rw`/`apply`/`exact` sequence.

12. Unfold only what you need, and prefer `dsimp` for definitional simplification

When unfolding is necessary, target the exact constant with `dsimp only [...]` or a narrow `unfold`. Use `dsimp` for pure definitional simplification and `simp` for lemma-based simplification.

13. Add explicit types or arguments when elaboration is fragile

If coercions, dependent types, or inference make a proof hard to read or unstable, add type annotations, named arguments, or explicit application grouping.
```lean
rw [lemma_name (α := α) (f := f)]
```

14. Inline tiny one-use helpers

If a helper lemma or `have` is just a short instantiation of existing lemmas and used once, inline it instead of creating extra declarations.

15. State lemmas in a canonical, reusable, and appropriately general form

Keep theorem statements short and in the normal API form. Avoid awkward coercions, wrappers, contrapositive formulations, or unnecessary specialization; prove the most natural useful statement and derive variants as corollaries.

16. Use `suffices` to expose the key intermediate goal

When the proof naturally proceeds through a simpler or more canonical intermediate claim, state it with `suffices`. This is often clearer than a long chain of local rewrites.
```lean
by
  suffices h : p = ⊥ by simpa [h]
  ...
```

17. Use standard case-split idioms

For simple decidable splits, use idioms like `by_cases h : x = 0` or `obtain rfl | h := eq_or_ne x 0`. For order splits, use standard lemmas such as `le_total`, `lt_or_ge`, or `le_or_gt`.

18. Use `have` for facts, `let` for data, and `letI`/`haveI` for local instances

Record reusable propositions with `have`, name terms with `let`, and introduce proof-local instances with `letI` or `haveI`. Do not pollute theorem statements with local implementation details.

19. Shape goals explicitly with `change`, `show`, `convert`, or `convert_to` when needed

If a lemma almost matches but the goal is in the wrong syntactic form, reshape the goal explicitly rather than forcing awkward rewrites. Use these tools deliberately, not as a substitute for missing API.
```lean
change ((x : ℤ) ≤ y)
convert h using 1
```

20. Prefer the simplest applicable specialized lemma or tactic

Use the straightforward API lemma or domain tactic first, such as `positivity`, `norm_num`, `ring`, `linarith`, `omega`, `norm_cast`, or `field_simp`. Reach for more technical variants only if needed.

21. Add focused regression tests for subtle tactic or elaboration behavior

When fixing or extending tactics, macros, simprocs, or elaboration behavior, add small explicit tests that capture the bug and nearby edge cases.

22. Use `calc` for chained equalities and inequalities

When a proof is naturally a sequence of algebraic or order-theoretic steps, use a `calc` block rather than repeated `rw`, `trans`, or transitivity lemmas.
```lean
calc
  x ≤ y := hxy
  _ = z := hz
  _ < t := hzt
```

23. Structure `↔` proofs explicitly

For iff goals, keep the two directions visibly separate using `constructor`, `refine ⟨..., ...⟩`, or `where mp := ...; mpr := ...`.

24. Prefer universal properties and natural isomorphisms over forced equalities

For categorical or abstract constructions, use the universal property and the corresponding API. State isomorphisms or equivalences rather than equalities when objects are naturally isomorphic, and prove equalities componentwise with `ext` when appropriate.

25. Prefer standard induction principles, with explicit generalization when needed

Use the type’s intended induction principle, and be explicit about `generalizing`, `revert`, or `generalize` so the induction hypothesis has the right strength.
```lean
induction n generalizing k with
| zero => ...
| succ n ih => ...
```

26. Prefer `obtain`/`rcases` for witnesses and `let` for data

Use `let` to name computed terms, and use `obtain`/`rcases`/`cases` to extract witnesses or components from hypotheses. Avoid `choose` unless it is genuinely the right tool.

27. Avoid unnecessary case splits and duplicated branch work

Do not introduce `by_cases`, pattern matches, or large case analyses unless they contribute to the argument. If branches share setup, move that work outside the split or package it in a common `have`.

28. Handle trivial or degenerate cases early

Split off easy cases like `x = 0`, `n = 0`, `s = ∅`, `⊥`, or `⊤` at the start so the main proof stays clean. Close such branches immediately with `simp`, `rfl`, or a standard lemma when possible.

29. Use standard proof patterns for set and subobject equality

For set and subobject equalities, prefer canonical patterns such as `ext x; simp` or `SetLike.ext`. Use propositional automation only as final cleanup, not as a substitute for structure.

30. Destructure hypotheses and witnesses early

Use `obtain`, `rcases`, `rintro`, or pattern matching to extract the components you need from `∃`, `And`, `Or`, and similar hypotheses. Do not repeatedly write `.1`, `.2`, or projection tricks.

31. Orient rewrite lemmas and simp lemmas toward simplification

State equalities with the more complicated expression on the left and the simpler normal form on the right. Do the same for `iff` lemmas intended for rewriting.

32. Prefer explicit constructors and witnesses

When proving existential, product, subtype, or `iff` goals, use `refine ⟨...⟩`, `use`, `constructor`, or direct constructor syntax so the subgoals are visible.

33. Add basic API lemmas after new definitions

After introducing a definition, provide the obvious `rfl`/`_def`/`_apply` lemmas and basic `@[simp]` lemmas for constructors, projections, coercions, and applications.

34. Keep the main proof branch visually prominent

Follow the line-of-sight rule: subordinate branches may be indented, but the main proof flow should remain easy to scan. Use bullets or `case` blocks to separate subgoals clearly.

35. Separate rewriting from discharge tactics

When using tactics like `field_simp`, `simp`, or algebraic normalization, structure the proof in phases: first rewrite or normalize, then solve the resulting goals. Keep side conditions visible and explicit.

36. Keep proof style consistent within a proof

Do not mix tactic mode and term mode in a small expression unless it clearly improves readability. Avoid deeply nested `by` blocks when a direct style works.

37. Use filter and eventual-equality APIs idiomatically

For filter, almost-everywhere, or eventual arguments, use `filter_upwards`, `EventuallyEq`, and standard congruence lemmas rather than manually unpacking filter definitions.

38. Prefer `.mp` / `.mpr` when using one direction of an `iff`

If you need only one direction of an iff lemma, apply `.mp` or `.mpr` directly instead of rewriting the whole goal.

39. Keep one active goal at a time and discharge subgoals explicitly

Avoid leaving many goals open simultaneously. Use bullets, `case`, `all_goals`, helper lemmas, or explicit structure so every generated subgoal is handled clearly.

40. Prefer `exact` when you already have the term, and `refine` when you want visible subgoals

Use `exact` when the required term is already known. Prefer `refine` over `apply` when it makes the remaining obligations clearer.

41. Control expensive unfolding and computation when performance matters

If elaboration or kernel checking is slow because a definition unfolds aggressively, factor expensive computation into separate definitions or use appropriate opacity wrappers. Prefer source-level fixes over brittle local hacks.

42. Keep classical reasoning local

Do not add `Classical` or decidability assumptions to theorem statements unless required by the statement itself. Use `by classical` inside the proof instead.

43. Design simp lemmas carefully and keep simp local when needed

Add explicit `@[simp]` lemmas for intended rewriting behavior, but avoid simp loops and unstable rewrite directions. For delicate projection or coercion goals, prefer local simplification over broad global simp behavior.

44. Fix the root cause of automation failures

If `simp`, `to_additive`, `reassoc`, `norm_cast`, or similar tools fail downstream, fix the underlying attribute, lemma, or generated theorem when possible rather than patching many individual proofs.

45. Keep rewrite chains readable

If many rewrites are needed, use a `calc` block or intermediate `have`s rather than a long opaque `rw [...]` chain. Avoid tricks like `rw [show ... by ...]` when a clearer structure is available.

46. State and discharge side conditions explicitly for partial operations

For division, inverses, roots, and similar operations, add the needed nonzero or nonnegativity assumptions explicitly. Do not rely on hidden side-condition discharge.

47. Introduce local instances explicitly with `letI`/`haveI`

If a proof needs a typeclass instance that is not inferable from the context, add it locally with `letI` or `haveI`. Do not rely on accidental inference through unrelated variables.

48. Keep ports incremental and avoid unrelated cleanup

When porting Lean 3 or older mathlib code, first get the file compiling with minimal semantic changes. Defer stylistic refactors and unrelated cleanup unless they are required to make progress.

49. Use coercion and cast lemmas deliberately

For cast-heavy goals, first align the syntax with `change` if needed, then use `norm_cast`, `push_cast`, or explicit coercion lemmas. Do not rely on implicit coercions or magical cast normalization.

50. Add `@[ext]` lemmas for new structures when appropriate

If a structure has a natural extensionality principle, provide an `@[ext]` lemma in the normal form users naturally need.

51. Handle dependent rewriting explicitly

When later arguments depend on earlier equalities, prefer `subst`, `rintro rfl`, `obtain rfl`, `dsimp`, or explicit cast lemmas. Do not hope that `simp` will magically solve dependent rewrites.

52. Use antisymmetry lemmas for equality of ordered objects

For set, submodule, subgroup, or lattice equalities, prove both inclusions or inequalities and conclude with `subset_antisymm`, `le_antisymm`, or similar lemmas.

53. Prefer direct contradiction tools over awkward case splits

Use `contrapose`, `contrapose!`, `mt`, `Or.resolve_left`, and similar tools when they match the argument better than a `by_cases` that immediately leads to contradiction.

54. Use local abbreviations sparingly and purposefully

Introduce `let` or `set` only when it clarifies a recurring expression, controls normalization, or improves proof structure. Avoid throwaway local definitions that obscure the main argument.

55. Design definitions to compute well

Choose definitions so key projections or evaluations are `rfl` or reduce by simple computation when possible. Separate computational data from later proof obligations so downstream proofs do not depend on opaque machinery.

56. Keep abstraction boundaries opaque

Do not unfold wrappers, type synonyms, structures, or proof terms just to make a proof go through unless there is a compelling reason. Prove and use lemmas about the abstraction instead of exposing implementation details.

57. Prefer quotient APIs and direct elimination of impossible cases

For quotient-like types, use the provided induction, recursion, and universal-property APIs rather than extracting representatives ad hoc. For vacuous branches, use idiomatic eliminators like `False.elim`, `Fin.elim0`, or `rintro ⟨⟩`.

58. Build structures and instances directly and reuse inherited fields

When defining bundled structures or instances, construct them explicitly with the target constructor and reuse inherited operations and proofs whenever possible. Avoid reproving obvious superclass fields or relying on fragile derived machinery.

59. Structure proofs so each step addresses the current goal

Write proofs so each tactic block visibly solves the goal in front of it. Avoid scripts that depend on fragile goal ordering or on later tactics accidentally solving earlier goals.

60. Put binders and hypotheses in the statement when natural

If the proof immediately introduces variables or assumptions, move them before the colon rather than starting with `intro` boilerplate.

61. Use descriptive names for local hypotheses and facts

Name hypotheses and intermediate facts clearly, such as `hx`, `hmem`, or `hmono`. Avoid overuse of `this`, anonymous assumptions, or repeated projection chains like `h.1.2`.

62. Keep automation targeted and readable

Use automation only after the goal has been put into a clean, stable shape. Do not use `aesop`, `simp`, or similar tactics as glorified `intro`/`constructor`, and prefer small `simp only` sets or targeted rewrites for intermediate steps.

63. Remove unused hypotheses and unnecessary intermediate facts

Treat linter warnings such as `unusedHavesSuffices` as prompts to simplify the proof. Delete irrelevant assumptions and avoid long walls of `have` statements that obscure the real dependencies.

64. Prefer direct construction for definitions and objects

Do not define objects by tactic scripts that merely prove existence. Construct them directly so definitional behavior is good and later proofs are simpler.

65. Use `subst` early for equalities of variables

If a hypothesis identifies a local variable, eliminate it early with `subst`, `rintro rfl`, or `obtain rfl`. This often simplifies the context and removes awkward casts.

66. Prefer structural recursion and honest termination arguments

Define recursive functions by structural recursion whenever possible. If well-founded recursion is necessary, use `termination_by` with a measure that matches the actual recursive decrease, and avoid `partial` for definitions you will reason about.

67. Use `Subsingleton.elim` in subsingleton contexts

When proving equality in a subsingleton type, use `Subsingleton.elim` rather than forcing progress with congruence or extensionality.

68. Avoid blank lines inside proofs

Do not use empty lines inside proof blocks. If you need visual separation, use proof structure or a brief comment instead.

69. Induct on the actual structure, not a proxy

Induct on the list, finset, quotient witness, or natural number itself rather than on length or another derived measure unless that measure is essential.

70. Keep induction cases short and clear

In inductive proofs, handle base and step cases with focused `simp` and the induction hypothesis when possible. Use explicit case names rather than relying on fragile goal renaming.

71. Use categorical reassociation, naturality, and cancellation lemmas

In category-theoretic proofs, prefer `[reassoc]` lemmas, naturality lemmas, `cancel_mono`, and `cancel_epi` over long manual associativity rewrites.

72. Avoid unnecessary coercions in theorem statements

Keep theorem statements at the natural abstraction level. Do not coerce morphisms, subobjects, or bundled structures to concrete types unless necessary.

73. Prefer `Finset`/`Finite` APIs when finiteness is central

If the argument is fundamentally finite, use `Finset`, `Finite`, and their APIs rather than set-theoretic encodings that obscure finiteness.

74. Add comments sparingly but usefully

Do not clutter short proofs with comments, but add brief comments for long proofs or non-obvious strategy shifts so the overall argument is clear.

75. Refactor for structure before micro-optimizing performance

If a proof or file is slow, first reduce duplication, simplify elaboration, and improve structure. Diagnose the source of slow `simp`, typeclass search, or unfolding before adding ad hoc workarounds.

76. Prefer `↔` when the result is genuinely bidirectional

If both directions are natural and useful, state an `iff`. If only one direction matters, do not force an `iff`.

77. Order binders and hypotheses for readability

Put explicit data before dependent hypotheses, and structural assumptions before side conditions. Keep argument order aligned with common usage.

78. Prefer separate assumptions over conjunction-packed hypotheses

Use separate named assumptions instead of a single `h : A ∧ B ∧ C` unless the bundled form is mathematically canonical.

79. Do not add tautological or purely definitional lemmas without API value

Avoid lemmas whose statement is just a syntactic tautology or trivial `rfl` unless the named lemma materially improves rewriting, discoverability, or the public API.

80. Prefer `Finite` over `Fintype` in statements when possible

If finiteness is only needed inside the proof, do not require a `Fintype` instance in the theorem statement. Introduce stronger finiteness data locally only when needed.

81. Prefer explicit proof terms for proof arguments

When a function expects a proof, pass an actual proof term. Use `by decide` only when the proposition is decidable and computation is the intended proof method.

82. Do not modify hypotheses in place unless necessary

Prefer deriving new facts from existing hypotheses rather than rewriting or mutating the originals. Keeping the original hypotheses intact usually makes the proof state easier to follow.

83. Prefer `rw`/`simp` over `▸`, and avoid `erw`

Use ordinary rewriting tactics rather than dependent rewrite syntax `▸` unless it is clearly the best option. Replace `erw` with proper rewrites, `change`, or better lemmas before merging.

84. Prefer canonical numeral and arithmetic formulations

Avoid brittle formulations such as `Nat.sub` and non-canonical numeral syntax like `bit0`/`bit1` in statements when a cleaner equivalent form exists. For naturals, prefer `n ≠ 0` to express nonzeroness, converting to `0 < n` only when needed.

85. Introduce binders directly in local facts when natural

When a local fact is naturally quantified, write the binders in the `have` itself.
```lean
have h (x : α) (hx : x ∈ s) : P x := by ...
```

86. Use `gcongr` for monotonicity and congruence inequality goals

When an inequality is obtained by applying monotone operations to known inequalities, prefer `gcongr` over manually chaining low-level monotonicity lemmas.

87. Prefer equivalences for cardinality equalities

When proving two finite types or sets have the same cardinality, construct an equivalence and use `Fintype.card_congr` or `Nat.card_congr`.

88. Use `rintro` for structured introductions

When introducing hypotheses with patterns, prefer `rintro` over repeated `intro` followed by manual destructuring.

89. Revert dependent hypotheses together

If one hypothesis depends on another, revert the main hypothesis so dependent hypotheses are reverted with it, then re-introduce them after rewriting.

90. Prefer weaker natural assumptions in analytic and measure-theoretic statements

Do not assume full measurability, integrability, or similarly strong hypotheses if weaker standard assumptions such as `AEMeasurable` or local versions suffice.

91. Avoid asserting equality of typeclass instances

Do not prove equalities between instances unless absolutely necessary. Prove the mathematical property you need instead.

# simp usage

92. Use `simp only [...]` when exact control matters

When proof stability, performance, or intent depends on exactly which rewrites fire, use `simp only [...]` with a minimal lemma list. This is especially appropriate for non-terminal simplification.

93. Avoid non-terminal `simp`

Do not use broad `simp` in the middle of a proof when it leaves substantial work behind. For non-terminal simplification, prefer `simp only [...]`, `rw`, `simp_rw`, or `dsimp`; an exception is `simp` immediately followed by a normalizing tactic such as `ring`, `abel`, `omega`, or `norm_num`.

94. Prefer terminal `simp`

Use plain `simp` or `simp [...]` when it closes the goal. Only replace it with `simp only [...]` if you need tighter control for stability, performance, or debugging.

95. Only add `@[simp]` when it improves automation

Do not mark a lemma `@[simp]` just because it is easy to prove. A simp lemma should be broadly useful, should fire often, and should simplify toward a canonical form.

96. Mark genuinely useful canonical lemmas with `@[simp]`

Add `@[simp]` to canonical evaluation, coercion, projection, constructor, and membership lemmas that users should rewrite with often. If the proof is definitional, prove it by `rfl`.
```lean
@[simp] theorem foo_apply (x) : foo x = ... := rfl
```

97. Orient simp lemmas toward canonical normal forms

State `@[simp]` lemmas with the more complicated or less canonical expression on the left and the simpler normal form on the right. For `iff` lemmas, put the more complicated condition on the left.

98. Prefer existing API lemmas over unfolding definitions

If Mathlib already has a lemma expressing the behavior you need, use it with `rw` or `simp` rather than unfolding the definition. This keeps proofs stable under refactors.

99. Prefer `@[simps]` to generate projection simp lemmas

When defining a structure-valued object, equivalence, or homomorphism, use `@[simps]` so Mathlib generates the standard projection and evaluation lemmas automatically instead of writing boilerplate by hand.

100. Inspect and control generated `@[simps]` lemmas

Check generated lemmas with `simps?` or `simps!?`, restrict to useful projections, and avoid generating noisy or unhelpful lemmas. If `@[simps]` produces the wrong shape, write the needed simp lemmas manually instead.

101. Do not add redundant simp lemmas

If `simp` can already prove the lemma from existing simp rules, or an existing simp lemma already performs the same rewrite, do not add another `[simp]` theorem. Keep the simp set minimal.

102. Prefer `simp` over long chains of simp-lemma rewrites

If a proof is mostly a sequence of rewrites by simp lemmas, replace it with one `simp` or `simpa` call. Conversely, if a single `rw` suffices, do not use `simp`.

103. Avoid `@[simp]` lemmas with hard side conditions

Do not mark lemmas `[simp]` if they require hypotheses that `simp` usually cannot infer or discharge cheaply. Prefer formulations whose assumptions are easy for typeclass inference or `simp` to handle.

104. Prefer dedicated coercion simp lemmas over relying on defeq

If `simp` does not rewrite through a coercion by definitional equality alone, add a targeted simp lemma matching the exact coercion or application pattern. Do not rely on fragile unfolding behavior.

105. Prefer `simpa ... using ...` for direct simplification

When a goal is solved by simplifying an existing term or hypothesis, write `simpa [...] using h` rather than `simp [...] at h; exact h` or `simp [...]; exact h`.

106. Ensure a simp lemma can actually fire

A simp lemma should have enough information on its left-hand side for `simp` to infer the needed parameters. Avoid underdetermined lemmas whose arguments cannot be reconstructed from the target expression.

107. Keep simp lemma left-hand sides in simp-normal form

Do not mark a lemma `[simp]` if its left-hand side itself simplifies further by existing simp lemmas. Restate the lemma in the form `simp` actually sees instead of suppressing the `simpNF` linter.

108. Avoid simp loops and expanding rewrites

Do not add `[simp]` lemmas that rewrite back and forth, recreate their own left-hand side, or make expressions larger. In particular, avoid non-affine rewrites where variables occur more often on the RHS than on the LHS.

109. Use explicit arguments when inference is fragile

If `simp` or `rw` fails because implicit parameters, typeclass arguments, or specialization are not inferred well, specify the important arguments explicitly.
```lean
simp [lemma (a := x)]
rw [@one_mul α _]
```

110. Avoid `simp_all` unless necessary

`simp_all` is aggressive and rewrites the whole context. Prefer targeted `simp at h ⊢` or `simp only [...]` unless you genuinely need hypotheses and goal to simplify each other.

111. Unfold only enough to expose the right rewrite

If `simp` does not fire because the target is hidden behind a reducible definition or partial application, first `dsimp` or unfold just enough to expose the pattern, then simplify. Avoid unnecessary unfolding.

112. Add small reusable simp lemmas instead of repeating local rewrites

If many proofs need the same tiny rewrite, add the corresponding simp lemma near the definition rather than repeatedly introducing local helper facts.

113. Use `@[reassoc (attr := simp)]` for categorical composition lemmas

For category-theoretic lemmas meant to rewrite under composition, use `@[reassoc (attr := simp)]` so both the original and reassociated forms are available to `simp`.

114. Use `@[simps!]` when stronger unfolding is needed

If ordinary `@[simps]` does not see through the definition enough to generate useful lemmas, use `@[simps!]`, especially for non-constructor bodies or type synonyms.

115. Treat `simpNF` linter failures as real issues

If the `simpNF` linter reports a problem, fix the lemma statement or attribute rather than silencing it with `nolint simpNF`, except as a documented last resort.

116. Avoid `erw`

Do not use `erw`. If `rw` fails, normalize with `dsimp`, `change`, or `simp only`, or add the proper API lemma so ordinary rewriting works.

117. Keep `dsimp` targeted

Prefer `dsimp only [...]` or `dsimp at h` over broad `dsimp at *`. Uncontrolled definitional unfolding is noisy, fragile, and often makes goals larger.

118. Do not expose implementation details in simp normal forms

Simp should rewrite toward the public API, not toward internal fields, recursors, `.1`/`.2`, or low-level representations. Avoid simp lemmas that break abstraction barriers.

119. Provide both forward and inverse simp lemmas for equivalences when canonical

For `Equiv`, `MulEquiv`, isomorphisms, and similar objects intended for rewriting, provide simp lemmas for both directions when both are canonical and non-looping.
```lean
@[simp] theorem e_apply_symm_apply ...
@[simp] theorem e_symm_apply_apply ...
```

120. Use dedicated automation for function properties

For continuity, measurability, and similar goals, use the dedicated automation such as `fun_prop` and measurability tactics, and tag supporting lemmas with the appropriate attributes rather than trying to solve everything with `simp`.

121. Keep simp attributes consistent across related lemmas

If one lemma in a natural family is `[simp]`, analogous variants usually should be too—or none should be. Inconsistent simp tagging across parallel APIs is confusing.

122. Use local simp attributes for narrowly useful rules

If a simp rule is useful only in one proof, section, or file, use `attribute [local simp] ...` or `@[scoped simp]` rather than making it global.

123. Do not use `simp` as a substitute for arithmetic automation

Use `norm_num`, `omega`, `linarith`, `positivity`, `ring`, `ring_nf`, `field_simp`, and similar tactics for numeric or algebraic side conditions. Let `simp` expose the arithmetic structure, then use the dedicated tactic.

124. Pass local hypotheses explicitly to `simp`

If simplification depends on local facts, include them explicitly with `simp [h]`, `simp only [h]`, or `simp [h] at hx ⊢`. Do not rely on `simp` to guess the right local hypothesis.

125. Do not tag definitions themselves with `@[simp]`

Put `@[simp]` on lemmas about a definition, not on the `def` or `abbrev` itself, unless global unfolding is truly intended. For structures and maps, prefer `@[simps]` or `@[simps!]` to generate projection lemmas.

126. Rewrite hypotheses and goals precisely

When the same rewrite should apply to a hypothesis and the goal, write `simp only [...] at h ⊢` or `rw [...] at h ⊢`. Avoid `at *`, which may rewrite unrelated hypotheses.

127. Prefer `dsimp` for pure definitional reduction

Use `dsimp`/`dsimp only` when you only need definitional unfolding such as beta, zeta, iota, or projection reduction. Use `simp` when you want rewriting by simp lemmas.

128. Use `to_additive` with simp attributes explicitly

When a lemma’s simp behavior should transfer to its additive version, use the supported form
```lean
@[to_additive (attr := simp)]
```
and verify that the generated declaration gets the intended attributes.

129. Configure simps projections after coercion setup

For custom structures, register the intended projections with `initialize_simps_projections` after the relevant `FunLike`/`CoeFun` instance is in place, so generated lemmas use the right names and shapes.
```lean
initialize_simps_projections MyStruct (toFun → apply)
```

130. Prove definitional equalities by `rfl`

If a lemma is definitionally true, write it as `:= rfl` rather than `by simp` or usually even `by rfl`. This makes the lemma usable by `dsimp` and clearly signals definitional equality.

131. Do not make algebraic rearrangement lemmas global simp rules

Do not mark commutativity, associativity, distributivity, or similar rearrangement lemmas as global `[simp]`. Use them explicitly with `rw`, `simp_rw`, or local `simp only [...]` when needed.

132. Disable problematic simp rules locally

If a generally good simp lemma is undesirable in one proof, remove it locally with `simp [-lemma]` or local attribute changes. Do not weaken the global simp set for an isolated case.

133. Remove redundant simplification

Delete `simp`, `simp only`, `rw`, or `dsimp` calls that do not materially change the proof state, including rewrites that merely repeat what a previous `simp` already did.

134. Use `@[norm_cast]` only for genuine cast-normalization lemmas

Add `@[norm_cast]` only to lemmas that normalize casts, with an explicit coercion on the left-hand side. Prefer the `norm_cast`/`push_cast`/`pull_cast` framework over ad hoc simp lemmas for coercions.

135. Prefer a new simp-normal-form copy over forcing a bad statement

If an existing theorem has a useful noncanonical statement, keep it, and add a separate simp-normal-form version tagged `@[simp]`. Do not force a noncanonical theorem into the simp set.

136. Use `simp_rw` for repeated or under-binder rewriting

Use `simp_rw [...]` when you need repeated directed rewriting, especially under binders or throughout a term. Prefer it over repeated `rw` for rewrites inside `∀`, `∃`, `iSup`, and similar expressions.

137. Prefer `rfl` for trivial definitional goals

When the goal is exactly a definitional equality, use `rfl` rather than a gratuitous `simp`, unless you are intentionally proving a simp lemma.

138. Register coercions properly for cast tools

If `norm_cast` or related tools must detect a coercion after unfolding, ensure the coercion is registered appropriately so cast normalization can see it.

139. Use `rw` for a single targeted rewrite

If you want one specific rewrite in one place, use `rw`/`rw [...] at h` rather than `simp only [...]`. Reserve `simp` for simplification, not one-off rewriting.

140. Add simp-friendly membership and predicate characterization lemmas

For new predicates and set-like constructions, provide canonical lemmas of the form `x ∈ S ↔ P x` or `foo x ↔ ...`, and mark them `[simp]` when they are the standard way to reason about the predicate.

141. Simplify before arithmetic normalization

Run targeted `simp` first to rewrite definitions and obvious identities, then call `ring_nf`, `norm_num`, `field_simp`, `linarith`, or similar tactics. This keeps arithmetic automation focused on actual arithmetic.

142. Avoid coercion simp lemmas that recurse or fight cast normalization

A coercion simp lemma should strictly simplify and should not reintroduce the same coercion pattern on the RHS. Also avoid simp lemmas that conflict with `norm_cast`, `push_cast`, or `pull_cast`.

143. Use contextual `simp` deliberately

When simplification must use hypotheses introduced inside the goal, enable contextual simplification explicitly with `simp +contextual`, `simp [*]`, or the corresponding config. Do not rely on contextual rewriting by accident.

144. Prefer the strongest general lemma as the simp lemma

When several versions of a result exist, put `[simp]` or related automation attributes on the most general useful version rather than on weaker special cases.

145. Use `FunLike` coercions as the canonical form

For morphism-like structures, use the standard `FunLike`/`CoeFun` machinery so elaborated terms have stable heads and existing simp lemmas apply uniformly.

146. Prefer `iff` lemmas for rewrite-friendly logical characterizations

When a result is meant to be used by rewriting, state it as an `↔` rather than a one-way implication. This makes it usable by both `rw` and `simp`.

147. Combine adjacent simplification steps

Merge consecutive `simp`, `simp only`, `rw`, or `dsimp` steps on the same goal when one call can do the job. Repeated tiny cleanup steps add noise and are harder to maintain.

148. Use `@[reassoc]` without `simp` when only reassociation is wanted

If a categorical lemma should support reassociation rewriting but should not be a global simp rule, use `@[reassoc]` alone.

149. Add `@[ext]` lemmas for structures commonly proved equal by components

If equality proofs repeatedly reduce to equality of underlying data, provide an extensionality lemma so users can write `ext; simp` instead of manual field-by-field proofs.

150. Give simp lemmas a stable constant head

The left-hand side of a simp lemma should have a stable constant head so the simplifier can index it effectively. Avoid variable-headed, lambda-headed, metavariable-headed, or overly broad patterns.

151. Prefer `ext; simp` for equality of maps and structures

When proving equality of morphisms, linear maps, natural transformations, and similar objects, prefer extensionality followed by simplification when the simp API supports it.

152. Avoid overlapping or competing simp lemmas

If two simp lemmas cover essentially the same pattern and one subsumes the other, keep only the stronger or more general one as `[simp]`. Competing simp lemmas make behavior less predictable and can hurt performance.

153. Provide evaluation and coercion simp lemmas for function-like objects

For maps, homs, embeddings, equivalences, and wrappers, add the evaluation lemmas users actually need, typically `foo_apply`, `map_apply`, `hom_apply`, or coercion lemmas.
```lean
@[simp] theorem coe_mk : ⇑(mk f h) = f := rfl
@[simp] theorem map_apply (x) : map f x = ... := rfl
```

154. Use `field_simp` only in its proper role

Use `field_simp` to clear denominators in expressions involving division or inverses, typically near the end of a proof and often followed by `ring`. Do not treat `field_simp` as a general replacement for `simp`.

155. Keep simp lemmas compatible with `field_simp`

Do not add global simp lemmas that interfere with denominator normalization or the side conditions generated by `field_simp`. Rewrite hypotheses into the forms `field_simp` expects before using it.

156. Be conservative about changing the global simp set

Do not add or remove global simp attributes casually, especially in unrelated refactors or ports. Changes to global simp behavior should be deliberate, justified, and reviewed carefully.

157. Avoid redundant evaluation simp lemmas

Do not add extra `_apply_apply`-style simp lemmas if they are already derivable from a simpler `_apply` lemma. Keep the simp API minimal.

158. Do not make broad functor equalities global simp lemmas

Avoid putting equalities of functors into the global simp set. Prefer object-level or morphism-level simp lemmas, or use isomorphism-based APIs instead.

159. Prefer canonical notation and normal forms in statements

Write lemmas using standard Mathlib forms, such as `<`/`≤` instead of `>`/`≥`, and other canonical spellings that match existing simp lemmas. This improves rewriting and reduces duplicate API.

160. Formulate propositional and boolean simp lemmas in direct rewrite form

For propositions, prefer `P ↔ True`, `P ↔ False`, or other direct `iff` forms rather than `P = True`. For booleans, use canonical boolean or logical forms rather than burying `b = true` or `b = false` inside larger patterns.

161. Use `simp?` and tracing to debug `simp`

If a `simp` call is fragile, slow, or surprising, run `simp?` to discover a good lemma list, and use tracing when needed to inspect fired rewrites.
```lean
set_option trace.Meta.Tactic.simp.rewrite true
```
Replace exploratory calls with explicit `simp only [...]` once you know what is needed.

162. Use public coercion syntax in simp lemmas

State coercion and evaluation lemmas using public syntax such as `⇑f` and `(x : α)`, not internal fields like `toFun` or `.1`, unless those are the stable public API.

163. Use `simp [h]` after `by_cases`

After `by_cases h : P`, simplify branch goals with `simp [h]`. Avoid unnecessary extra cleanup such as `simp at h` unless it is actually needed.

164. Match simp lemmas to the expression shape users actually see

State simp lemmas in the fully applied form that appears in goals, especially for projections and coercions. If simplification fails on an application shape, add a lemma for that exact shape.
```lean
@[simp] theorem Equiv.refl_apply (a : α) : Equiv.refl α a = a := rfl
```

165. Use `.not` on existing iff lemmas for negated rewrites

When rewriting a negated equivalence, prefer the `.not` form of an existing `iff` lemma rather than introducing separate `not_*` lemmas or manual `push_neg` boilerplate.

166. Use `subst` for variable substitution

When you have an equality of the form `x = t` or `t = x` and want to replace a variable everywhere, prefer `subst x` over forcing `simp` or repeated `rw`.

167. Do not use implications as simp rules

Simp works best with equalities and `iff` lemmas. Do not try to use plain implications as simp rules.

168. Avoid broad `simp` steps in `calc` blocks

In `calc` proofs, prefer `rw`, `ring`, or another precise justification over a broad `simp` step. If `simp` is necessary, use `simp only [...]` to keep the step robust.

# tactic usage

169. Keep automation focused and curated

When using tactics like `grind` or `apply_rules`, supply only the lemmas they actually need, for example with `only [...]`. Do not stack heavy tactics as a catch-all.

170. Prefer `refine` for partial constructions and controlled subgoals

Use `refine` when you want to build part of a term now and leave explicit holes for later. Prefer `?_` placeholders for goal-generating holes, not `_`.
```lean
refine ⟨x, hx, ?_⟩
```

171. Use controlled simplification when stability matters

Use `simp only [...]` or `dsimp only [...]` when you want a specific simplification set or controlled definitional unfolding. Avoid broad nonterminal `simp` calls that obscure which lemmas are doing the work.

172. Use explicit or named arguments when inference is brittle

When applying lemmas with many arguments or ambiguous implicits, provide explicit or named arguments to stabilize elaboration and avoid dependence on argument order.
```lean
rw [lemma_name (j := j) (j' := j')]
```

173. Close solved goals with `exact`

Use `exact` when you already have a term of the goal type. Do not use `apply` or `refine` as stylistic substitutes when no subgoals are intended.

174. Keep tactic layout readable

Prefer one tactic per line unless the whole proof is a short one-liner. Lean tactic blocks are indentation-sensitive, so preserve clear nesting and grouping.

175. Prefer short term-style proofs over tactic blocks

If a proof is naturally a single term, write it directly instead of opening tactic mode. Avoid wrappers like `by exact` or `by apply`.
```lean
def foo : ∃ x, p x := ⟨x, hx⟩
```

176. Keep rewriting and simplification local and goal-directed

Rewrite only the subexpressions you need, when you need them. Avoid large premature rewrites of the goal or hypotheses that make later steps harder to understand.

177. Combine consecutive rewrites

When several rewrites happen in the same proof state, combine them into one `rw [...]` call. This reduces noise and makes the proof easier to read.

178. Add automation attributes deliberately

Tag lemmas with attributes such as `@[simp]`, `@[ext]`, `@[gcongr]`, `@[fun_prop]`, `@[mono]`, `@[norm_cast]`, `@[aesop]`, or `@[grind]` only when they are genuinely intended for that automation. Avoid tags that create loops, ambiguity, or performance regressions.

179. Reuse existing tactic infrastructure in metaprograms

Before adding a new tactic, check whether core Lean or Mathlib already provides the needed behavior. Prefer thin wrappers around existing tactics and APIs over duplicating logic.

180. Use tracing and inspection tools for debugging, not final code

When debugging tactics or inference, use tracing options, simp traces, definitional-equality traces, profiler output, or `show_term` rather than guessing. Remove debugging options and scaffolding from committed code.

181. Prefer `simpa` when simplification closes the goal

Use `simpa` or `simpa using h` when a hypothesis or lemma solves the goal up to simplification. Do not use `simpa` if no simplification is actually needed.

182. Prefer automation-friendly API lemmas over repeated unfolding

If a proof pattern recurs, add a dedicated simp lemma, ext lemma, congruence lemma, or other API lemma instead of repeatedly unfolding definitions by hand.

183. Prefer `let` for data and `have` for propositions

Use `let` for non-`Prop` local definitions and `have` for local facts. Use `letI` or `haveI` only when introducing local instances for typeclass inference.

184. Prefer the right normalization tactic for the domain

Use specialized tactics such as `ring`, `ring_nf`, `abel`, `field_simp`, `field`, `linarith`, `nlinarith`, `norm_num`, `norm_cast`, `mod_cast`, `push_cast`, `lift`, `zify`, `qify`, or `linear_combination` when they match the goal. Do not replace a clean specialized proof with broad automation.

185. Avoid repeated expensive elaboration or inference in tactic code

Do not repeatedly elaborate the same syntax or synthesize the same instances inside loops. Cache results and provide explicit arguments when inference is slow or ambiguous.

186. Prefer the canonical Lean 4 / Mathlib tactic

Use the standard, non-legacy tactic or syntax for the job. Avoid deprecated or duplicate variants such as `cases'`, `induction'`, `split`, `existsi`, `refine'`, or `native_decide` unless there is a specific technical reason.

187. Use `erw` only as a last resort

Prefer `rw`, possibly after `dsimp` or `change`. Reach for `erw` only when ordinary rewriting fails because of transparency or definitional-equality issues.

188. Prefer `obtain` for forward witness extraction in a single goal

When destructuring an existential or structured hypothesis without branching into multiple goals, prefer `obtain`. Use `rcases` more for genuine case splits.

189. Use `gcongr` for monotonicity-style relational goals

For inequalities and similar goals that follow from monotonicity or generalized congruence, prefer `gcongr` over manual monotonicity lemmas. Tag supporting lemmas with `@[gcongr]` when appropriate.

190. Use `rintro` to combine introduction and destructuring

When you immediately destruct introduced hypotheses, use `rintro` instead of `intro` followed by `rcases` or `cases`.

191. Keep one active goal at a time when possible

Structure proofs so side goals are handled promptly and locally instead of letting many unrelated goals accumulate.

192. Use goal combinators and subgoal blocks only when they clarify structure

Use `case` blocks for named goals and `<;>` only for genuinely uniform follow-up across all branches. Avoid `swap`, broad `all_goals`, or anonymous focus syntax when they make proof structure less explicit.

193. Avoid `convert` unless it clearly simplifies reuse

Prefer direct rewriting or `simpa using` over `convert`. If `convert` is genuinely the clearest tool, use `convert ... using n` to control matching depth.
```lean
convert h using 2 <;> simp
```

194. Avoid `unfold` in proofs when API lemmas suffice

Prefer public rewrite lemmas, `rw`, `simp`, or `dsimp` over `unfold`. Use definitional unfolding only in a controlled way when no suitable API exists.

195. Prefer local `classical` and narrowly scoped options

When classical reasoning or special options are needed, introduce them locally rather than globally. Use `classical`, `set_option ... in`, and local attributes only where needed.

196. Prefer `induction` over legacy induction variants

In Lean 4 / Mathlib code, use `induction`, not `induction'`. Prefer structured `induction ... with | ... => ...` syntax and `case` blocks.

197. Prefer compact constructor and existential syntax

When building conjunctions, existentials, or structures, use `⟨..., ...⟩`, `use`, or `refine ⟨..., ?_⟩` rather than `constructor`/`existsi` boilerplate. Use `constructor` for constructor goals, not legacy `split`.

198. Prefer structured destructuring tactics

Use `rcases`, `obtain`, and `rintro` to unpack `∃`, `∧`, `∨`, sigma types, and constructor arguments. Avoid manual `cases` chains when structured destructuring is clearer.

199. Replace search tactics with explicit final code

Tactics such as `exact?`, `apply?`, and `simp?` are for discovery, not committed proof scripts. Replace them with the concrete lemma application or explicit simplification set they suggest.

200. Prefer `fun_prop` for routine function-property goals

When the goal is continuity, measurability, differentiability, or a similar tagged function property, use `fun_prop`. Tag intended lemmas with `@[fun_prop]`.

201. Use `lia` for linear arithmetic over `Nat` and `Int`

For linear arithmetic over naturals and integers, prefer `lia`. Use other arithmetic tactics only when the domain or goal shape calls for them.

202. Prefer `filter_upwards` for `∀ᶠ` and filter reasoning

For `Eventually` goals and hypotheses, use `filter_upwards` rather than unpacking filter definitions manually. If a direct `.mono` proof suffices, that is also fine.
```lean
filter_upwards [h₁, h₂] with x hx₁ hx₂
```

203. Tactic implementations should make real progress and preserve goals correctly

Do not let a tactic report success while leaving the proof state unchanged. Manage the goal list explicitly and do not accidentally drop trailing goals; use APIs such as `replaceMainGoal` when appropriate.

204. Use `apply` only for backward reasoning that should create subgoals

Use `apply` when the goal matches the conclusion of a lemma and you want its premises as new goals. Do not use `apply` as a generic replacement for `exact`.

205. Use `norm_num` for concrete numerical goals

When the goal is straightforward arithmetic with concrete numerals, prefer `norm_num`. Use `by decide` only after simplification has reduced the goal to a small decidable proposition.

206. Avoid `change` unless definitional reshaping is genuinely the point

Do not use `change` as routine goal massaging. Prefer `rw`, `simp`, `simpa`, or a better-targeted lemma unless you specifically need a definitionally equal target.

207. Use `#guard_msgs` and related tools for tactic tests

When testing tactics, elaborators, warnings, or expected failures, use `#guard_msgs`, `fail_if_success`, and similar tools rather than unchecked comments or informal examples.

208. Prefer specialized automation over broad automation

When a specialized tactic matches the domain, use it instead of broad search tactics like `aesop`, `grind`, `library_search`, `exact?`, or `apply?`. Specialized automation is usually clearer, faster, and more stable.

209. Use heavy automation sparingly and usually terminally

Avoid search tactics when a short direct proof is clearer. If you use them, prefer terminal use or tightly controlled rule sets/configuration.

210. Prefer `by_cases!`, `by_contra!`, and `contrapose!` when pushing negations helps

Use the `!` variants when you want negations pushed automatically through hypotheses or goals. For ordinary proposition splits, use `by_cases h : P`.

211. In meta code, manage context and reduction explicitly

Use `withMainContext` when interacting with the local context, but do not confuse it with goal focusing. Normalize expressions with `whnf`/`whnfR`/`whnfD` before shape-based inspection when reduction is relevant.

212. Prefer `ext` for extensionality goals

When proving equality of functions, sets, or other extensional objects, use `ext` to reduce to pointwise goals. Name variables explicitly when helpful, and use depth bounds like `ext : 1` if needed.

213. Use `ring` and `abel` near the end of normalization proofs

Use `ring`/`ring_nf` for polynomial identities and `abel`/`abel_nf` for additive commutative-group normalization, after the expression is in the right form. Do not use them as early catch-all steps.

214. Keep theorem statements and local contexts minimal

Do not introduce unnecessary variables, hypotheses, or local instances. Extra context makes elaboration, automation, and case splits harder to control.

215. In metaprograms, prefer macros for syntax sugar and `MetaM` for real logic

If custom syntax is only a wrapper around existing syntax, implement it with `macro_rules`. Put substantive proof-search or transformation logic in `MetaM` over `MVarId`s, and keep `TacticM` as a thin interactive wrapper.

216. Prefer dedicated quotient, closure, or domain-specific induction principles

For quotients, closures, or other generated predicates, use the dedicated induction or elimination principles provided by the API rather than generic `cases`.

217. Use `positivity` for positivity and nonnegativity side goals

When the goal is of the form `0 ≤ _` or `0 < _`, especially after `gcongr` or algebraic preprocessing, try `positivity` first.

218. Prefer `inferInstance` or `inferInstanceAs` over manual instance construction

If typeclass inference can synthesize the instance, let it do so. Use `inferInstanceAs` when you want to specify the target type explicitly.

219. Prefer `rfl` for definitional equalities

If the goal is definitionally true, close it with `rfl` rather than heavier automation. Also use `rfl` patterns in destructuring when they eliminate equalities immediately.

220. Prefer `congr!` for congruence-style subexpression changes

Use `congr!` to rewrite inside larger expressions or strip matching outer structure. Use plain `congr` only when you specifically need it.

221. Prefer `obtain rfl | h := eq_or_ne ...` for equality splits

When splitting on whether a term equals a distinguished value, use `obtain rfl | h := eq_or_ne ...` so the `rfl` branch rewrites automatically.

222. Prefer `decide` or `by decide` over `native_decide`

In Mathlib, use `decide` or `by decide` for decidable goals. Do not commit `native_decide` proofs.

223. Use `conv` only for genuinely targeted rewriting

If ordinary rewriting is insufficient, use `conv` to target a specific occurrence or position. Make the target occurrence unambiguous rather than using `conv` as a routine rewrite tool.

224. Use `field_simp` or `field` only when denominators are the issue

Use `field_simp` as preprocessing to clear denominators once the goal is in the right shape, and provide the needed nonzero side conditions explicitly. Do not expect `field_simp` or `field` to solve the whole proof.

225. Use cast-normalization tactics for coercion cleanup

When casts between numeric types are the main obstacle, use `norm_cast`, `mod_cast`, or `push_cast` rather than manual rewriting.

226. Avoid unnecessary explicit instance arguments

Do not thread named instance arguments through proofs unless needed for disambiguation, performance, or elaboration stability.

227. Use `rwa` only when the combined rewrite-and-close step is clearly better

If a rewrite immediately turns the goal or hypothesis into something solved, `rwa` can be concise. Otherwise prefer explicit `rw`/`simp` plus `exact` or `assumption`.

228. Prefer `calc` for readable chains

When a proof is naturally a chain of equalities or inequalities, use `calc` rather than repeated transitivity lemmas or a long tactic script.
```lean
calc
  a = b := by rw [h]
  _ ≤ c := hc
```

229. Use `generalizing` or specialized induction principles when needed

If the induction hypothesis must apply to extra variables, use `generalizing` rather than revert/reintroduce boilerplate. If there is a natural specialized induction principle, use `induction ... using ...`.

230. Use `subst` or `obtain rfl` for variable equalities

When an equality identifies a variable with a term, rewrite it away globally with `subst` or `obtain rfl := h` rather than carrying the equality around.

231. Prefer `choose` for uniform existential witnesses

When a hypothesis has the form `∀ x, ∃ y, P x y`, use `choose` instead of manually chaining `Exists.choose`.

232. Use `wlog` only for genuine without-loss-of-generality arguments

Use `wlog` or `wlog!` only when one case truly reduces to another by symmetry or normalization. For independent branches, use `by_cases` instead.

233. Use `simp_rw` for repeated rewriting or rewriting under binders

Prefer `simp_rw` when the same rewrite should happen repeatedly or inside binders, lambdas, or quantifiers. It is often clearer and more robust than many repeated `rw` calls.

234. Use `split_ifs` for `if`-expressions

When the proof naturally splits on an `if`, use `split_ifs with h` and solve each branch with the resulting hypotheses.

235. Prefer `cases` over `induction` when no induction hypothesis is needed

If you only need constructor splitting and no recursive hypothesis, use `cases`, not `induction`.

236. Use `nontriviality` for `Nontrivial` assumptions

When a proof needs `[Nontrivial α]`, use `nontriviality α` early rather than manually constructing the instance. Tag supporting lemmas with `@[nontriviality]` when appropriate.

237. Prefer existing filter, asymptotic, and domain combinators over rebuilding proofs

For notions such as `Tendsto`, `IsBigO`, `IsTheta`, and similar APIs, use the library combinators and standard lemmas rather than reproving the underlying machinery from scratch.

238. Prefer direct application of hypotheses and iff projections

If you need `H x hx`, write that directly rather than `specialize H x hx`. For `↔` lemmas, use `.mp` and `.mpr` when they make the proof shorter and clearer.

239. Use dedicated domain tactics where they are standard

For specialized domains, prefer the tactics that encode the standard workflow, such as `cat_disch`, `aesop_cat`, `tfae_have`, `tfae_finish`, `coherence`, `monoidal`, `fin_cases`, or `interval_cases`, when they fit the goal.

240. Prefer `@[simps]` and `simps` for projection lemmas

When defining structures, equivalences, or morphisms, use `@[simps]` or related projection-generation support rather than hand-writing routine projection lemmas, unless the generated lemmas are unsuitable.

241. Prefer `apply_fun` for transporting equalities through functions

When you want to apply a function to both sides of an equality or equality hypothesis, use `apply_fun`. This is clearer than manually invoking congruence lemmas.

242. Prefer direct projections when destructuring is unnecessary

If you only need fields like `h.1` and `h.2`, use them directly instead of destructuring the whole hypothesis.

243. Preserve source positions and good error messages in macros

Macro expansions should keep errors pointing at the relevant user syntax. Do not obscure failures by losing source locations during expansion.

244. Prefer `let` over `set` unless you need the defining equation

Use `let` for a local abbreviation when you do not need an equation in the context. Use `set x := expr with hx` only when the equation `hx` will be used later.

# code style

245. Make inferable arguments implicit and non-inferable ones explicit

Use implicit binders `{...}` for parameters Lean can reliably infer from explicit arguments or the goal. Keep central or non-inferable parameters explicit, and when specifying implicits manually, prefer named arguments like `(R := R)` over `@foo _ _ _`.

246. Reuse surrounding binders, but keep declaration signatures explicit

Do not redeclare parameters or typeclass assumptions already in scope, and factor shared binders into a local `variable` block or `section` when several nearby declarations use them. Still write each declaration with the binders you want it to depend on; do not rely on ambient variables leaking in implicitly.

247. Keep top-level layout and indentation standard

Start top-level commands at column 0. Indent proof bodies by 2 spaces and wrapped declarations or continuations in standard Mathlib style.

248. Open namespaces and scopes sparingly

Keep `open`, `open scoped`, and local notation as narrow as practical. Prefer qualified names or `open ... in` when that avoids file-wide namespace pollution.

249. Use dot notation when it improves readability

Prefer forms like `h.symm`, `x.foo`, or `f.comp g` when they make code shorter and clearer. Avoid dot notation when name resolution becomes ambiguous or fragile.

250. Use standard spacing and avoid manual alignment

Write `x : α`, `a + b`, `rw [h₁, h₂]`, and similar standard spacing. Do not align columns with extra spaces; use ordinary indentation so diffs stay stable.

251. Parenthesize only when helpful

Remove unnecessary parentheses around simple expressions, but add them whenever precedence or parsing could be unclear, especially with custom notation, coercions, arrows, or unary operators.

252. Keep contexts minimal

Remove unused parameters, hypotheses, universes, local `have`/`let` bindings, and obsolete helpers. If a binder is intentionally unused, write `_` or a clearly unused name like `_h`.

253. Reuse existing Mathlib APIs and notation

Do not reimplement standard lemmas, wrappers, encodings, or notation that already exist in Mathlib/Core. Prefer canonical forms such as `x ∈ s`, `∅`, `Set.univ`, `a * b`, `n + 1`, and standard bundled structures.

254. Put parameters and hypotheses in binder form before the colon

Prefer declaration headers like `lemma foo (x : α) (h : P x) : Q x := ...` rather than encoding assumptions with a leading `∀` or trailing implications when ordinary binder syntax works better.

255. Use conventional Mathlib names

Choose standard names such as `α β`, `R`, `G`, `x y`, `s t`, `i j`, and hypothesis names like `h`, `h₁`, `h₂`. Match nearby files’ naming and argument conventions rather than inventing a new local style.

256. Inline one-use helpers; name repeated nontrivial expressions

If a short local helper is used only once, inline it. If a nontrivial expression or fact is used several times, give it a local name and reuse it consistently.

257. Do not use broad option hacks to force proofs through

Do not use escapes like `set_option maxHeartbeats 0` to bypass performance problems. If an option change is unavoidable, keep it local, conservative, and justified.

258. Localize options and lint suppressions

Use `set_option ... in` and other suppressions on the smallest possible region. Fix the underlying issue rather than disabling linters or adding `@[nolint]` unless the exception is deliberate and justified.

259. Prefer `fun x ↦ ...` for lambdas

In Mathlib code, write lambda expressions with `↦`. Reserve `=>` for match arms and other standard syntax roles.
```lean
def f : ℕ → ℕ := fun x ↦ x + 1
```

260. Do not abuse definitional equality or implementation details

Do not rely on fragile defeq coincidences between wrappers, coercions, or structures, and do not use low-level projections or fields when the intended API provides named lemmas or notation. Prefer extensionality lemmas, membership notation, and named projections over implementation-specific details.

261. Drop redundant namespace qualifiers

If a namespace is already open or you are already inside it, omit unnecessary qualification. Keep qualification only when it helps disambiguate.

262. Keep `autoImplicit` off and declare variables explicitly

Do not rely on undeclared implicit variables. Mathlib convention is to declare all variables explicitly.

263. Use `let` for data, `have` for propositions, and `letI`/`haveI` for instances

Keep the distinction between data, facts, and instances clear. Use `let` for values, `have` for propositions, and `letI` or `haveI` only for local instances.

264. Keep `:=`, `by`, and infix operators at the end of the previous line

Do not start a new line with `:`, `:=`, `by`, or infix operators such as `=`, `+`, `*`, `≫`, or `∘`. Break lines so these tokens stay attached to the preceding line.

265. Scope `noncomputable` and classical reasoning locally

If code is noncomputable, mark only the relevant declaration or use `noncomputable section` only when many nearby declarations need it. Prefer `classical`, `by classical`, or `open scoped Classical in` over global `open Classical`.

266. Use `def`, `lemma`, `theorem`, `abbrev`, and `instance` appropriately

Use `def` for data, `lemma`/`theorem` for propositions, and `instance` for typeclass instances rather than `@[instance] theorem`. Use `abbrev` only for transparent aliases that should remain reducible.

267. Use standard coercion notation and avoid unnecessary coercions

When an explicit coercion is needed, write `↑x` or `⇑f`, not raw coercion constants. Omit explicit coercions when Lean can insert them unambiguously, but add them when the intended type would otherwise be unclear.

268. Name intermediate facts explicitly

Give meaningful names to important `have`, `obtain`, and similar intermediate results rather than relying on `this` or autogenerated names.

269. Avoid unnecessary `@` applications and underscore-heavy argument lists

Let Lean infer implicit arguments when it can. If you must specify them, prefer named arguments over `@foo _ _ _`.

270. Follow the surrounding file’s conventions

Match the local file’s established naming, notation, formatting, binder style, and proof style unless there is a clear reason not to. Do not make unrelated style-only rewrites in the same PR.

271. Use `where` blocks and named fields for structures and instances

Prefer `where` syntax and named fields over anonymous constructors or positional structure syntax, especially for multi-field structures.
```lean
instance : Foo α where
  bar := ...
  baz := ...
```

272. Avoid shadowing local names

Do not reuse an existing name for a different object in a nested scope unless there is a compelling reason. Use descriptive fresh names for intermediate facts and variables.

273. Use standard mathematical notation and statement forms

Prefer canonical forms such as `x ∈ s`, `s ⊆ t`, `{x | P x}`, `∀ x ∈ s, ...`, `∃ x ∈ s, ...`, `S.Nonempty`, `∑ x ∈ s, ...`, and `∃! x, ...`. State lemmas in the standard orientation and shape that Mathlib users expect.

274. Mark file-local implementation helpers `private`

Use `private` for helper lemmas and definitions that are not intended as part of the public API. Do not simulate privacy with leading underscores.

275. Order binders in standard Mathlib order

List type parameters first, then typeclass assumptions, then term arguments, then hypotheses. Keep dependent arguments after the data they depend on, and preserve established argument order unless there is a real API reason to change it.

276. Prefer `Type*` unless explicit universe control is needed

Write `Type*` rather than `Type _` or explicit universe parameters unless the declaration genuinely needs precise universe management.

277. Format `by` blocks and short proofs idiomatically

Use one-line proofs like `by rfl` or `by simp` when they are genuinely tiny. For nontrivial proofs, use a structured multiline `by` block rather than dense semicolon chains.

278. Break long declarations at logical boundaries

Keep short declarations on one line when they remain readable. For longer ones, break after binders or before the conclusion in a way that keeps the statement easy to scan.

279. Use `_root_` or `nonrec` only to avoid real shadowing problems

Do not write `_root_.foo` unnecessarily, but do use `_root_` or `nonrec` when needed to refer to an existing declaration rather than a shadowing local one.
```lean
nonrec def min (a b : ℕ) : ℕ := _root_.min a b
```

280. Use `alias` for pure renamings and standard deprecation attributes

If a declaration is only another name for an existing theorem, use `alias` rather than restating or reproving it. When deprecating names, use the standard `@[deprecated (since := "...")]` form.

281. Use one blank line between top-level declarations

Separate consecutive top-level declarations with a single blank line. Avoid both cramped formatting and multiple blank lines.

282. Keep definitions computable when possible

Do not mark declarations `noncomputable` unless they genuinely require noncomputable machinery. Prefer constructive definitions when available.

283. Add type ascriptions for ambiguous numerals

If Lean may infer the wrong type for a numeral, add an explicit type ascription or cast.

284. For metaprogramming, keep syntax lightweight and implementation structured

Use hygienic syntax and structured APIs rather than string hacking or disabled hygiene. Keep macros lightweight, separate syntax frontends from implementation logic, and reuse shared helpers instead of duplicating elaboration code.

285. Remove dead code and duplicates

Delete commented-out code, obsolete declarations, duplicate lemmas, unreachable branches, and unnecessary alternate names unless there is a clear API reason to keep them.

286. Avoid `rename_i`; name binders directly

Treat `rename_i` as a code smell. Name variables explicitly in binders, `intro` patterns, `match`, `induction`, or `next =>` clauses instead.

287. Keep changed code lint-clean

New or modified code should pass the relevant linters. Do not leave avoidable warnings behind.

288. Use standard binder notation

Prefer ordinary binder notation such as `∀ x, P x` and `Π x, A x` over awkward arrow encodings like `(x : α) -> ...` when binders are clearer.

289. Write explicit binder types

Prefer binders like `{R : Type*}` over bare `{R}`. Explicit binder types make signatures easier to read and review.

290. Prefer term-style definitions and pattern matching for data

When defining data or simple functions, use direct term syntax and `match` rather than tactic-mode `by` blocks or low-level recursors when possible. Reserve tactic mode for proofs or genuinely awkward definitions.

291. Do not commit placeholders or non-source artifacts

Do not commit `sorry`, generated build artifacts, or environment-specific files unless they are intentionally part of the source tree.

292. Prefer `<|` and `|>` over `$`

Use `<|` for right-associative application and `|>` for pipelines. Avoid `$` in Mathlib code.

293. Omit names for typeclass binders unless needed

Write `[Ring R]`, not `[hR : Ring R]`, unless the instance name is used in the proof. This keeps signatures shorter and clearer.

294. Keep imports minimal but sufficient

Add all required imports, remove redundant ones when practical, and avoid broad imports just to obtain a few names or notations.

295. Keep code readable and maintainable

Prefer clear, direct code over clever parser tricks, heavy golfing, or fragile definitional-equality arguments. If two versions work, choose the one a future contributor can read and modify easily.

296. Prefer standard Unicode notation and identifiers

Use established Mathlib Unicode forms such as `↦`, `≤`, `∅`, `𝓝`, `𝕜`, and subscripts like `h₂` instead of ad hoc ASCII alternatives. Avoid decorative Unicode in identifiers when it is not standard mathematical notation.

297. Prefer `≤` and `<` over `≥` and `>`

State inequalities with the smaller term on the left when practical. This matches common Mathlib normal forms and rewrites better.

298. Prefer named projections over numeric projections

Write `.val`, `.prop`, `.fst`, `.snd`, or a structure field name instead of `.1`, `.2`, `.3` when possible. Named projections are clearer and more robust.

299. Give top-level `def`s explicit return types

Do not rely on inference for the result type of a top-level definition. Write the return type in the header.

300. Prefer `:= rfl` for definitional facts

If a declaration is definitionally true, write `:= rfl` rather than `:= by rfl`. This is shorter and keeps the definitional nature obvious.

301. Avoid `simp only` unless there is a reason

Do not replace ordinary terminal `simp` with `simp only` by default. Restrict the simp set only when maintainability, proof stability, or performance genuinely requires it.

302. Prefer direct terms over redundant wrapper syntax

If a proof or definition can be written cleanly as a direct term, do so instead of wrapping it in unnecessary `by exact ...`. Conversely, use `exact` inside tactic mode when it improves clarity.

303. Add useful standard attributes, and place them directly above the declaration

Use attributes such as `@[simp]`, `@[simps]`, `@[ext]`, and `@[to_additive]` when they provide standard automation or API support. Put attributes immediately above the declaration they modify.

304. Prefer direct syntax over verbose encodings

Use direct lambdas instead of `Function.const` when clearer, and use ordinary notation rather than low-level constants like `Nat.sub` or `Zero.zero` unless you specifically need them. Prefer `if`/`bif` over legacy `cond`.

305. Scope custom notation narrowly

Introduce custom notation only when it materially improves readability and is likely to be reused. Prefer `local notation`, `scoped notation`, or scoped infix declarations with explicit precedence, and avoid conflicts with existing syntax.

306. Use `where`, `termination_by`, and `decreasing_by` in standard layout

Indent `where` blocks consistently as part of the surrounding declaration, and keep `termination_by` and `decreasing_by` in the usual declaration layout. Do not use `where` when a simple direct term or record literal is clearer.

307. Keep lines within project limits

Break long lines rather than exceeding the repository’s line-length conventions, except for rare unavoidable cases such as URLs.

308. Use current Lean 4 / Mathlib syntax

Prefer idiomatic Lean 4 / Mathlib forms and avoid legacy Lean 3 or mathport-style syntax such as `begin ... end` or obsolete patterns when a standard Lean 4 form exists.

309. Reuse existing structure data when constructing structures

When building a structure from an existing one, use structure extension or record update syntax such as `..` or `{ r with field := ... }` instead of restating unchanged fields manually.

310. Keep simp lemmas canonical

State `@[simp]` lemmas in the standard notation and coercion shape users will actually rewrite with. Avoid odd statement forms that make `simp` less effective or harder to discover.

311. Prefer `Array` over `List` for indexed or performance-sensitive code

Use `Array` when you need efficient indexed access or predictable performance. Reserve `List` for naturally recursive, proof-oriented, or list-like code.

312. Prefer direct application over unnecessary rewriting

If an existing lemma already matches the goal, apply it directly with `exact`, `refine`, `.mp`, `.mpr`, or other standard projections instead of rewriting through equivalent formulations for no reason.

313. Use explicit field names and standard record update syntax

Construct structures with named fields and update records with `{ r with field := ... }` rather than positional constructors or rebuilding unchanged fields manually.

314. Do not contort public statements just to get an `rfl` proof

Use `rfl` when it is the natural proof, but do not expose implementation details or choose unnatural statement forms merely so the proof can be reflexive.

# naming

315. Prefer standard mathematical and Mathlib terminology

Choose names from standard mathematical usage and existing Mathlib vocabulary. Do not invent ad hoc synonyms, and avoid names that would be confused with major existing concepts, tactics, or operations.

316. Keep one concept one name, and keep naming families parallel

Use one canonical public name per concept, and mirror naming across analogous APIs and variants (`Set`, `Finset`, `List`, `LinearMap`, `RingHom`, left/right, additive/multiplicative, dual, `Within`/global, etc.). If one member of a family is renamed, rename the corresponding variants consistently.

317. Make the name accurately match the statement

A declaration name must reflect the actual direction, hypotheses, operations, and conclusion of the theorem. If the statement changes, rename the declaration accordingly.

318. Preserve upstream and core names unless there is a compelling reason not to

Do not rename Lean core or upstream identifiers just to match Mathlib style. If a better Mathlib-facing name is needed, add an alias and document the reason.

319. Use standard theorem-name patterns

Follow established templates such as `_iff`, `_of_`, `_inj`, `_injective`, `_surjective`, `_bijective`, `_mono`, `_antitone`, `_eq_`, `_left`, and `_right`. Do not invent new patterns when a standard one already exists.

320. Mention only essential hypotheses in theorem names

Include assumptions in the name only when they distinguish the lemma from nearby variants, such as `_of_isUnit`, `_of_surjective`, or `_of_finite`. Omit routine, ambient, or implied hypotheses.

321. Follow Mathlib casing conventions

Use `lowerCamelCase` for term-level definitions, projections, and bundled maps; `UpperCamelCase` for types, structures, classes, namespaces, and files; and `snake_case` for theorem and lemma names. Preserve established acronym casing exactly as Mathlib does (`FG`, `ULift`, `ENNReal`, `ZMod`, etc.).

322. Reuse existing canonical names

Before adding a declaration, check whether Mathlib already has the same concept or statement under an established name. Reuse that name instead of creating synonyms, near-duplicates, or parallel terminology.

323. Include the main operation or construction in the name

If a statement is fundamentally about `map`, `comp`, `preimage`, `smul`, `pow`, `derivWithin`, or a similar operation, that operation should usually appear in the name. Avoid names that hide the central object of the lemma.

324. Put declarations in the most relevant namespace

Place lemmas and definitions in the namespace where users will look for them and where dot notation reads naturally. Avoid root-level names unless the declaration is truly global.

325. Distinguish variants with descriptive suffixes, not primes

When there are several similar lemmas, use explicit qualifiers such as `_univ`, `_singleton`, `_zero`, `_within`, `_id`, `_fun`, or `_pi`. Use `'` only for a very close entrenched variant when a descriptive name would be worse.

326. Prefer concise, guessable, statement-driven names

Use the shortest conventional name that remains clear. A user should be able to plausibly guess the name from the statement, and the name should reflect mathematical content rather than implementation details.

327. Support dot notation with namespace and argument order

If a theorem or definition is naturally used as a method on a structure or hypothesis, put it in the corresponding namespace and make the receiver-like argument the first explicit argument.
```lean
namespace IsOpen
theorem preperfect (hU : IsOpen U) : ... := ...
end IsOpen
```

328. Use `_iff` only for actual `↔` lemmas

If the statement is an equivalence, use an `_iff` name; if it is not, do not. When useful, follow the `lhs_iff_rhs` pattern.

329. Use predicate-style names for Prop-valued declarations

Name `Prop`-valued definitions and classes as properties or predicates. Use `Is...` for Prop-valued mixins and properties when that is the local pattern, but not for data-bearing structures.

330. Use theorem-name segmentation that preserves existing API chunks

Theorem names should be `snake_case`, but if they contain an existing CamelCase declaration name, lowercase only its initial capital and keep the chunk intact. For example, prefer `liftRel_subrelation_lex`, not `lift_rel_subrelation_lex`.

331. Build theorem names from the statement, left to right

Arrange words in theorem names to follow the left-to-right order of the main symbols and arguments in the statement. For example, prefer `image_union` over `union_image`.

332. Name explicit instances with the `inst` prefix

If an instance needs an explicit name, start it with `inst...`, and do not use `inst` for non-instances. If the instance will never be referenced by name, prefer leaving it unnamed.
```lean
instance instSubsingletonFoo : Subsingleton Foo := ...
```

333. Do not use underscores in definition names

Name definitions in `lowerCamelCase`, not `snake_case`. For example, write `shortComplexObj`, not `shortComplex_obj`.

334. Keep generated names sensible

When using `@[simps]`, `@[ext]`, `@[mk_iff]`, `@[to_additive]`, instance generation, or similar automation, choose source names so the generated declarations are conventional and informative. Override autogenerated names when they are unclear, ugly, or nonconforming.

335. Use conventional binder names and established argument order in statements

Within declarations, use standard variable names (`f g`, `x y`, `s t`, `R`, `M`, `ι`, etc.) and follow the established argument order of the surrounding API. Keep binder naming and ordering parallel across related lemmas.

336. Make conversion names show direction and structure

For conversions and induced maps, make the direction obvious with names like `toX`, `ofX`, or `fromX`, and include the relevant structure when omission would be ambiguous.
```lean
def toLinearMap : ... := ...
def ofHom : ... := ...
```

337. Use standard constructor and helper names

Use `mk` for canonical constructors, `mk'` for established nearby constructor variants, and `of`/`ofX` for standard wrappers. Use `Core`, `Aux`, or `_aux` only for genuine internals, and keep even private helper names descriptive.

338. Do not encode local binder names into declaration names

Do not build theorem names from variable letters like `n`, `p`, `α`, or `q` unless they are part of an established concept. Name declarations after the mathematical objects and operations, not the chosen binder names.

339. Distinguish bundled and unbundled variants in names

When the same underlying notion appears at different bundling levels, encode that in the name.
```lean
foo
fooHom
fooLinearMap
fooContinuousLinearMap
```

340. Rename public API only for a clear benefit

Do not rename declarations gratuitously. Rename only when the old name is misleading, conflicts badly, or clearly violates convention; when compatibility matters, add a deprecation or alias.

341. Use established names for standard operation families

Reuse Mathlib’s standard names for common operations and indexed/set variants: `image`, `preimage`, `union`, `inter`, `subset`, `compl`, `sup`, `inf`, `sSup`, `sInf`, `iSup`, `iInf`, `iUnion`, `iInter`, `pow`, `nsmul`, `smul`, `div`, `mod`, `nhds`, `nhdsWithin`, and so on. Do not invent abbreviations like `preimg`.

342. Use `_apply` for evaluation lemmas

If a lemma states the value of a function-like object at an argument, use the `_apply` suffix; use `_apply_apply` for doubly applied function-like objects. Do not use `_apply` for mere coercion lemmas or definitional unfolding.

343. Use `coe_...` for coercion lemmas, and name casts with the local cast vocabulary

Name coercion lemmas with `coe_...` only when the coercion itself is the point; use `val` instead when the API is really about `Subtype.val`. For algebraic casts, follow the established local naming such as `natCast`, `intCast`, `ratCast`, or the prevailing `Nat.cast_*` family.
```lean
theorem coe_toLinearMap : ⇑φ.toLinearMap = φ := rfl
```

344. Name monotonicity lemmas consistently

Use `Monotone`, `Antitone`, `StrictMono`, and `StrictAnti` for properties, and theorem-name patterns like `_mono`, `_monotone`, or `.mono` according to the surrounding API. Keep related declarations parallel.

345. Distinguish `_inj` from `_injective`, and similarly for surjectivity

Use `foo_inj` for lemmas of the form `foo a = foo b ↔ a = b`, and `foo_injective` for lemmas concluding `Function.Injective foo`. Apply the same distinction to `_surj`/`_surjective` and related names when both forms exist.

346. Use `exists_...` for existential statements

If the main content of the theorem is an existential claim, especially one beginning with `∃`, prefer an `exists_...` name.

347. Do not repeat the namespace inside the identifier

Inside `namespace Foo`, write `bar`, not `fooBar` or `FooBar`, unless extra disambiguation is genuinely necessary.

348. Name rewrite lemmas after the expression being rewritten

For equality/rewrite lemmas, choose the name based on the expression users will search for or rewrite, usually the left-hand side. If appropriate, orient the equality so the more complicated expression is on the left.

349. Use `_left` and `_right` systematically for side-specific variants

For binary operations or side-specific statements, use `_left` and `_right` to indicate which side varies, is fixed, or is cancelled. Provide both variants when symmetry does not make one redundant.

350. Use `..._of_...` for implication lemmas

Reserve `of` for names read as “conclusion from hypothesis,” and put the conclusion before the hypothesis: `conclusion_of_hypothesis`.

351. Use only established abbreviations

Use established Mathlib abbreviations such as `fg`, `finrank`, `zpow`, `nsmul`, `rpow`, `logDeriv`, and `supp`. Do not invent ad hoc shortenings.

352. Distinguish equivalences from categorical isomorphisms

Use `equiv` for equivalences (`α ≃ β`) and `iso` for categorical isomorphisms (`X ≅ Y`). Name conversions between related notions in the obvious direction.

353. Use words like `zero`, `one`, `top`, and `bot` in names

Prefer identifier words over numerals or symbols in declaration names, such as `map_zero`, `pow_two`, and `eq_top_iff`. Avoid arbitrary numerals unless there is an established family.

354. Name structure fields and projections predictably

Structure fields are term-level names, so use `lowerCamelCase`. Field names should match the conventional theorem or property names they encode so the generated API is predictable.
```lean
structure Equiv where
  toFun : α → β
  left_inv : ...
```

355. Use `to...` only for genuine projections or conversions

Reserve `toX` names for canonical projections, forgetful maps, or explicit conversions. Do not use `to...` for arbitrary constructions unrelated to forgetting structure.

356. Use `comp` consistently for composition lemmas

If a statement is about composition, include `comp` in the name and place it to reflect the composition order in the statement. Do not mention `comp` when the theorem is not really about composition.

357. Follow local conventions for specialized families

For specialized APIs, follow entrenched local naming rather than inventing a new pattern. Examples include `symm` placement, `succ` vs `add_one`, `prodMk`, `fun_`/`_pi`, and other family-specific conventions.

358. Make names `to_additive`-friendly

Choose multiplicative names so the additive translation is sensible, and provide an explicit additive name when the automatic result would be poor. Likewise, keep dualized names (`dual`, `_op`, `_unop`) aligned with established patterns.

359. Use singular names for predicates and plurals for collections

A predicate on elements should usually be singular or adjectival, while plural names are for bundled collections or sets. For example, `Prime : Nat → Prop` but `primes : Set Nat`.

360. Use established category names and abbreviations

For bundled categories, use the standard short name if one already exists (`Grp`, `Ring`, `Top`, ...); otherwise use the structure name with `Cat`.

361. Use standard projection and sum-side names

Use `fst`/`snd` for product projections and `inl`/`inr` for coproduct sides. Do not replace these with `left`/`right` where Mathlib already has a standard term.

362. Keep tactic, elaborator, syntax, and command names descriptive and non-conflicting

Name tactics and elaborators by behavior and scope, mirroring analogous existing tools. Give custom syntax explicit names with `syntax (name := ...)`, and avoid `#`-prefixed names for persistent commands.

363. Name `Tendsto` lemmas with `tendsto_...` when that is the main content

For lemmas whose main content is a `Tendsto` statement, prefer a `tendsto_...` prefix unless an established namespace method is better. Include filters such as `atTop`, `atBot`, `nhds`, or `nhdsWithin` when they distinguish the result.

364. Reserve `ext` for genuine extensionality lemmas

Use `ext` only for lemmas characterizing equality of arbitrary objects by their fields or evaluations. Put such lemmas in the relevant namespace, not `_root_`.

365. Reserve `refl`, `symm`, `trans`, `assoc`, and `comm` for their standard roles

Use these suffixes only when the theorem really expresses reflexivity, symmetry, transitivity, reassociation, or commutativity. In particular, use `_assoc` for reassociated variants and `_comm` for swapping symmetric arguments or commutative laws.

366. Use `₀` only for established zero-variant families

Reserve subscript `₀` for standard Mathlib families such as `MonoidWithZero` variants. Do not introduce ad hoc `₀` names.

367. Use `_def` for definitional unfolding lemmas

When a theorem simply unfolds a definition to its defining expression, `_def` is an appropriate suffix.

368. Use `congr` only for congruence lemmas

Reserve `congr`, `congrLeft`, and `congrRight` for lemmas about congruence or transport along equalities/equivalences. Do not use `congr` for arbitrary maps or unrelated equivalences.

369. Do not distinguish public names only by case or a trailing underscore

Avoid identifiers whose only difference is capitalization, and do not use trailing `_` in public names. Choose a genuinely different, readable name instead.

370. Avoid `_root_` unless it is genuinely needed

Do not use `_root_` to work around poor namespace choices. Use it only when the intended public API really belongs in the root or another parent namespace.

371. Use `_eq_` or `_eq` only when equality is genuinely the point

Use `_eq_` when the key content is an equality between two named notions, and use a trailing `_eq` only when it actually disambiguates. Do not append `_eq` mechanically to every equality theorem.

372. Use conventional names for induction principles and recursors

Follow established names such as `induction_on` rather than `inductionOn` for theorem-style induction principles. Name recursor arguments and cases conventionally (`major`, `minor`, `zero`, `succ`, `cons`, etc.).

373. Distinguish type-level and subset-level properties consistently

When both a property of a type and a property of subsets exist, follow the established pairing and do not blur them. For example, use `CompactSpace` for the type-level property and `IsCompact` for subsets.

374. Prefer American English and usually ASCII in identifiers

Use American spellings in declaration names, and prefer ASCII unless a non-ASCII form is already established. For example, prefer `center`, `neighborhood`, and `color`.

375. Use `Stronger.toWeaker` for explicit inheritance maps

When naming explicit inheritance or forgetful instances outside the `inst...` pattern, use `Stronger.toWeaker`.
```lean
instance CommRing.toRing : Ring R := ...
```

376. Use `map_...` for homomorphism-preservation lemmas

For lemmas stating that a homomorphism preserves an operation or constant, use the standard `map_*` pattern, such as `map_add`, `map_mul`, or `map_zero`.

377. Use `protected` when a short standard name should live in a namespace

If a declaration should have a conventional short name but needs namespacing to avoid clashes, use `protected` where appropriate.

378. Use established suffixes for default-value variants

When a family already uses `D` for an explicit default argument and `I` for an `Inhabited`-provided default, follow that convention consistently.

# documentation

379. Keep theorem docstrings about the result, not the proof

Use theorem and lemma docstrings to describe the statement and intended use. Put proof sketches, tactic commentary, and implementation details in ordinary comments nearby or in module-level `

380. State assumptions, caveats, and exact behavior accurately

Mention non-obvious hypotheses, quantifiers, coercions, and limitations, and ensure the docstring matches the code exactly. Do not claim more generality than the declaration has.

381. Document new public declarations when the docstring adds real value

Add `/-- ... -/` docstrings to new public, user-facing declarations: definitions, structures, classes, important instances, notation, syntax, tactics, commands, and nontrivial theorems/lemmas. Do not use placeholder docstrings or text that merely restates the name; trivial lemmas whose name and statement are already completely clear may omit a docstring.

382. Keep module docstrings high-level and synchronized with the file

Module docs should describe the file’s actual contents and main ideas, not PR history or future promises. Update them when the file gains or changes a central theorem, definition, notation, or other major export.

383. Write self-contained docstrings

Make each docstring understandable in hover view without relying on surrounding file context. Do not say “above”, “below”, or “this” ambiguously; name the relevant declaration, object, or parameter explicitly.

384. Use standard mathematical terminology and Mathlib naming

Prefer established mathematical terminology and existing Mathlib conventions over ad hoc wording or obscure abbreviations. If a declaration name is descriptive rather than standard, mention the standard term or common alias when that improves discoverability.

385. Add a module docstring to every new substantive file

Every nontrivial new file should have a top-level `/-! ... -/` module docstring after the imports. It should begin with a `#` title and briefly explain the file’s mathematical purpose, main definitions, and major results.

386. Describe mathematical meaning, behavior, and purpose

Explain what the declaration means mathematically, how it behaves, and why a user would use it. Do not merely paraphrase the type signature or identifier.

387. Follow normal sentence-style punctuation and capitalization

Capitalize the first word of a docstring. End complete sentences with periods, and use consistent punctuation style within a file.

388. Use the correct doc comment form and placement

Use `/-- ... -/` for declaration docstrings and `/-! ... -/` for module docstrings. Place module docstrings immediately after imports, and place declaration docstrings directly on the declaration they document.

389. Explain how variants differ

When introducing `foo'`, left/right variants, specialized/generalized versions, converses, or similar nearby declarations, say explicitly how they differ in hypotheses, domain, codomain, or formulation.

390. Put documentation on the canonical user-facing declaration

Attach the main docstring to the declaration users should hover or search for, not to a wrapper, helper, or re-export. For aliases and notation with the same meaning, prefer `@[inherit_doc]` rather than duplicating text.
```lean
@[inherit_doc foo]
notation:50 "⌣" => foo
```

391. Cross-reference closely related declarations

Use `See also` or similar wording to point to converses, special cases, generalizations, additive/multiplicative counterparts, and alternative APIs. This is especially useful when several nearby declarations are easy to confuse.

392. Keep terminology consistent within the file and API

Use one term consistently for the same concept rather than alternating between synonyms. Match existing Mathlib terminology unless there is a strong reason not to.

393. Add comments to long, delicate, or non-obvious proofs

If a proof is long, structurally subtle, or performance-sensitive, add brief comments explaining the main steps or why the proof is written that way. Avoid comments that merely restate the current goal or obvious tactic effects.

394. Format docstrings so generated docs render correctly

Use renderer-friendly Markdown/CommonMark, with sensible indentation for wrapped paragraphs and lists. Avoid malformed formatting, broken spacing, or ad hoc HTML that harms generated documentation.

395. Prefer fully qualified names in docstring references

When referring to other declarations, prefer fully qualified backticked names when that improves reliability of doc-gen links or avoids ambiguity.

396. Mark internal or auxiliary declarations as such

If a declaration is private, auxiliary, or an implementation detail not meant for direct use, say so and point users to the preferred public API when relevant.
```lean
/-- Implementation detail. Users should use `foo` instead. -/
def fooAux ...
```

397. Use comments for local rationale, not as a substitute for docs

Use ordinary comments for local explanations, workarounds, proof strategy, and maintenance notes. Keep them close to the code they explain, and do not use them in place of declaration or module docstrings.

398. Explain non-obvious parameters, fields, and return values

Document parameters, indices, bundled data, structure fields, and return values when their role is not clear from the type alone. For `Bool`/`Option`-valued declarations, say exactly what `true`/`false` or `some`/`none` means.

399. Use backticks for Lean identifiers and valid Lean code

Wrap declaration names, notation, and Lean expressions in backticks in docstrings and comments. Only backtick valid Lean identifiers or expressions; otherwise use plain prose or a fenced code block.

400. Add characteristic lemmas for new definitions and operations

When introducing a new `def`, also provide the key lemmas that characterize or compute it, such as `_iff`, `_def`, `_apply`, or `@[simp]` lemmas. If a simp lemma mainly supports automation or a chosen normal form, document that intent when useful.

401. Document tactics, commands, attributes, and tools at the user-facing entry point

Ensure the thing users invoke has the docstring, not only internal helpers. Describe behavior, syntax, options, limitations, and how it differs from nearby commands or tactics.

402. Use standard deprecation mechanisms with explicit replacements

When deprecating a declaration, use `@[deprecated newName]` or the appropriate deprecation form so users see the replacement. Include `since := "YYYY-MM-DD"` when required, and say explicitly if there is no direct replacement.
```lean
@[deprecated newFoo (since := "2025-01-15")]
def oldFoo := newFoo
```

403. Structure module docstrings with standard sections

Use standard `##` headings such as `

404. Record TODOs and temporary workarounds clearly

Put important future work in a module docstring or a clearly marked nearby `TODO` comment, with enough context to revisit it later. Remove or update TODOs once they are no longer accurate.

405. Document instances and coercions by their mathematical meaning

For instances and coercions, explain the intended mathematical relationship between the source and target structures, not just the implementation. If typeclass behavior is surprising, document that too.

406. Keep docstrings concise and readable

Use clear natural English, put the key point first, and keep one-line docstrings on one line when possible. Add detail only when it genuinely helps users understand the API.

407. Document linter, checker, and tool behavior precisely

For linters and similar tools, state what pattern they detect, why it is discouraged, what they guarantee, and any important limitations or false positives/false negatives.

408. Use Lean/Mathlib notation and Unicode in documentation

Prefer Lean-friendly notation and standard Unicode already used in Mathlib, such as `f ⁻¹' s`, `Icc a b`, `ℝ`, `≤`, and `∘`. Avoid LaTeX-heavy prose in declaration docstrings unless Lean notation would be unreasonable.

409. Add examples to tactic, command, syntax, and notation docs

For tactics, commands, macros, syntax extensions, and unusual notation, include at least one concrete example of typical usage. Explain supported inputs, important options, goal shapes or outputs, and notable failure modes when relevant.

410. Document notation in module docs and relevant declaration docs

If a file introduces important notation or scoped notation, document it in a `

411. Prefer fixing documentation over suppressing doc lints

Do not use `@[nolint]` or `@[inherit_doc]` as a generic escape hatch for missing or poor documentation. Add real documentation instead; reserve suppressions for genuine deliberate exceptions.

412. Preserve useful existing documentation and avoid unnecessary churn

Do not remove, weaken, or rewrite good existing documentation just for stylistic preference. In a focused PR, prefer targeted fixes to inaccurate or unclear docs over broad unrelated rewrites.

413. References` section or a declaration docstring using Mathlib’s standard citation style. Reuse existing bibliography entries and standard references where possible.



414. Document omitted instances and non-obvious typeclass behavior

If a natural instance is intentionally omitted to avoid loops, diamonds, or poor inference, explain why. Also comment on surprising `inferInstance`, local instance, or inference-chain behavior when users or maintainers would otherwise be confused.

415. Document edge cases and default or junk values explicitly

If a definition returns a default value outside its intended domain, or has important degenerate cases, say so explicitly in the docstring.
```lean
/-- Returns `0` when the support is infinite. -/
def finsumLike ...
```

416. Use standardized `Porting note:` comments for intentional port divergences

When a Lean 4 port intentionally differs from the source in a non-mechanical way, add a nearby comment beginning exactly with `Porting note:` and explain what changed and why. Remove or update the note when it becomes obsolete.

417. Document notation and syntax by meaning, not just parsing

User-facing notation and syntax should explain what they mean mathematically, not only how they parse. For unusual binders or sigils, include an explicit expansion or example when helpful.

418. Implementation notes` or nearby comments. Help users and maintainers understand why the API is designed that way.



419. Explain every lint suppression or intentional exception

Whenever you use `@[nolint]`, suppress a warning, or keep an intentional exception, add a nearby comment explaining why. The explanation should help a future maintainer decide whether to remove the suppression or keep it.

420. Use `library_note` only for reusable library-wide rationale

Create a `library_note` only for design guidance that matters across multiple files or the whole library. Reference it with the standard mechanism such as `#see_note`.

421. Add references for major mathematical content

For important definitions, theorems, or files, include literature references in a `

422. Give stable names to instances or generated declarations when docs must refer to them

If documentation or links need to mention an instance or generated declaration, give it an explicit stable name rather than relying on autogenerated names. This improves hover text, linking, and maintainability.

423. Implementation notes` or comments for non-obvious design choices

Explain surprising representations, omitted instances, one-sided APIs, inference workarounds, arbitrary choices, or performance-driven decisions in `

424. Use precise, informative error messages in user-facing metaprograms

When throwing errors in `MetaM`, tactics, commands, or other user-facing metaprogramming code, provide specific messages explaining what failed and what the user should check. Avoid generic placeholders like `"failed"`.

425. Use fenced code blocks for examples, syntax, and diagrams

When including examples, syntax forms, or ASCII diagrams in docstrings, wrap them in triple backticks so they render correctly in generated documentation.

426. Use `@[stacks "TAG"]` for Stacks Project references

When a result corresponds to the Stacks Project, attach the exact `@[stacks "TAG"]` attribute with the correct tag.

427. Keep author and copyright metadata minimal, standard, and accurate

Use the project’s standard header format for new files. Only add authors for substantial file-level contributions, and do not casually change copyright headers or years for routine edits.

428. Explain unusual proof/code tricks that remain necessary

If final code contains non-obvious constructs such as `_`, `change`, terminal `simp only`, unusual parser forms, or delicate elaboration tricks, add a short comment explaining why they are needed.

429. Reserve `example` for tests and documentation

Use `example` for tests or demonstrations, especially inside docstrings or test files. Do not use unexplained `example` declarations as reusable library API when a named theorem, lemma, or private helper would be clearer.

430. Use Mathlib interval notation, not informal bracket notation

Write intervals as `Ioo a b`, `Ioc a b`, `Ici a`, and so on, not `(a, b)` or `[a, ∞)`. This avoids ambiguity and matches Mathlib style.

431. Notation` section and mention any required `open scoped`. Also document the notation on the relevant declaration when that helps users understand what it expands to.



432. Use `def` for data and `theorem`/`lemma` for proofs

Use `def` when constructing mathematical data such as an equivalence, morphism, or object. Use `theorem` or `lemma` for mathematical results, and do not use `def` merely to package proof code.

433. Implementation notes`.



434. Tags` when applicable. List the key exported declarations rather than every auxiliary lemma.



435. Communicate module deprecations explicitly

If a module is removed or renamed, leave a deprecation mechanism in the old location telling users what to import instead. Do not make downstream users guess the replacement module.

436. Implementation notes`, `



437. Main definitions`, `



438. Notation`, `



439. Use `



# module structure

440. Use the most specific existing namespace

Put each declaration in the established namespace matching the primary structure it is about, and prefer an existing namespace over inventing a new one. Choose the most specific namespace that still reflects the intended API.
```lean
namespace ContinuousLinearMap
theorem my_lemma (f : E →L[𝕜] F) : ... := ...
end ContinuousLinearMap
```

441. Reuse existing definitions and keep one canonical abstraction

Before adding a new definition, check whether Mathlib already has the concept. Prefer expressing specialized constructions as instances, abbreviations, aliases, or corollaries of existing general machinery rather than duplicating parallel API.

442. Place declarations in the most specific appropriate module

Put each definition, lemma, or instance in the file whose mathematical topic it belongs to, not merely where it happens to compile. Use tools like `#find_home!` when unsure.

443. Keep new declarations out of `_root_`

Place new definitions, lemmas, and instances in the namespace of the main mathematical object or theory, not in `_root_`, unless they are truly global API. This improves discoverability and avoids name collisions.
```lean
namespace Submodule
theorem foo ... := ...
end Submodule
```

444. Keep PRs small, focused, and reviewable

Each PR should have one coherent purpose. Separate mechanical refactors, file moves, import cleanup, and renames from substantive API or mathematical changes, and split large projects into incremental merge-ready stages.

445. Group shared assumptions with `section` and `variable`

When multiple consecutive declarations share parameters or typeclass assumptions, introduce them once in a `section` with `variable` declarations instead of repeating binders on every theorem.
```lean
section CommRing
variable {R : Type*} [CommRing R]
...
end CommRing
```

446. Keep internal helpers out of the public API

Mark proof-specific or implementation-only helpers as `private` when they are only internal details. If a result is mathematically reusable outside the file, make it public and place it in the appropriate module instead.

447. Minimize imports and keep dependency direction clean

Import the smallest set of modules needed for the file, and avoid adding heavy or transitive-only imports to foundational files. If one lemma requires heavier imports than the rest of the file, move that lemma to a downstream file instead of bloating a basic module.

448. Keep module structure coherent and well-scoped

A file should read as a coherent Lean module, not an ad hoc script with repeated top-level namespace hopping. Ensure `namespace` and `section` blocks are properly opened and closed with matching `end`s.

449. Place declarations near related material

Put new lemmas and definitions next to the existing declarations they extend or characterize. Basic API lemmas should appear immediately after the definition they describe, and related lemmas should stay in one contiguous block.

450. Keep module hierarchy clear, canonical, and non-redundant

Organize modules by the main mathematical object or logical strength, using established Mathlib hierarchy and naming. Avoid fake module paths, unclear duplication, or excessive directory nesting unless the split is stable and meaningful.

451. Follow local naming, statement, and attribute conventions

Match the naming scheme, argument order, namespace placement, `@[simp]` usage, and overall style of nearby analogous declarations. New API should look like it belongs in the file and theory where it is added.

452. Open namespaces and notation only at the narrowest useful scope

Prefer `open X in`, local `open`, `open scoped`, or `open Classical in` over file-wide `open`, unless the whole file genuinely relies on it. This limits namespace and instance pollution.
```lean
open scoped Classical in
theorem foo : _ := ...
```

453. Land prerequisites and broad refactors separately

If a change depends on a missing general lemma, new abstraction, or large reorganization, introduce that in a preliminary or follow-up PR rather than burying it inside a domain-specific change. Avoid broad downstream churn unless that refactor is itself the purpose of the PR.

454. Preserve compatibility when renaming declarations or modules

When renaming or moving declarations, provide `@[deprecated]` aliases; when moving files, leave a deprecated shim module at the old path when appropriate. Remove deprecated names only after the normal grace period.
```lean
@[deprecated new_name (since := "2026-01-01")]
alias old_name := new_name
```

455. Enforce recurring structural rules with linters and CI

If a style or hygiene issue recurs, prefer a linter or CI check over reviewer memory. Integrate checks into standard Mathlib or Lake entrypoints, and reduce false positives rather than disabling checks wholesale.

456. Keep variable and section scopes minimal

Declare only the variables and instances actually needed, and close sections as soon as their assumptions are no longer required. Avoid carrying unused assumptions through later declarations or redeclaring variables already in scope.

457. Avoid unnecessary or overly deep namespaces

Do not introduce wrapper namespaces that add no semantic value or force users through internal paths. Prefer flatter, discoverable namespace structure unless deeper nesting reflects a real conceptual distinction.

458. State results in canonical form under the weakest natural assumptions

Use the library’s standard formulation and the weakest typeclass assumptions that actually suffice. Put a lemma in the weakest section or file where it is valid, but do not over-generalize if the broader abstraction would require disproportionate new infrastructure.

459. Split large or mixed-purpose files along conceptual boundaries

If a file becomes large or mixes foundational material with heavier theory, split it into smaller modules along conceptual and dependency boundaries. Keep lighter imports available without forcing downstream users to import advanced results.

460. Factor repeated proof patterns into reusable lemmas

If the same argument or intermediate result appears repeatedly, extract it into a reusable lemma in the appropriate shared module instead of reproving it ad hoc. Keep it local only if it is not useful elsewhere.

461. Prefer one central general lemma over many special cases

When several statements are all consequences of a more natural general theorem, prove the central result and derive the special cases from it. Avoid combinatorial API growth from many near-duplicate variants.

462. Use `protected` for method-like lemmas when it avoids collisions

Mark lemmas `protected` when they are naturally part of a structure’s API and should be accessed as `X.lemma`, especially to avoid clashes with generic names. Do not use `protected` to hide broadly useful standalone lemmas without a clear reason.
```lean
namespace Foo
@[protected] theorem bar : True := trivial
end Foo
```

463. Scope notation, syntax, and specialized instances

Prefer `scoped` notation, scoped instances, and scoped parser or macro declarations over global ones. Do not introduce broad global notation or non-canonical global instances in shared modules.

464. Place tactic and metaprogramming code in the proper hierarchy

Put user-facing tactics under `Mathlib/Tactic` and keep metaprogramming utilities separate from mathematical theory. Do not mix tactic or linter infrastructure into mathematical namespaces.

465. Use `public section` and `@[expose]` only when genuinely needed

Use `public section` when a whole block is intentionally exported, and use `@[expose]` only when downstream code truly needs definitional unfolding of the implementation body. Do not add extra exposure machinery when ordinary visibility suffices.

466. Keep `Defs` files lightweight

In `Defs` files, include only core definitions, essential instances, and very basic `rfl`-style lemmas. Move theorem-heavy API and advanced results to `Basic` or later files to preserve a light import graph.

467. Keep root and widely imported modules conservative

Do not add broad imports to `Mathlib.Init` or other root files without strong justification. Changes there affect the whole library and should remain minimal and stable.

468. Avoid redundant API and thin wrapper lemmas

Do not add lemmas or definitions that merely restate obvious consequences of existing API unless they are genuinely useful for automation or repeated use. When a stronger lemma subsumes an older one, deprecate, alias, or remove the redundant version instead of keeping both.

469. Separate results by assumption strength

When different groups of lemmas require different typeclass assumptions, organize them into separate sections or files reflecting those levels. This keeps weaker results easy to find and prevents stronger assumptions from leaking into unrelated API.

470. Extract reusable lemmas from long instance or construction proofs

If an instance or construction requires a long proof, factor out supporting lemmas instead of keeping everything inline. This improves readability and often creates useful API for later files.

471. Use `namespace` blocks instead of manual name prefixes

When several declarations share a prefix, open a `namespace X ... end X` block rather than naming everything `X.foo`, `X.bar`, etc. Inside `namespace X`, write `foo`, not `X.foo`, unless qualification is needed for disambiguation.

472. Avoid unnecessary or fragmented sections

Do not create a `section` for a single declaration or merely to save a little typing. Merge adjacent sections with the same context, and use theorem-local binders when assumptions are needed only once.

473. Place instances near the definitions they belong to

Declare instances immediately after the definition or general instance they specialize, and keep related instances grouped together. Do not scatter instance declarations throughout the file.

474. Split modules by dependency weight

Separate lightweight definitions and core instances from proof-heavy, tactic-heavy, or specialized developments. Use stable splits such as `X.Defs`, `X.Basic`, and later files when that keeps imports lighter and the hierarchy clearer.

475. Keep the public API surface minimal and stable

Expose clean characterization lemmas rather than implementation-heavy details, and avoid forcing users to rely on unfolding internal definitions. A new definition should come with the basic lemmas or instances needed to make it usable, but not a large cloud of redundant wrappers.

476. Use `public import` or `export` only for intentional re-exports

Prefer ordinary `import` unless downstream users should automatically receive the imported module through the current file. Use `export` or `public import` only when that re-export is part of the module’s intended API.
```lean
namespace MyNS
export OtherNS (usefulLemma)
end MyNS
```

477. Keep files focused and place declarations in the right module

Each file should have a coherent mathematical theme. Put declarations in the file whose topic and dependency level best match them, rather than wherever the needed imports already happen to be available.

478. Scope instances carefully and keep them canonical

Global instances should be canonical and broadly appropriate. Use `local instance` or `scoped instance` for specialized or potentially conflicting instances, and place reusable public instances in the canonical namespace and file near related definitions.

479. Name sections after the assumptions they introduce

Give sections meaningful names reflecting the extra assumptions in scope, such as `section CommRing`, rather than vague topic labels. Put the corresponding `variable` declarations immediately after the section header so the scope is obvious.

480. Avoid unnecessary churn in widely used names, modules, and style

Do not rename or relocate foundational concepts, core modules, or heavily used identifiers without strong justification. Likewise, avoid widespread style-only edits unless the cleanup is systematic, local, and directly justified by the PR.

481. Order declarations from foundational to derived

Introduce basic definitions and supporting lemmas before higher-level constructions and main theorems that depend on them. Keep the file’s narrative aligned with dependency order.

482. Avoid import-time computation and side effects

Importing a module should not perform expensive computation or fragile initialization. Keep generated or cached artifacts out of the critical import path, and ensure importing Mathlib yields a usable environment.

483. Use `namespace` for naming scope and `section` for variable scope

Use `namespace` when you want qualified names and dot-notation; use `section` when you want local parameters or assumptions. Do not use one as a substitute for the other.

484. Keep bundled objects bundled when that is the standard API

State results using the standard bundled representation or canonical type used elsewhere in Mathlib, rather than an equivalent but less standard encoding. Do not unbundle maps into bare functions when downstream API expects bundled morphisms.

485. Keep tests lightweight and close to what they validate

Use dedicated test files or Lake components with minimal imports and stable runtime. Put regression tests near the relevant definition when practical, and avoid tests that rely on large rebuild surfaces or intentionally slow compilation.

486. Inline one-off trivial helpers

If a helper lemma is tiny and used only once, prove it inline rather than adding a standalone declaration. Extract a separate lemma only when it improves reuse, readability, or API.

487. Keep binder and universe order consistent

When related declarations repeat binders, preserve the established order of variables, universes, and typeclass assumptions. Avoid arbitrary reordering that creates unnecessary churn or downstream breakage.

488. Generate symmetric APIs automatically when possible

For paired additive/multiplicative or order-dual results, state one canonical lemma and derive the others with automation such as `@[to_additive]` or `@[to_dual]` when available. If the surrounding API already provides both variants manually, keep new additions consistent with that pattern.
```lean
@[to_dual] theorem max_def ... := ...
```

489. Provide standard extensionality lemmas when needed

For new structures, add the minimal useful `ext` or `hom_ext` lemmas needed for standard extensionality tooling. Do not add a large family of extensionality lemmas unless they are genuinely used.

490. Use environment extensions for persistent tooling state

For registries, caches, “already processed” markers, or other persistent metaprogramming state, use environment extensions rather than ad hoc global state. Follow existing `register...Extension` patterns.

491. Use `noncomputable section` for noncomputable developments

When a file or substantial block is noncomputable, wrap it in a `noncomputable section` rather than tagging each declaration individually. Do this only when the noncomputability genuinely applies to the whole block.

492. Use section headers and comments to reflect real structure

In long files, organize material with meaningful comment headers and section names that match the mathematical grouping. Avoid stale or arbitrary headers that do not reflect the actual contents.

493. Prefer definitional equality and coherent instance inheritance

When designing derived instances, make them definitionally equal to existing constructions whenever possible. Avoid diamonds, shortcut instances, or inheritance patterns that create multiple non-defeq versions of the same structure.

494. Use standard simplification and aliasing mechanisms

Mark genuinely useful rewrite lemmas with `@[simp]` instead of duplicating simplification logic elsewhere. When introducing a new name for an existing theorem, use `alias` rather than restating the theorem.

495. Restrict `meta` to the smallest necessary scope

Do not mark an entire file or large section as `meta` if only a few declarations need it. Scope `meta` as narrowly as possible, especially outside tactic-specific files.

496. Ensure new modules are compiled and indexed

After adding new files, make sure they are reachable from the project’s import structure so CI and users actually compile them. In Mathlib, run `lake exe mk_all` and include the resulting updates to `Mathlib.lean` in the same change.

497. Use `assert_not_exists` to protect lightweight files

In foundational files where heavy dependencies must not appear, add `assert_not_exists` checks using the most specific forbidden name that captures the architectural constraint. This helps prevent accidental import bloat.

498. Use `abbrev` for lightweight aliases

If a definition is just a convenient synonym and does not need its own reducibility or API story, prefer `abbrev` over a new `def`. This keeps the development lightweight and avoids unnecessary API commitments.

# generalization

499. State results under the weakest assumptions actually used

Use the minimal typeclasses and hypotheses required by the proof. Prefer `Semiring` over `Ring`, `Preorder` over `LinearOrder`, `Finite` over `Fintype`, `Injective` over `Bijective`, and weaker side conditions such as `≤` or `x ≠ 0` when stronger ones are unnecessary.

500. Generalize to the most natural useful form, but not speculatively

Generalize over types, parameters, indices, domains, codomains, filters, and measures when the proof supports a broader mathematically natural statement. Do not introduce extra abstraction merely for hypothetical future use if it makes the API harder to understand.

501. Prove the general theorem first; derive special cases afterward

When a specialized lemma is needed, first prove the underlying general result and obtain the special case by instantiation, rewriting, or a short corollary. Do not duplicate the proof for the special case.

502. Make non-inferable key parameters explicit; inferable ones implicit

If Lean can infer a parameter reliably, prefer an implicit binder. If a parameter is not determined by the others, is central to rewriting, or must be chosen by the user, make it explicit.

503. Extract reusable intermediate facts, but inline one-off helpers

If a local `have` captures a nontrivial fact likely to be reused, factor it into a named lemma with appropriate generality. Conversely, do not create standalone lemmas for tiny one-use proof steps that only add noise.

504. Reuse existing API; do not add redundant declarations

Before adding a new lemma, definition, or instance, check whether the result already already exists, is a direct specialization of an existing theorem, or is definitionally equal to something already in Mathlib. Do not add thin wrappers like `lemma foo := by simpa using bar`; use `bar` directly unless a specialized corollary clearly improves usability.

505. Add the expected symmetric, dual, and parallel variants

When a lemma belongs to a standard family, provide the corresponding left/right, dual, additive/multiplicative, image/preimage, `WithinAt`/`At`, `norm`/`nnnorm`, or similar variants when natural. Do not leave the API asymmetrical without a reason.

506. Use one canonical representation; avoid duplicate APIs

Choose a canonical spelling or normal form for each concept and state the main lemmas there. Provide translation lemmas for coercion variants or equivalent formulations instead of maintaining parallel theorem families for the same idea.

507. Prefer `↔` characterizations for genuine equivalences

When both directions are natural, state the result as an `iff` and use an `_iff` name. Prefer `P ↔ Q` over `P = Q` for propositions, since `iff` lemmas work better with `rw`, `simp`, `.mp`, and `.mpr`.

508. Use `Type*` by default and keep universe polymorphism clean

Prefer `Type*` or omitted universe annotations in ordinary developments. Introduce explicit universe parameters only when needed, avoid unnecessary universe clutter or forced equalities like `u = v`, and ensure declarations do not leave unresolved universe metavariables.

509. Use automation and transport mechanisms for parallel APIs

Prefer `@[to_additive]`, `OrderDual`, standard coercion lemmas, and other transport infrastructure over manually duplicating proofs. Reuse existing machinery for additive, dual, opposite, restricted, semilinear, or scalar-tower variants when possible.

510. Prefer local or filter-based hypotheses when the conclusion is local

For within-set, neighborhood, asymptotic, or convergence statements, state assumptions on the same set or filter as the conclusion. Prefer forms like `EqOn`, `ContDiffOn`, `∀ᶠ x in l, ...`, and `Tendsto` over unnecessarily global hypotheses.

511. Remove unused, redundant, and proof-only hypotheses

Every binder should affect the statement, another binder’s type, or typeclass inference. Drop assumptions implied by others, and if decidability or classical choice is only needed in the proof, use local `classical` rather than adding it to the theorem statement.

512. Handle degenerate and boundary cases explicitly instead of assuming them away

Avoid unnecessary assumptions like `n ≠ 0`, `Nonempty α`, or positivity hypotheses when the zero, empty, or boundary case can be handled directly by `by_cases`, `cases`, or `simp`. Include such assumptions only when the statement genuinely fails without them.

513. Do not rely on fragile definitional equality

Avoid proofs that depend on implementation-specific `rfl` or defeq behavior across abstraction boundaries, bundled/unbundled forms, opposites, quotients, or coercions. Use explicit API lemmas and transport lemmas so proofs remain stable under refactors.

514. Keep definitions minimal; move assumptions to lemmas

Do not bake unnecessary finiteness, decidability, nonemptiness, or side conditions into definitions. Put such requirements on the theorems that need them instead.

515. Scope `variable` declarations and assumptions tightly

Do not overuse broad section-wide `variable` blocks. Introduce shared parameters and stronger typeclass assumptions only where they first become necessary, so later declarations are not accidentally over-generalized or over-constrained.

516. Prefer the right abstraction level, not a stronger or more concrete one

State results for the simplest abstraction that captures the proof. Prefer `LinearMap` over `LinearEquiv` if invertibility is unused, `Embedding` or `Injective` over `Equiv` if no inverse is needed, and `Set`-based formulations over encoded ranges or subtype-heavy statements when the subtype itself is not essential.

517. Keep specialized convenience corollaries when they improve usability

After proving a general theorem, keep or add short specialized lemmas for common cases if they improve discoverability or avoid awkward instantiations. These corollaries should be derived from the general result, not reproved.

518. Use canonical Mathlib predicates, structures, and abstractions

State results using standard notions such as `Set.EqOn`, `Disjoint`, `Monotone`, `StrictMono`, `BijOn`, `IsLUB`, `Pairwise`, `Finite`, `Finsupp`, and `Nodup` rather than ad hoc encodings. Reuse existing Mathlib abstractions before introducing new wrappers, predicates, or typeclasses.

519. Preserve established binder order, explicitness, naming, and statement shape

When generalizing or refactoring an existing theorem, keep variable names, binder order, explicitness, and overall shape aligned with nearby API unless there is a strong reason to change them. Consistency improves search, rewriting, and downstream compatibility.

520. Split `iff` directions when they need different hypotheses

If one direction of an equivalence needs weaker assumptions than the other, prove separate directional lemmas at their natural strength and combine them into the final `iff` only under the stronger assumptions.

521. For `iff` lemmas, keep arguments mostly implicit

In `↔` lemmas, variables appearing on both sides should usually be implicit so users can write `rw [foo_iff]` or use `h.mp` and `h.mpr` without supplying extra arguments.

522. Prove results at the right categorical level, then specialize

If a result is genuinely categorical, prove it in the general categorical setting and derive concrete corollaries afterward. When computational content is needed, work with explicit cones, cocones, or chosen limit data rather than mere existential existence assumptions.

523. Prefer canonical left-hand sides and rewrite-friendly statement forms

Orient equalities and `iff` lemmas so the left-hand side is the expression users naturally encounter in goals. Choose forms that work well with `rw` and `simp`, and keep key rewrite parameters explicit when needed.

524. State the strongest natural conclusion the proof gives

If the proof naturally yields an equality rather than an inequality, an `iff` rather than an implication, or a stronger structural conclusion such as `Subsingleton`, state that stronger result and derive weaker corollaries afterward.

525. Use proposition-level finiteness and the right cardinality notion

Prefer `[Finite α]`, `s.Finite`, `Nat.card`, or `Set.ncard` when only finiteness or cardinality is needed, and obtain a `Fintype` locally only if the proof requires computation. Use `Finset.card` for explicit finite data and `Nat.card` for types.

526. Split conjunctions and independent conclusions into separate lemmas

Avoid bundling reusable facts into a single theorem with conclusion `A ∧ B` unless the conjunction itself is the natural API. Separate existence from uniqueness, and give focused lemmas for each reusable component.

527. Add foundational API for new definitions and structures

A new definition should usually come with the expected characterization lemmas, `ext` or `ext_iff`, coercion and `*_apply` lemmas, simp lemmas for special values, and compatibility with standard operations. Do not leave a bare definition without the basic API users will need.

528. Prefer `abbrev`, notation, or canonical definitions over parallel wrappers

If a new `def` would only create an unnecessary abstraction barrier, prefer `abbrev`, notation, or a single canonical definition with specialized lemmas. Collapse near-duplicate definitions instead of maintaining parallel wrappers.

529. Prove independence lemmas for choice-based definitions

If a definition depends on an auxiliary choice such as a basis, representative, or witness, prove that the resulting object or property is independent of that choice. Use those independence lemmas downstream instead of repeatedly unfolding the choice.

530. Keep proofs maintainable and robust

Prefer direct, modular proofs over brittle cleverness or dependence on accidental elaboration behavior. Add explicit type annotations when needed, use `wlog ... generalizing ...` and induction with proper generalization, and avoid gratuitous `generalize`.

531. Preserve useful definitional equalities when they are cheap and intentional

If a construction is meant to reduce by `rfl` in common cases and preserving that behavior is easy, prefer the design that keeps the useful definitional equality. But do not contort the API solely to force defeq when a clean abstraction plus explicit lemmas is better.

532. Preserve downstream compatibility when changing existing API

When generalizing or refactoring an existing theorem, avoid unnecessary breaking changes in argument order, explicitness, names, or statement shape. Keep old specialized lemmas as wrappers or deprecations when appropriate, and separate renames from signature changes.

533. Keep PR scope focused

Do not mix unrelated refactors, infrastructure changes, renames, and new theorems in a single PR. Large generalizations, file moves, or compatibility changes should usually be split into separate PRs.

534. Prefer set-level formulations over finitary encodings when the mathematics is set-based

Do not force a `Finset` or `List` representation when the statement is really about sets or unordered collections. Use `Set`, `Set.Finite`, `Multiset`, or `Finset` according to whether order and multiplicity matter.

535. Keep naming, notation, and namespace behavior conservative and predictable

Follow existing Mathlib naming conventions and avoid introducing competing naming styles. Add notation only when it is standard, unambiguous, and genuinely improves readability, and keep name resolution unsurprising under ordinary namespace usage.

536. State hypotheses in the weakest natural user-facing form

Choose assumptions users are likely to already have and that match the real dependency of the proof. For example, prefer `Preconnected` over `Connected`, `SurjOn` over global surjectivity, `x ≠ 0` over `0 < x` when order is irrelevant, and `IsUnit x` when invertibility is the real assumption.

537. Prefer arbitrary finite index types over hard-coded `Fin n`

If a result is conceptually about a finite family, state it for a general index type `ι` with `[Finite ι]` or `[Fintype ι]` rather than only `Fin n`, unless fixed-size indexing itself is essential.

538. Keep theorem statements semantically precise and free of proof artifacts

Do not expose arbitrary choices, chosen witnesses, auxiliary points, implementation details, or intermediate constructions that arose only in the proof. Public statements should mention only the real mathematical data and dependencies.

539. In category theory, prefer isomorphism over equality of objects

Use `Iso` or equivalence-style statements rather than literal equality of categorical objects unless equality is truly the right notion. This avoids unnecessary transport and matches standard categorical practice.

540. Generalize filter and measure statements appropriately

State convergence lemmas for arbitrary filters when the proof only uses filter properties. In measure theory, parameterize results by an explicit measure `(μ : Measure α)` on a `MeasurableSpace α` rather than hard-coding `volume` or requiring a bundled `MeasureSpace` unless that is genuinely intended.

541. Keep theorem statements usable after simplification

When a theorem is intended to be used after `simp` or `dsimp`, shape its arguments and conclusion so it matches the form that actually appears in goals. Add eta-expanded or composed variants only when rewriting genuinely needs them.

542. Shape simp lemmas to be canonical and composable

State `@[simp]` lemmas so they rewrite toward the canonical normal form users want and compose well with arbitrary simp sets. Do not add redundant specialized simp lemmas when a more general one already covers the case.

543. Prefer ambient-type membership hypotheses over subtype formulations

When a theorem is about elements of a set or substructure, prefer hypotheses like `x ∈ s` over introducing subtype variables `(x : s)` unless the subtype itself is essential. This reduces coercion friction and usually yields a more reusable statement.

544. Avoid syntactic tautology lemmas

Do not add lemmas whose two sides are definitionally the same or that merely restate syntax after unfolding or coercion simplification. Remove such lemmas instead of suppressing lints.

545. Design APIs so extensionality and automation are clean

Choose representations that make the main `ext` theorem natural and easy to use. If many proofs are repetitive projection-by-projection arguments, add appropriate `@[ext]`, `@[simps]`, or related automation rather than duplicating boilerplate.

546. Avoid awkward `Nat` subtraction in statements

Remember that `Nat` subtraction is truncated. Prefer addition-based reparameterizations such as `n = k + t`, `n + 1`, or equivalent formulations that avoid brittle `n - k` expressions in theorem statements.

547. Order binders idiomatically

Put type parameters and main objects first, then auxiliary data and hypotheses. Match the order users naturally encounter in expressions and the order used by related lemmas.

548. Use direct coercion and normalization lemmas when needed

If downstream use needs a specific coercion equality, state it explicitly in canonical form instead of relying on unfolding. For example, a lemma like
```lean
@[simp] lemma coe_toFoo : ((f.toFoo : _) : α → β) = f := rfl
```
is preferable to expecting users to unfold definitions manually.

549. Use `TFAE` for many equivalent characterizations

When proving several equivalent formulations of the same property, prefer a `TFAE` block over a large family of pairwise `iff` lemmas. Add only the most useful named consequences afterward.

550. Prefer direct, curried hypotheses over bundled existential or conjunctive assumptions

If users naturally supply separate facts or witnesses, take them as separate arguments rather than hiding them inside `A ∧ B`, `∃ x, ...`, or implication-shaped hypotheses. Prefer `(ha : A) (hb : B)` over `(h : A ∧ B)` and `∀ x ∈ s, P x` over subtype-heavy packaging.

551. Use `rcases` and `rintro` when destructuring with generalization

When pattern matching while also generalizing dependent variables, prefer `rcases` and `rintro` over plain `cases` and `intro` when they produce a cleaner and more robust proof state.

552. Match theorem names to their actual mathematical content

Ensure the statement has the intended strength and the name accurately describes what it proves. Do not give a theorem a name suggesting a stronger or different result than its actual conclusion.

553. Keep imports, parsing, and dependency footprint tidy

Avoid unnecessary imports and dependency growth, especially in foundational files. When porting or refactoring, preserve the intended parsed meaning with explicit parentheses if needed rather than relying on changed parser behavior.

554. In metaprograms, distinguish local variables from metavariables

Do not identify variables by user-facing names alone or conflate free variables with metavariables. Use stable identifiers such as `FVarId`, and only create fresh metavariables when the local context has actually changed.

555. For proof-oriented fixed-size data, prefer `Fin n → α` over `Vector α n`

In theorem statements and proofs, `Fin n → α` is often easier to use than `Vector α n`. Reserve `Vector` for APIs where the computational representation matters, and provide conversions if both views are useful.

556. Put declarations in the most general appropriate namespace and file

If a result is not specific to the current specialized context, place it in the more general namespace or earlier foundational file where it belongs. Avoid duplicating specialized versions in later files when a reusable general statement is possible.

557. Preserve metadata and deprecation behavior in generated or migrated APIs

Automatically generated or migrated declarations should preserve relevant attributes, naming conventions, and deprecation tags. When deprecating APIs, provide a reasonable transition path rather than removing them immediately.

# typeclass design

558. Use the weakest sufficient typeclass assumptions

State lemmas, definitions, and instances with the minimal algebraic, order, topological, or categorical assumptions actually used. Prefer `[Semiring R]` over `[Ring R]`, `[Preorder α]` over `[LinearOrder α]`, and `[AddCommMonoid M]` over `[AddCommGroup M]` unless stronger structure is genuinely needed.

559. Use `letI`/`haveI` only for actual local instances

Introduce local instances with `letI` or `haveI` only when typeclass inference should use them. For ordinary auxiliary facts or terms, use `let` or `have` instead.

560. Use explicit type ascriptions or `inferInstanceAs` to guide inference

When elaboration or typeclass search is ambiguous, add a type annotation, named arguments, or `inferInstanceAs` with the intended target type. Prefer this to strengthening theorem assumptions or relying on fragile elaborator guesses.

561. Declare something as an `instance` only if typeclass search should use it

Use `instance` only for results intended to be found automatically by inference. If a result is not meant to drive search, or is better used explicitly, declare it as a `lemma` or `def` instead.

562. Prefer `Type*`/`Sort*` by default; follow local universe conventions in sensitive areas

Use implicit universe polymorphism with `Type*` or `Sort*` in ordinary declarations. Add explicit universe binders only when necessary, and in areas like category theory match the surrounding Mathlib universe and instance conventions exactly.

563. Use typeclass arguments only for assumptions meant to be inferred

Write a hypothesis as `[P]` only if instance search is expected to supply it. If a parameter or proposition is not realistically inferable, keep it as an explicit argument.

564. Prefer standard bundled assumptions when they already exist

Use the canonical Mathlib class that packages the intended structure instead of ad hoc combinations of hypotheses. For example, prefer `[IsDomain R]` over `[Nontrivial R] [NoZeroDivisors R]` when that is the real assumption.

565. Introduce new typeclasses only when inference is genuinely useful

Do not turn every reusable property into a class. Use a `class` only when there is a canonical instance and automatic inference or propagation through constructions is part of the intended API; otherwise prefer `structure`, `def`, `abbrev`, or an explicit proposition.

566. Avoid unnecessary decidability assumptions

Do not add `[DecidableEq α]`, `[DecidablePred p]`, or `[Decidable p]` unless the statement or definition genuinely depends on computable decidability. If decidability is only needed internally, use `by classical` or a local instance.

567. Avoid duplicate, overlapping, or looping instances

Before adding an instance, check whether `inferInstance` already finds one or whether a more general existing instance subsumes it. Do not introduce instances that create diamonds, circular search, or broad fallback behavior; use a lemma or a wrapper instead if necessary.

568. Remove redundant assumptions implied by stronger ones

Do not list typeclass assumptions already implied by others in context. For example, omit `[Nontrivial R]` if `[IsDomain R]` is assumed, and do not restate additive structure already provided by `[Module R M]`.

569. Use the standard hierarchy’s intended classes

Prefer existing Mathlib hierarchy nodes such as `SMulCommClass`, `IsScalarTower`, `ContinuousSMul`, `CovariantClass`, and `ContravariantClass` over custom parallel classes. Also choose the weakest standard class that matches the proof.

570. Set explicit priorities for overlapping instances

When an instance may overlap with others, assign an explicit priority so more specific instances are tried before generic fallback ones. Broad bridge instances should usually have lower priority.

571. Preserve definitional equality in instance design

Design inheritance and derived instances so there is a single canonical path to each structure, and important inherited fields remain definitionally equal to the intended parent instances. Avoid refactors that break `rfl`-based behavior or change which instance path Lean uses.

572. Make inferable parameters implicit, but keep ambiguous structure parameters explicit

Make parameters implicit when Lean can reliably recover them from later arguments or instance search. Keep them explicit when inference is unreliable or when multiple instances may exist on the same type, especially for data-carrying structures like `MeasurableSpace` or topologies.

573. Prefer `Finite` to `Fintype` unless enumeration is required

Use `[Finite α]` when only finiteness is needed mathematically, and require `[Fintype α]` only when the statement or definition uses computable data such as `Fintype.card`, `Finset.univ`, or explicit enumeration. Derive a local `Fintype` with `letI := Fintype.ofFinite α` when needed in a proof.

574. Control reducibility deliberately in typeclass-facing definitions

If instance search should find an instance by unfolding a wrapper, use `abbrev` or `@[reducible]` intentionally. If unfolding would be harmful or noncanonical, keep the definition opaque.

575. Choose `abbrev`, `def`, and one-field `structure` intentionally

Use `abbrev` for transparent aliases that should inherit reducibility and existing instances. Use a one-field `structure` when you want a genuinely distinct type with separate instances; do not use `def` as a fake newtype.

576. Prefer direct shortcut instances over long inference chains

If typeclass search repeatedly reaches a target through a long chain of intermediate instances, add a direct canonical shortcut instance or refactor the hierarchy. This improves performance and predictability.

577. Use standard typeclass formulations for common properties

Prefer canonical Mathlib classes and predicates over ad hoc hypotheses. Examples: use `[NeZero n]` instead of `h : n ≠ 0`, `Set.Nonempty s` instead of `Nonempty s`, and standard notions like `Commute`, `Monotone`, or `RightInverse`.

578. Keep `Classical` and `noncomputable` as local as possible

Use `classical` or `open Classical` only in the smallest scope that needs it, and mark only the smallest appropriate definition or instance as `noncomputable`. Do not add `noncomputable` to `Prop`-valued declarations.

579. Scope noncanonical or context-dependent instances narrowly

If an instance is noncanonical, expensive, or only useful in one context, make it `local`, `scoped`, or attach it to a wrapper type rather than declaring it globally.

580. Ensure instance parameters are genuinely inferable

Do not introduce instance arguments whose applicability depends on unresolved metavariables or ambiguous inputs. Use `outParam` or `semiOutParam` only when a parameter is truly determined by the others.

581. Use standard coercion classes and keep coercions canonical

Define coercions through the appropriate coercion classes such as `Coe`, `CoeSort`, and `CoeFun`, and ensure the coercion really has the advertised type. Avoid ad hoc or misleading coercions.

582. Use constructor-shaped instance definitions when defeq matters

Prefer `instance ... where` or direct structure literals, explicitly assigning parent fields when necessary to preserve definitional equality. Record updates are often better than helper functions for keeping constructor shape clear.

583. Keep proof-only assumptions local

If `DecidableEq`, `DecidablePred`, `Classical`, `Nontrivial`, `Fact p`, or similar assumptions are needed only inside the proof, introduce them locally with `classical`, `letI`, or `haveI` rather than strengthening the theorem statement.

584. Prefer `FunLike`/`DFunLike` and `SetLike` interfaces

For function-like structures, provide the standard `FunLike` or `DFunLike` interface; for set-like subobjects, provide `SetLike`. Rely on these standard interfaces instead of custom coercions, membership relations, or parallel order structures.

585. Extend only minimal compatible superclasses

When defining a class with `extends`, include only the weakest superclasses whose operations and axioms genuinely match your structure. If the natural stronger superclass is too strong, extend a weaker one and add stronger instances separately.

586. Reuse canonical instances with `inferInstance` and projections

When an instance already exists, use `inferInstance`, `inferInstanceAs`, or parent projections instead of manually rebuilding it from fields. Forget parent structure via projections; do not reconstruct it.

587. Use `class` for canonical inferable structure and `structure` for explicit data

If data is meant to be passed explicitly rather than synthesized by typeclass search, define it as a `structure` rather than a `class`. Avoid data-carrying typeclasses for noncanonical choices.

588. Make property classes `Prop`-valued mixins

If a class expresses a reusable law or property rather than data, define it as `: Prop`, typically with an `Is...` name or as a small mixin. Keep optional laws such as commutativity, cancellation, or compatibility separate from core data-carrying classes.

589. Order typeclass arguments to reflect dependencies and help search

List foundational classes before structures that depend on them, and compatibility classes after the structures they relate. In instance declarations, put more discriminating assumptions earlier so search can fail fast.

590. Usually leave instances unnamed, but name them if they must be referenced

In general, let Lean use instances structurally rather than by generated names. Give an instance an explicit stable name only if you will later disable it, reprioritize it, or refer to it directly.

591. Use `Fact` sparingly and usually locally

Avoid global `Fact` instances unless they are extremely safe and canonical. Prefer explicit hypotheses, or introduce `haveI : Fact p := ⟨hp⟩` locally when `Fact` is only needed to trigger existing API.

592. Keep theorem APIs and instance APIs separate

Do not make ordinary theorems into instances or use instances as disguised lemmas. If a fact is useful both as a theorem and for inference, provide both forms explicitly.

593. Register companion instances expected by the hierarchy

When defining a new structure or action that should interact with standard automation, also provide the expected companion instances or lemmas. For example, a new `SMul` instance often also needs `SMulCommClass` or `IsScalarTower` if those laws hold.

594. Use `to_additive` carefully and define multiplicative versions first

When using `@[to_additive]`, define the multiplicative declaration first and ensure helper declarations, parent classes, and coercion-related names translate correctly. Add explicit `to_additive` mappings when automation does not choose the right names.

595. Avoid overlapping coercions to functions

Do not define multiple competing coercions from the same structure to function types. Route function coercions through the canonical `FunLike.coe` path.

596. Prefer existing standard wrappers

Use standard wrappers such as `Subtype`, `Opposite`, `Lex`, `WithOne`, and similar constructions when they fit the intended meaning. Do not invent a custom wrapper when Mathlib already provides the right one with established API and instances.

597. Keep global instances narrow, canonical, and fast

Avoid broad, variable-headed, or expensive global instances that match too many goals. An instance should either apply quickly or fail quickly.

598. Avoid pattern matching on typeclass instances

Do not destructure instances directly in proofs or definitions. Use typeclass inference, explicit arguments, projections, or lemmas about the class instead.

599. Use wrappers when one carrier needs multiple incompatible structures

If the same underlying type needs different global instances, introduce a wrapper or new bundled type and put the alternative instances there. Do not install competing global instances on the same type.

600. Prefer `Nonempty` over `Inhabited` for mere existence

Use `Nonempty α` when only existence matters. Assume or define `Inhabited α` only when a distinguished default element is genuinely part of the API.

601. Prefer concrete bundled morphism types in APIs

In theorem statements and definitions, use concrete morphism types such as `MonoidHom`, `RingHom`, `LinearMap`, or `ContinuousLinearMap` rather than `...HomClass` unless the extra abstraction is genuinely needed.

602. Handle measurable-space assumptions carefully

In measure-theoretic APIs, do not force a global `[MeasureSpace α]` when an explicit measure `μ` and a measurable-space structure suffice. Keep measurable-space parameters controlled and explicit enough when multiple sigma-algebras may exist on the same type.

603. Keep numeral support canonical and total

Use `OfNat` only when numerals have a total, canonical interpretation on the type. Do not define numeral instances for types that interpret only some numerals or whose numeral semantics are nonstandard.

604. Define foundational operations before higher-level structure

Introduce basic operations such as `Zero`, `Add`, `Mul`, or `SMul` before defining structures like `Ring`, `Module`, or similar classes that depend on them. Ensure higher-level structures use the intended underlying operations definitionally.

605. Avoid `let` bindings inside `instance` definitions

Inside an `instance`, avoid local `let` bindings that complicate unfolding and search. If helper terms are needed, move them outside or use `letI` only for genuine local instances.

606. Use `extends` only when parameters align cleanly

Use bundled inheritance when the subclass naturally extends a superclass on the same parameters. If parameters do not line up well, prefer explicit fields or unbundled mixins over awkward projection instances.

607. Use `deriving` for straightforward standard instances

When a new type can derive standard classes such as `Repr`, `DecidableEq`, `Zero`, or `One`, prefer `deriving` over manual boilerplate, provided the derived instances are the intended ones.

608. Add regression examples for delicate instance behavior

When changing or adding instances to fix inference, coherence, or definitional-equality issues, include a small `example`, `#synth`, or similar test showing that the intended instance is found and no diamond or `rfl` regression appears.

609. Keep parent fields disjoint in `extends`

When a structure extends multiple parents, ensure the parents do not share fields. Shared fields create diamonds and usually destroy definitional equality, so redesign the hierarchy or use mixins instead.

610. Register canonical derived instances once, upstream

If a structure or property is routinely derivable from another, add the general canonical instance in the appropriate foundational file rather than duplicating ad hoc local instances downstream.

611. Keep core classes minimal and avoid redundant fields

Do not add ad hoc, duplicate, or derivable fields to foundational classes. Every extra field becomes a permanent burden for all instances and often creates coherence problems.

612. Use standard notation typeclasses

Hook overloaded notation into standard classes such as `Membership`, `SMul`, `Pow`, `HMul`, `HSMul`, and `HPow` rather than inventing ad hoc notation encodings. Keep conceptually different operations in different classes.

613. Prefer `AEMeasurable` when full measurability is unnecessary

If a theorem only needs almost-everywhere measurability, state it with `AEMeasurable` rather than `Measurable`. Do not strengthen assumptions beyond what the proof uses.

614. Prefer standard transitivity registration via `Trans`

Use the `Trans` typeclass rather than the legacy `@[trans]` attribute for transitivity behavior, especially for heterogeneous or nonuniform relations.

# api design

615. Reuse existing Mathlib abstractions and keep one canonical API

Before adding a new definition, theorem, notation, or wrapper, search Mathlib for the canonical existing concept and reuse it. Do not create parallel APIs that differ only by naming, notation, packaging, or minor statement changes; if a duplicate name is needed, bridge with `alias`, `abbrev`, or a deprecated alias instead of reproving everything.

616. Make inferable parameters implicit and central parameters explicit

Use implicit binders only for arguments Lean can reliably infer. Keep mathematically central or non-inferable data explicit, and use `outParam` only for genuine functional dependencies.

617. Preserve backward compatibility when changing public API

When renaming, moving, or replacing a public declaration, keep a deprecated alias or wrapper so downstream code still compiles with a warning. Do not silently change the meaning, assumptions, argument order, or binder structure of a public declaration without an explicit migration path.

618. Hide implementation details behind user-facing lemmas

Public statements should use the intended mathematical interface, not quotient representatives, `Classical.choose`, internal wrappers, coercion internals, or awkward encodings. Keep foundational representations internal and expose stable characterization lemmas instead.

619. Add reusable API lemmas when proofs repeatedly need awkward rewrites

If proofs repeatedly require `change`, `convert`, long `rw` chains, or transport boilerplate, that usually indicates a missing API lemma. Factor such patterns into small reusable lemmas in the appropriate namespace.

620. Mirror existing APIs when adding analogous constructions

If you add a construction parallel to an existing one, copy the established naming pattern, assumptions, companion lemmas, ext lemmas, and simp behavior. New APIs should feel like part of the same family, not a one-off variant.

621. Prefer one canonical representation and bridge alternatives explicitly

When multiple equivalent representations exist, choose one as the source of truth and build the API around it. Provide explicit equivalences and bridging lemmas rather than duplicating the API on each representation or relying on accidental definitional equality.

622. State definitions and lemmas at the greatest natural generality

Use the weakest reasonable assumptions and the broadest natural domain. Prove the general result first, then add specialized wrappers only when they clearly improve ergonomics.

623. Give every new public definition a usable API immediately

Do not add a bare public definition. Also provide the obvious supporting lemmas and instances: `_apply`/evaluation lemmas, `*_iff` characterizations, identity/composition laws, extensionality lemmas, coercion lemmas, and relevant `simp` lemmas.

624. Introduce new public declarations only when they are independently useful

Minimize the public API surface: add new public `def`s, lemmas, structures, and instances only if they are genuinely reusable. Inline one-off helpers, mark local scaffolding `private`, and avoid exporting implementation-detail declarations.

625. Provide the expected companion lemmas and symmetric variants

When a result naturally has left/right, source/target, inverse, additive/multiplicative, dual, or similar variants, add the obvious companions. Do not force users to reconstruct standard symmetric forms manually.

626. Place declarations to support natural dot notation

Put lemmas in the namespace of their primary receiver and order arguments so expressions like `h.foo` or `f.map_bar` work naturally. Use `protected` when helpful to support dot notation without polluting the global namespace.

627. Keep assumptions minimal and do not expose proof-only hypotheses

Remove unused variables and avoid stronger typeclass assumptions than the statement needs. Do not burden users with assumptions like `[DecidableEq α]` or stronger algebraic structure if they are needed only for the proof; introduce them locally inside the proof instead.

628. Use `abbrev` only for true definitional aliases

Use `abbrev` when a declaration is just a transparent synonym and should not create a new API boundary. Use `def` when the concept deserves its own abstraction, documentation, or supporting lemmas.

629. Use automation-generating attributes instead of duplicating parallel APIs

Use attributes such as `@[to_additive]`, `@[to_dual]`, and `@[mk_iff]` when they fit the design. This keeps additive/multiplicative, dual, and iff-style APIs aligned and avoids hand-maintained duplication.

630. Prefer standard constructors and helper APIs over manual constructions

When Mathlib provides canonical constructors or helper functions, use them instead of rebuilding structures field-by-field. For example, prefer APIs like `Quotient.lift`, `Quotient.map`, `AlgHom.ofLinearMap`, or other standard universal-property constructors.

631. Use bundled morphisms and equivalences when they are the standard interface

If a map preserves structure, define it as the appropriate bundled object such as `RingHom`, `LinearMap`, `AlgHom`, `ContinuousLinearMap`, `Equiv`, or `OrderIso` rather than as a bare function plus side lemmas. In reusable lemmas, generalize over `FunLike`/`HomClass`-style interfaces when that matches existing Mathlib practice.

632. Prefer standard predicates and canonical formulations

Use established Mathlib predicates and formulations such as `Set.MapsTo`, `Set.EqOn`, `Function.Surjective`, `Filter.Tendsto`, `Disjoint`, `HasSum`, and standard universal-property APIs. Prefer canonical object/property formulations over ad hoc encodings.

633. Follow existing Mathlib naming, namespace, and statement-shape conventions

Choose names, suffixes, namespaces, and theorem shapes that match nearby APIs, such as `_apply`, `_iff`, `_ext`, `toFoo`, `ofFoo`, and `IsFoo`. Prefer one canonical spelling per concept and deprecate older alternatives rather than maintaining parallel names.

634. Choose bundled structures, predicates, and wrappers intentionally

Use a `Prop` predicate for a mere property, and use a `structure` when you need stored data, named fields, coercions, or instances. Avoid unnecessary wrappers and avoid single-field `Prop`-valued structures unless they provide real API value.

635. Treat binder structure as public API

Do not casually rename, reorder, regroup, or change explicitness of binders in existing public declarations. In Lean, these changes can break downstream code even when the mathematical content is unchanged.

636. Use `alias` for useful alternate names and `iff` directions

When one direction of an `iff` is commonly used directly, expose it under a good name with `alias` rather than forcing users to write `.1` or `.2`. Also use `alias` rather than reproving a theorem when you only need a second name.

637. Prefer explicit equivalences and isomorphisms over equalities

When relating types or structured objects, prefer `Equiv`, `Iso`, `LinearEquiv`, `OrderIso`, and similar bundled equivalences over equality unless equality is truly the intended interface. These are usually more reusable and better supported by existing API.

638. Use the most structured standard representation of the mathematics

Prefer the representation with the strongest existing API support, such as `Equiv` for bijections, `PartialEquiv` for partial equivalences, `Finset` for finite unordered collections, and standard container/cardinality APIs instead of bespoke encodings.

639. Order arguments for ergonomics and compatibility

Match the argument order of the canonical existing API. Usually this means implicit and typeclass parameters first, then the main explicit object, then other explicit inputs, with dependent arguments in dependency order and hypotheses later.

640. Use standard parser, elaborator, command, and extension infrastructure

When adding syntax, commands, attributes, or tactic interfaces, use the established Lean and Mathlib parser/elaborator mechanisms and match the style of analogous existing tools. Use the lightest extension mechanism that fits the job.

641. Keep structures minimal and derive redundant fields

Store only essential data in structures. Do not add fields that can be derived from other fields or from a universal property, and prefer `extends` when refining an existing structure instead of repeating fields manually.

642. Package related data and coherence assumptions together

If several arguments are always used together and must satisfy compatibility conditions, bundle them into a structure rather than repeating a long list of loosely related assumptions in every theorem. This usually yields a cleaner and more reusable API.

643. Use `@[simp]`, `@[simps]`, and simp-normal forms deliberately

Add simp lemmas for obvious computational behavior, projections, coercions, constructor identities, and `_apply` lemmas. Do not add simp lemmas that expose unstable implementation details, create loops, or normalize to the wrong representation.

644. Do not rely on definitional equality as public API

If users are expected to rewrite or compute with a definition, provide explicit lemmas such as `*_def`, `*_apply`, `coe_*`, or `ext` lemmas. Do not expect downstream users to unfold definitions manually or depend on fragile `rfl`/defeq behavior across abstraction boundaries.

645. Prefer standard coercions and `FunLike` infrastructure for wrapper types

If a wrapper naturally acts like a function or underlying object, provide the expected coercions and `FunLike`/`CoeFun` instances rather than bespoke projection functions. Also add the corresponding `coe_*` and `_apply` simp lemmas.

646. Prefer mathematically meaningful statements over representation lemmas

State lemmas in the language users naturally reason in, not in terms of helper defs or low-level encodings. For propositions, prefer `P ↔ Q` over `P = Q` when the result is naturally an equivalence.

647. For metaprogramming APIs, prefer explicit configuration and clear errors

Thread user-facing configuration explicitly through tactic, command, and elaborator APIs rather than relying on hidden global state or internal flags. When preconditions fail, report informative errors with enough local context to explain what went wrong.

648. Avoid arbitrary noncanonical choices in core definitions

Do not bake unnecessary choices into public definitions. If choice is essential, isolate it in a separate definition and expose stable characterization lemmas rather than making downstream users depend on a chosen representative.

649. Keep notation lightweight, standard, and scoped

Define notation as thin syntax over existing semantics, not as a new semantic layer. Introduce notation sparingly, avoid conflicts with core syntax, prefer scoped notation when ambiguity is possible, and ensure elaboration and pretty-printing round-trip predictably.

650. Separate renames from semantic changes

A pure rename should not also change statement shape, argument order, or behavior. If semantics change, introduce a new declaration under a new name and provide explicit compatibility lemmas or deprecated bridges.

651. Handle edge cases with total, uniform APIs

Prefer total definitions with a fixed codomain and sensible edge-case behavior over APIs that become partial or require extra hypotheses just to state them. Use safe accessors like `get?` and natural default or degenerate values when appropriate.

652. Add extensionality and eliminator support for new types

For new structures, bundled maps, and wrapper types, provide `@[ext]` lemmas and `ext_iff` when useful. Also add custom induction, cases, or eliminator lemmas with the standard attributes when the default eliminators are not ergonomic.

653. Provide smart constructors when they remove routine proof obligations

When constructor proofs can be filled in canonically or computed internally, offer smart constructors for common use. Keep the full proof-carrying constructor available for advanced uses, but optimize the common API for usability.

654. Prefer incremental, low-churn refactors and stable public APIs

Avoid disruptive redesigns unless the payoff is clear. Internal refactors should not force users to rewrite code when the public semantics have not changed.

655. Prefer canonical coercion and conversion paths

Use the standard cast or coercion route for a concept, such as canonical `Nat.cast`, `Int.cast`, or `algebraMap`-based formulations. Avoid multiple competing coercion paths to the same target.

656. Put declarations in the file and module where users will look for them

Place broadly useful lemmas in the namespace and file of the concept they belong to, not in a problem-specific file. Keep imports and dependencies aligned with the intended API, and avoid introducing heavier dependencies than necessary.

657. Prefer explicit witness definitions only when the witness will be reused

If an existence proof yields data that will be referenced repeatedly, define the chosen witness as a named `def` and prove its properties separately. If the witness is not meant to be reused, prefer an existence theorem over introducing a named definition solely to package it.

658. Use standard transport and identity constructors

When transporting data along equality, use standard APIs such as `eqToIso`, `eqToHom`, `Eq.ndrec`, `.refl`, `copy`, or analogous canonical tools rather than ad hoc wrappers. This keeps proofs compatible with existing infrastructure and often improves definitional behavior.

659. Do not add new axioms to fill API gaps

Develop missing theory as definitions, instances, and lemmas rather than postulating new axioms. If a result is temporarily unavailable, use an explicit placeholder mechanism rather than hiding the gap behind a fake proof or distorted API.

660. Prefer explicit type signatures on new public declarations

Give new public definitions and lemmas clear type signatures rather than relying on inference. This makes declarations easier to read, review, and search.

661. Use `def` for data and `theorem` for propositions

If a declaration constructs data, maps, or structures, make it a `def`; reserve `theorem` for propositions. Prefer a definitional construction when downstream code should be able to use it by computation or `rfl`.

662. Avoid coercions that obscure meaning or create ambiguity

Do not add coercions when there are multiple plausible interpretations or when the coercion hides important structure. In such cases, prefer explicit named projections or conversions.

663. Design APIs to compose with existing automation

Prefer theorem shapes and attributes that work with `simp`, `norm_cast`, `gcongr`, `positivity`, `ext`, and related tools. If a new coercion or algebraic interface is important, add the expected automation lemmas such as `@[norm_cast]` where appropriate.

664. Mark noncomputable definitions honestly, but preserve computability when possible

If a construction is inherently classical, mark it `noncomputable` rather than forcing an artificial computable design. Conversely, do not introduce unnecessary classical or noncomputable layers into APIs that can remain computable.

665. Use `@[implemented_by]` only to improve performance without changing semantics

When a clean specification is slow to compute, keep the user-facing definition and connect it to a more efficient implementation with `@[implemented_by]`. Use this to improve runtime behavior, not to hide semantics or create a second API.

666. Keep user-facing metaprogramming configuration separate from internal plumbing

Do not expose internal debugging or implementation flags in public config structures unless users are meant to control them. Use the standard Lean/Mathlib option and configuration infrastructure for tactics, commands, and linters.

667. Prefer pure return types for metaprogramming helpers when effects are unnecessary

If a helper only computes data, return `Option`, `Except`, or another pure type rather than `MetaM` or `IO` unless effects are genuinely required. This makes the helper easier to test, reuse, and reason about.

668. Preserve compatibility with likely upstream `Std` conventions when relevant

If a feature plausibly belongs in `Std`, avoid Mathlib-specific design choices that would block future upstreaming. Keep temporary compatibility hacks and porting scaffolding from becoming permanent public infrastructure.

# existing api

669. Reuse existing theorems, definitions, constructors, and instances

If Mathlib already has the needed result or object, use it rather than reproving it or rebuilding it locally. Prefer fixing imports or applying the existing constructor over creating a parallel definition.

670. Adapt existing lemmas with rewriting instead of reproving variants

If an existing theorem nearly matches the goal, use `rw`, `simp`, `simpa`, `convert`, `symm`, or argument reordering to apply it. Do not add a near-duplicate lemma just because the statement differs slightly.

671. Search for existing API before adding anything new

Before introducing a definition, lemma, instance, or helper, search Mathlib first (`exact?`, `apply?`, `library_search`, `#find`, `Loogle`, grep, `#synth`). Reuse existing declarations instead of duplicating them; if something small is genuinely missing, add it once as reusable library API in the right place.

672. Prefer the most specific existing lemma when it matches the concrete goal

When a structure-specific lemma already fits, use it instead of coercing to a more general setting and rewriting back. Match the exact operation and object in the goal, e.g. `Matrix.map_sub`, `Finset.sum_congr`, or the correct `tsub`/`Int.ediv`/`Nat.cast` lemma.

673. Prefer the most general reusable lemma when the argument is abstract

If a proof only uses general structure, use or state the theorem at that level of generality. Do not specialize unnecessarily when a standard abstract lemma already exists, e.g. prefer `Subsingleton.elim` to a type-specific variant.

674. Prefer characterization lemmas and canonical rewrites

Use existing `..._iff`, `..._eq_...`, `mem_...`, `range_...`, `span_...`, `closure_...`, and similar lemmas to rewrite goals into standard forms. Avoid manually reconstructing equivalent statements.

675. Use canonical names, namespaces, notation, and modern Lean 4 API

Use the actual Mathlib identifier, spelling, casing, namespace, and notation rather than inventing aliases or preserving obsolete Lean 3 names. For example, prefer `congrArg` over `congr_arg`, and use standard notation like `ℝ ∙ v`.

676. Avoid redundant wrappers and trivial lemmas

Do not add one-off lemmas that merely compose existing results, restate a theorem for a single use site, or are just `rfl`/`inferInstance`, unless they materially improve rewriting, automation, or discoverability.

677. Add reusable bridge lemmas instead of repeating local workarounds

If several proofs need the same small conversion or rewrite fact, add it once as reusable API in the appropriate place. Do not duplicate ad hoc rewrites across multiple proofs.

678. Prefer established topology, analysis, filter, and measure-theory API

For continuity, convergence, neighborhoods, metric and uniform structures, asymptotics, integrability, interval integrals, and measure-theoretic constructions, use the standard Mathlib API (`Filter.Tendsto`, `Eventually`, `Metric`, `IsBigO`, `Measure.map`, `integral`, etc.) rather than unfolding definitions or rebuilding epsilon-delta arguments.

679. Prefer aliases and projections over reproving equivalent lemmas

If a new lemma is just a symmetric form, one direction of an `iff`, or a renamed restatement, define it via `.symm`, `.mp`, `.mpr`, or `alias` rather than giving a new proof. Keep one canonical proof of each fact.

680. Use existing constructors and builders instead of assembling structures by hand

When Mathlib provides a constructor or helper, use it rather than filling fields manually. Examples include `Equiv.ofUnique`, `MulEquiv.ofBijective`, `AlgEquiv.ofRingEquiv`, `NatIso.ofComponents`, and `Module.Free.of_basis`.

681. Reuse existing typeclass instances via inference

Do not manually construct or redeclare instances that typeclass search can already find. Use `inferInstance` or `inferInstanceAs`, and avoid referring to autogenerated instance names directly.
```lean
letI := inferInstanceAs (Subsingleton α)
```

682. Use canonical definitions, bundled structures, and standard abstractions

Prefer Mathlib’s standard notion over ad hoc reformulations. Use bundled objects such as `AlgHom`, `ContinuousLinearMap`, `LinearEquiv`, `OrderEmbedding`, `Function.Injective`, `DenseRange`, `RingCon`, etc., when they match the context.

683. Prefer standard coercions and conversion lemmas over ad hoc conversions

Use existing coercions, `to...` maps, and bridge lemmas rather than inventing local conversion functions. If coercion inference is insufficient, use the explicit canonical conversion, e.g. `LinearEquiv.toLinearMap e`.

684. Provide and use automation-friendly rewrite lemmas

For new definitions and bundled structures, add the standard lemmas needed for simplification and rewriting, especially for coercions, projections, applications, and membership tests. Tag lemmas with attributes such as `@[simp]`, `norm_cast`, `fun_prop`, or `positivity` when appropriate.

685. Mirror additive, dual, opposite, and analogous API

When adding a lemma in a standard family, check whether the corresponding additive, dual, opposite, left/right, `sup`/`inf`, `iSup`/`iInf`, or analogous container version should also exist. Use `@[to_additive]`, `@[to_dual]`, and related mechanisms instead of manual duplication when possible.

686. Prefer map/comap/image/preimage and substructure API over set-level reproving

For images, preimages, ranges, kernels, spans, closures, and transport of substructures, use dedicated lemmas such as `map`, `comap`, `image`, `preimage`, `ker`, `range`, `span`, and `closure`. Avoid manual set-extensionality proofs when object-specific API already exists.

687. Prefer monotonicity, order, lattice, congruence, and positivity API

For order-theoretic arguments, use existing lemmas for `Monotone`, `StrictMono`, `GaloisConnection`, `OrderIso`, `sup`, `inf`, `sSup`, `sInf`, and standard tools like `gcongr`, positivity lemmas, and `hp.mono hq`. Do not introduce one-off helper lemmas for routine monotonicity or congruence steps.

688. Reuse existing metaprogramming, elaboration, and notation infrastructure

When writing tactics, macros, simprocs, delaborators, or notation, build on existing Lean/Mathlib utilities rather than reimplementing syntax traversal, elaboration, simp-context construction, or pretty-printing machinery. Use notation as syntax sugar for canonical underlying terms and reuse existing unexpanders and dot-notation support.

689. Do not unfold definitions when interface lemmas already exist

Treat definitions as opaque when there are named lemmas describing their behavior. Prefer `*_apply`, `*_def`, `mem_*`, `map_*`, `range_*`, `*_iff`, and similar interface lemmas over `unfold` or defeq-sensitive proofs.

690. Use public, stable API rather than internal implementation details

Prefer exported user-facing lemmas and constructors over private declarations, tactic-only helpers, autogenerated instance names, or implementation lemmas. Internal declarations are not the intended interface and are more fragile under refactors.

691. Prefer homomorphism lemmas like `map_*`

Use `map_sum`, `map_mul`, `map_pow`, `map_smul`, `map_zero`, and similar lemmas from the appropriate hom class instead of expanding definitions and simplifying by hand.

692. Prefer standard quotient, localization, and universal-property API

For quotients, localizations, fraction rings, generated subobjects, and induced maps, use constructors and lemmas such as `Quotient.lift`, `Quotient.map`, `IsLocalization.lift`, `RingCon.Quotient`, and ext/universal-property lemmas. Do not use implementation-level devices like `Quotient.out` when the structured API suffices.

693. Import the module that provides the needed API, but keep dependencies minimal

If a theorem or instance exists but is unavailable, add the appropriate import rather than duplicating the result locally. Prefer more foundational modules when they already provide the needed API, and verify dependency minimization by testing the file, not only with tools.

694. Use the weakest sufficient hypotheses

Do not require stronger typeclasses or assumptions than necessary. Match theorem statements to the weakest standard hypotheses under which the proof and the supporting library lemmas work.

695. Use extensionality lemmas instead of manual pointwise or fieldwise proofs

For function-like or bundled structures, prefer `ext`, `ext1`, `DFunLike.ext`, `LinearMap.ext`, `Functor.ext`, and similar lemmas. This is usually shorter, more robust, and more idiomatic than manual `funext` or field-by-field proofs.

696. Prefer standard finite/cardinality/finiteness APIs

Use the correct API for the object being counted: `Fintype.card` or `Nat.card` for types, `Finset.card` for finite containers, `Set.ncard` for finite sets, and `Set.encard` when finiteness may vary. Derive finiteness from `Finite`/`Set.Finite` lemmas and use local `Fintype.ofFinite` when appropriate instead of manually constructing enumerations.

697. Reuse inherited API from parent structures and wrappers

If a structure extends another or is a subtype/wrapper, use the parent API directly unless a genuinely structure-specific lemma is needed. Avoid restating the same facts for the child type without added value.

698. Prefer existing automation when it is the intended tool

When a goal is a standard algebraic, arithmetic, bitvector, positivity, or regularity consequence already supported by Mathlib, use tools like `ring`, `omega`, `norm_num`, `positivity`, `fun_prop`, `aesop`, `grind`, or `bv_decide`. But do not expect automation to solve goals outside its intended scope.

699. Reuse existing transport and congruence constructions

When moving data across equalities, equivalences, or isomorphisms, use standard helpers such as `Submodule.equivOfEq`, `TensorProduct.congr`, `LinearEquiv.arrowCongr`, `Equiv.arrowCongr`, or `Ideal.quotEquivOfEq`. Do not hand-build transported structures if a canonical combinator exists.

700. Prefer exact theorem application when the goal already matches

If the goal is exactly an existing theorem, use `exact`, `simpa`, or direct application. Do not reconstruct a proof of a fact already available verbatim.

701. Add missing simp lemmas when simplification repeatedly gets stuck

If many proofs need the same obvious simplification, add the right lemma to the library instead of repeatedly working around `simp` locally. But do not mark a theorem `[simp]` unless it is genuinely a good simplification rule.

702. Use standard cast and numeral APIs

Prefer `Nat.cast`, `Int.cast`, `algebraMap`, and the associated lemmas over ad hoc cast formulations. Use `norm_cast`, `push_cast`, and the correct bridge lemmas for numerals rather than reasoning through unrelated representations like `Int.ofNat` unless the goal genuinely uses them.

703. Follow existing naming, argument order, statement shape, and file placement

When adding new API, mirror analogous existing lemmas in naming, assumptions, orientation, and argument order. Put declarations in the namespace and file where users will naturally look for them, and imitate nearby Mathlib code.

704. Write statements in canonical forms targeted by existing API

Prefer standard formulations such as `iSup` over `sSup (Set.range f)`, `Function.Surjective` over `∀ y, ∃ x, ...`, and the correct cardinality API for the object involved. Canonical statement shapes make existing lemmas and automation apply directly.

705. Reuse existing induction and recursion principles

Before writing custom recursion or induction, check for a library principle tailored to the type, such as `Fin.induction`, `Fin.consInduction`, or `Nat.binaryRec`. Prefer the standard recursor when it matches the structure of the argument.

706. Prefer standard container APIs and match their assumptions

Use the dedicated API for `Set`, `Finset`, `List`, `Multiset`, `Finsupp`, `DirectSum`, and similar structures rather than ad hoc recursive definitions or manual conversions. Choose lemmas whose equality and decidability assumptions match the context, such as `DecidableEq` vs `BEq`.

707. Prefer coercion and cast lemmas over low-level injectivity arguments

When rewriting through bundled maps or casts, use `coe_*`, `*_apply`, `norm_cast`, and `push_cast` lemmas instead of manual coercion manipulation or injectivity proofs. This is usually more robust and aligns with existing simp infrastructure.

708. Use standard `if`/`dite` rewriting lemmas

For conditional expressions, use lemmas such as `if_pos`, `if_neg`, `dif_pos`, `dif_neg`, `apply_ite`, and `apply_dite` that match the position of the conditional. Do not introduce bespoke lemmas for routine `ite` rewriting.

709. Prefer object-specific and category-theory infrastructure

Use the dedicated API for structures like `Matrix`, `TensorProduct`, `Polynomial`, `Submodule`, `Ideal`, `Subgroup`, `LinearMap`, and `ContinuousLinearMap`, and use standard category-theory constructions for limits, colimits, adjunctions, whiskering, `eqToHom`, `Comma`, `StructuredArrow`, and natural isomorphisms. Do not reduce everything to lower-level representations or ad hoc universal-property proofs.

710. Use `#synth` to check instance availability, and add only genuinely missing instances

When deciding whether a new instance is needed, test with `#synth` rather than `#check`. If inference really cannot produce the instance, add only the minimal bridge instance needed, not a parallel hierarchy.

711. State results at the natural bundled morphism level

Use the morphism type that carries the relevant structure: for example `AlgHom` rather than `RingHom` when algebra structure matters, or `ContinuousLinearMap` rather than `LinearMap` in normed settings. This gives access to the intended API and avoids later coercion workarounds.

712. Add standard extensionality lemmas when repeated manual ext proofs appear

If a structure repeatedly requires manual extensionality arguments and no standard `ext` lemma exists, add one following Mathlib conventions. This is better than duplicating the same proof pattern throughout the file.

713. Preserve usability when generalizing or refactoring API

When replacing specialized API with a more general theorem or definition, make sure the old form remains easy to recover by `simpa`, an alias, or a thin wrapper if users are likely to search for it. Add bridge lemmas when introducing a new formulation.

714. In analysis, prefer the strongest reusable standard formulation

State analytic results in the form that composes best with existing API, such as `HasDerivAt` rather than only `deriv`, when the stronger statement is natural. Stronger standard formulations are usually easier to reuse and specialize later.

715. Qualify names when ambiguity is plausible

If an unqualified name could resolve to the wrong declaration or a local definition, write the namespace explicitly. For example, prefer `Relation.Asymmetric` or `List.mem_map` when ambiguity is realistic.

716. Use the `Fact` pattern when a proposition must be supplied as an instance

If typeclass inference needs a proposition as an instance, wrap it in `Fact p` rather than inventing a custom workaround. This is the standard Mathlib pattern for assumptions such as primality or positivity hypotheses.

717. Respect `simps` and projection infrastructure

If `simps` generates poor lemmas, write the desired lemma manually and support it with `initialize_simps_projection` when appropriate. Reuse the existing projection setup rather than bypassing it downstream.

718. Prefer standard logical projection and witness-extraction APIs

Use `Iff.mp`, `Iff.mpr`, and standard elimination/projection lemmas rather than custom helpers. When a reusable chosen witness is needed, use `Exists.choose`, `Classical.choose`, and their specification lemmas.

# file organization

719. Put declarations in their canonical home

Place each new definition, theorem, or instance in the existing Mathlib file whose mathematical topic, abstraction level, and dependencies best match it. Use `#find_home` or `#find_home!` first, then confirm by checking nearby API, docs, and imports.

720. Place declarations near the API they belong to

Put a theorem, simp lemma, alias, or instance immediately after the definition or core lemma it elaborates when possible. Keep closely related variants adjacent.

```lean
def foo := ...

@[simp] theorem foo_apply ... := ...
```

721. Prefer the earliest appropriate file in the hierarchy

If a result is broadly useful and does not depend on later theory, move it upstream to the earliest reasonable module. Do not make foundational files import later specialized files just to host a reusable lemma or instance.

722. Do not rely on transitive imports

Import modules directly for declarations, notation, attributes, tactics, or instances your file uses. This keeps the file robust when the dependency graph changes.

723. Minimize imports aggressively

Import only the modules actually needed for the file’s declarations, notation, tactics, and instances. Remove unused or “just in case” imports, and prefer the narrowest module that provides what you use.

724. Keep foundational files dependency-light

Do not add heavy imports or unrelated theory to early files such as `Defs`, `Basic`, notation, or utility modules. If a result needs stronger imports, place it in a later file.

725. Keep file names, module paths, and directories conventional

Use descriptive `UpperCamelCase` file names and place files in the directory hierarchy matching their mathematical domain and abstraction level. The module path, import path, and filesystem location should align exactly.

726. Order imports consistently

Sort imports alphabetically when possible, but preserve any semantically necessary order for syntax, notation, attributes, or instances. Keep `public import`s before ordinary imports, with clean grouping.

727. Factor reusable helpers into named lemmas; keep local helpers private

If a helper fact is useful beyond one proof or file, extract it into a standalone theorem in the appropriate shared location. If it is only a technical artifact of the current file, mark it `private`.

728. Split large or mixed-purpose files along real boundaries

If a file becomes too large, mixes distinct topics, or accumulates heavier dependencies, split it into smaller focused modules. Split by genuine topic or dependency boundaries, not arbitrarily.

729. Prefer specific imports over umbrella imports

Inside Mathlib, import the module that actually provides the declarations you need rather than broad entrypoints like `Mathlib`, `Std`, or `Batteries`, except in intentional umbrella files. Broad imports hide dependencies and bloat the graph.

730. Follow porting layout and alignment conventions

During ports, first mirror the Lean 3 / Mathlib3 file layout and keep the Lean 4 file close to the source in order and structure. Preserve names when possible, add `#align` for renamed public declarations near the target declaration, and do not `#align` private helpers.

```lean
theorem foo_bar : ... := ...
#align old_namespace.foo_bar foo_bar
```

731. Search for existing API before adding new declarations

Before proving a new theorem or defining a new object, check whether it already exists in Mathlib, Lean, or Std, or whether a more general result already covers it. Reuse existing API instead of duplicating it.

732. Use import-minimization tools during development

Use tools such as `#min_imports`, `#minimize_imports`, or `lake exe shake` to check that the import list is minimal. Keep the final file clean according to project practice.

733. Prefer existing files; create new ones only when justified

Add small or moderate extensions to an existing file when possible. Create a new file only when the material is substantial, self-contained, or would otherwise improve dependency structure or discoverability.

734. Keep files mathematically cohesive

Do not leave declarations in a file merely because they were first needed there. If a result is not really about the file’s subject, move it to a better thematic home.

735. Use canonical import paths and exact casing

Import each module at most once, using its full canonical Mathlib path with exact on-disk capitalization. Do not use outdated, shortened, duplicated, or case-mismatched import paths.

736. Keep declarations in the appropriate namespace

Define declarations in the namespace of the main structure or concept they concern. Use `_root_` only for genuinely root-level declarations.

```lean
namespace TopologicalSpace
theorem foo ... := ...
end TopologicalSpace

theorem _root_.my_global_theorem := ...
```

737. Put tests and non-library material outside core library files

Do not leave regression tests, tactic tests, exploratory `example`s, scripts, or counterexamples in production `Mathlib` files. Put them in the appropriate dedicated locations such as test directories, `MathlibTest`, `Counterexamples`, `Archive`, or `scripts/`.

738. Place instances in the earliest natural module

Define typeclass instances in the earliest reasonable file where all required definitions are available and where the instance conceptually belongs. Do not force heavy imports into weaker files just to host an instance.

739. Keep `Defs` files minimal and foundational

Use `*.Defs` files for core definitions and only the minimal supporting theory needed for later definitions. Move theorem-heavy API, substantial proofs, and heavier imports to `Basic` or later files.

740. Reuse surrounding section variables and shared setup

Reuse variables and assumptions already in scope instead of restating them in every theorem. Put shared `variable`, `open`, and `open scoped` declarations near the top of the relevant file or section, not scattered throughout the file.

741. Provide compatibility shims for moved modules when needed

If a module is moved, split, or replaced, leave a thin file at the old path that imports the new location or uses the standard deprecation mechanism. Preserve downstream import paths during transitions when project policy expects it.

742. Order declarations by dependency and strength

Place foundational lemmas before results that use them, and weaker-assumption sections before stronger-assumption sections. For example, `PartialOrder` material should come before `LinearOrder`-specific API.

743. Avoid explicit `Init` imports unless genuinely needed

Do not add explicit `Init.*` imports for things Lean already provides by default. Import a specific `Init` module only when it is truly required.

744. Register new or renamed files with project tooling

When adding, removing, renaming, or splitting files, update generated umbrella imports and build registration using the project tooling, for example `lake exe mk_all`, rather than manual edits. Ensure the new module is reachable from the build graph.

745. Refactor shared material to avoid bad dependency edges

If placement would create an import cycle or require an earlier file to import a later one, split out the common low-level material into a separate earlier file. Do not solve dependency problems with broader or backward imports.

746. Add focused tests for new tactic or extension behavior

For changes such as tactic registrations, positivity extensions, syntax extensions, or custom attributes, add a small dedicated test so the new behavior is exercised explicitly. Follow existing nearby test patterns and keep test imports minimal.

747. Import syntax, notation, and attribute providers before use

If a file uses custom notation, syntax extensions, parser commands, or custom attributes, import the module that defines them before the first use. Many parser or attribute errors are just missing-import errors.

748. Use `public import` only for intentional re-exports

Default to ordinary `import`. Use `public import` only when downstream users should receive that API by importing the current file.

749. Keep umbrella files as import-only entrypoints

A file like `Foo.lean` that serves as a directory entrypoint should mainly aggregate or re-export underlying modules such as `Foo/Basic.lean`. Put substantial definitions and proofs in the underlying files, not in the umbrella file.

750. Match local naming conventions

Choose declaration names that follow the patterns already used nearby and in the target namespace. Avoid ad hoc names that clash with established Mathlib naming.

751. Generalize first, then choose the file

State results with the weakest appropriate assumptions, and place them in the file matching that generality. For example, a lemma needing only `[Monoid α]` should not live in a `Group` file.

752. Put `@[simp]` lemmas and aliases in the core API location

Place simp lemmas in the file where users naturally import the corresponding definition, usually right after that definition. Put `alias` and deprecated aliases immediately next to the original theorem.

753. Keep imports at the top in standard order

Put all imports at the top of the file. Use the standard header order: copyright header, then `module` if present, then imports, then the module docstring, then code.

754. Keep notation and syntax in low-import, appropriately scoped files

Place broadly used notation or syntax declarations in lightweight files so they are available early without dragging in heavy theory. Scope specialized notation when possible instead of making it global.

755. Separate moves, renames, and deprecations from substantive edits

When reorganizing files, prefer a pure move or rename first and content changes afterward. This keeps review, git history, and blame much clearer.

756. Quarantine deprecated or transitional API

If deprecated names or wrappers would clutter an active file, move them to a dedicated deprecated section or file. Keep the live API clean while preserving migration paths.

757. Keep organizational PRs incremental and focused

Treat file organization as part of API design and change it deliberately in small, reviewable steps. Prefer focused PRs over large reshuffles.

758. Use `inferInstanceAs` for definitionally inherited instances

When an instance for a derived object is definitionally the same as an existing one, define it via `inferInstanceAs` rather than naming a deep implementation detail.

```lean
instance : Foo (Bar α) := inferInstanceAs (Foo α)
```

759. Keep module docstrings aligned with actual contents

The file-level docstring should accurately describe what the file contains and, when relevant, why it is organized that way. If placement is non-obvious because of dependency constraints, explain that briefly.

760. Separate declarations cleanly and use headings for major structure

Leave a blank line between top-level declarations. In larger files, organize major parts with section headings such as `/-! #

# other

761. Name lemmas from outermost to innermost structure

When naming lemmas after expressions, follow the application structure from outermost to innermost, typically left-to-right. Keep standard exceptions only where the library already has a clear convention, such as some predicate names appearing last.

762. Keep PR metadata synchronized with the actual change

If the scope of a PR changes, update the title, commit message, and summary to match what the PR now does. In particular, if user-visible behavior or documentation changes, the metadata should describe that final result accurately.

763. Interpret type-directed rewrite notation from the expected type

For notation such as `↧`, determine its meaning from the expected type. Inspect the target, identify the relevant conversion map such as an `.of...` function, and apply that interpretation rather than guessing from syntax alone.

764. Inspect generated terms and exact errors when debugging

When debugging elaboration, coercions, or proof-state issues, inspect what Lean actually produced instead of guessing. Use tools like `#where`, `#check`, and options such as `set_option pp.natLit true`; when asking for help, quote Lean’s full error message verbatim rather than paraphrasing it.

```lean
set_option pp.natLit true in
#check someTerm
```

765. Use standard PR and commit title format

Write PR and commit titles in the project’s conventional format, such as `feat: ...`, `fix: ...`, `refactor: ...`, or `chore: ...`. Make the summary technically specific, avoid repository path prefixes like `Mathlib/`, and for ports use forms like `feat: port Module.Name`.

766. Apply PR labels only when they communicate actionable workflow state

Use labels sparingly and only when they indicate a concrete status or next action. For example, use `WIP` only for genuinely in-progress work, `awaiting-CI` only when the code is otherwise ready, and specialized labels like `meta` only when they truly apply.

767. Link prior discussion and keep follow-up in the relevant thread

If a PR continues an earlier design discussion, link the relevant Zulip thread or prior discussion in the PR. Continue follow-up in that same thread rather than cross-posting into unrelated review discussions.

768. Use scoped or otherwise disambiguated notation

When introducing notation that could clash with existing notation or concepts, avoid global ambiguous notation. Prefer `scoped notation`/`scoped infix` or another explicit disambiguation so parsing and error messages stay predictable.

```lean
scoped notation "‖" x "‖ₑ" => Euclidean.norm x
```

769. Prevent accidental global instances

Do not introduce global instances unless they are canonical and intended everywhere. Prefer `scoped instance` or `local instance` when the instance is only meant to apply in a limited context.

770. Use `Π` for type-valued dependent function types

Prefer `Π` when the quantified expression is type-valued rather than proposition-valued. Reserve `∀` for propositions.

```lean
theorem foo : (Π n : ℕ, Fin n → Nat) := ...
```

771. Use reducibility terminology precisely

Do not call something “opaque” unless you mean Lean’s actual notion of opacity. If you mean a different reducibility behavior, say so explicitly, such as `reducible`, `semireducible`, or `irreducible`.

772. Do not overinterpret internal `simp` or discrimination-tree debug output

When debugging `simp`, do not treat implementation-specific discrimination-tree keys or `no_index` artifacts as semantically meaningful. Focus on the actual rewrite lemmas and whether they transform the goal you care about.

773. Prioritize correct `simp` normal forms over vague “performance” explanations

If an issue is really that expressions simplify to a bad normal form, describe and fix it as a `simp`/normal-form problem rather than as runtime performance. Distinguish representation choices that affect rewriting from claims about execution speed.

774. Do not use `Fact` to make typeclass search prove arbitrary logic

Use `Fact` only for simple isolated assumptions that naturally behave like data carried by typeclass search. Do not rely on `Fact` instances as a general-purpose theorem prover for first-order logical goals.

```lean
-- acceptable
variable [Fact (0 < n)]

-- avoid designing APIs that expect typeclass search to reconstruct large proofs
```

775. Align changes with the intended existing API

If a proposed change comes from misreading the current API, revise the change to fit the intended abstraction rather than patching around the misunderstanding. Prefer the established general API when that is the library design.

776. Keep PRs small, focused, and conceptually split

Do not combine unrelated cleanups, refactors, and new lemmas in one PR. Split large changes into small conceptual units so they are easier to review, test, and merge.

777. Leave explicit TODOs only for concrete deferred work

Add `TODO` comments when there is a specific follow-up action that is genuinely being deferred and might otherwise be forgotten. Do not use TODOs for vague uncertainty or unspecified future improvements.

778. Do not merge specialized changes without qualified review

Avoid merging code in specialized mathematical or architectural areas unless someone knowledgeable can validate both correctness and API design. Lack of qualified review is itself a reason to wait.

779. Verify whether a configuration change affects source files or only editor display

Before enforcing an editor or configuration setting, check whether it changes actual file contents or only local presentation. Do not treat display-only settings as repository formatting requirements.

780. Review shell code according to how it is actually executed

Only raise shell-injection concerns when code actually constructs shell-parsed commands, such as through `eval` or `sh -c`. Otherwise, review the real hazards for shell code, especially unquoted expansions, globbing, and word splitting.

781. Do not run bare `lake update`

Do not run `lake update` without the intended package arguments. A bare `lake update` can update dependencies broadly and cause unrelated breakage.

782. Make diagnostics precise and allow justified suppressions

Linter messages, review diagnostics, and automated checks should describe the actual problem directly, not a misleading proxy. If you add an automated check, provide a way to suppress it in justified cases because false positives will occur.

# performance

783. Cache typeclass synthesis outside hot paths

Do not repeatedly call `synthInstance` or trigger equivalent instance search inside tight loops, recursive numeral code, tactic inner loops, or simp-heavy rewriting. Synthesize once, bind it, and reuse it; if needed, pass the dictionary explicitly.

```lean
-- Bad
for x in xs do
  let inst ← synthInstanceQ (MyClass α)
  ...

-- Better
let inst ← synthInstanceQ (MyClass α)
for x in xs do
  ...
```

784. Prefer specialized lemmas and implementations over generic abstractions when performance matters

Use specialized APIs and lemmas for the concrete type or property at hand instead of routing through more general machinery that introduces extra kernel reduction, typeclass search, or conversions. Typical examples are `Fin`-specific lemmas over generic `Fintype` arguments, or more direct injectivity/surjectivity lemmas over broader abstractions.

785. Cache expensive intermediate results instead of recomputing them

If a nontrivial expression, proof, or computed object is used more than once, bind it with `let`, `have`, or a `match h : ... with` / `=>`-style sharing pattern rather than rebuilding it. This includes repeated normalization, repeated typeclass-driven constructions, and expensive computed data such as matrix entries or other large structured values.

```lean
match h : expensive x with
| v => ...
```

786. Prefer direct expression construction over `mkAppM` in hot metaprogramming code

Avoid `mkAppM`/`mkAppOptM` in performance-critical loops when the function, universes, and argument types are already known. Prefer `mkApp`, `mkAppN`, `mkConst`, or more specific constructors to avoid unnecessary unification and inference overhead.

```lean
-- Better in a hot path
let e := mkAppN (mkConst ``MyStruct.mk [u]) #[α, a, b]
```

787. Avoid expensive coercions, wrapper projections, and non-definitional structure reuse

When a stronger structure is not definitionally an extension of the weaker one, do not rely on automatic coercions, unpack/repack projections, or rebuilding intermediate structures repeatedly. Work directly with the underlying fields/components, and in instances assign fields explicitly when that avoids elaboration or unification overhead.

788. Override fields locally instead of changing reducibility of shared definitions

If a standard definition is intentionally non-reducible and making it reducible would hurt performance elsewhere, do not change the global definition just to speed up one use case. Define a local instance/object with the needed fields overridden instead.

789. Be careful with `@[simp]` lemmas and rewrites that force extra instance search

Do not add or rely on simp rewrites that require synthesizing substantial typeclass evidence on each rewrite attempt. If a rewrite triggers expensive searches such as `FunLike`, `ZeroHomClass`, or similar class inference, prefer a formulation that avoids that cost or keep the rewrite more localized.

790. Minimize conversions between optimized internal representations and `Expr`

In tactics, simprocs, and metaprograms, keep data in the optimized internal representation for as long as possible and convert only at the boundary where an `Expr` is actually needed. Repeated back-and-forth conversion wastes expression-building time and allocations.

791. Require evidence before adding metadata-heavy simproc or checker plumbing

Do not introduce metadata threading, simproc plumbing, or similar infrastructure on a hot path without evidence that the overhead is acceptable. Prefer a prototype or benchmark first, especially if the design forces extra data to be passed through many calls.

792. Design checkers, linters, and environment extensions to be incremental

Process only newly introduced or changed declarations when possible rather than rescanning the entire environment on every run. Incremental designs are strongly preferred for PR-facing tools and persistent environment extensions.

---
