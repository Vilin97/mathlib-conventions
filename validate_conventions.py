"""Validate conventions for outdatedness.

Sends each category's FINAL conventions to GPT-5.4 along with Lean 3→4 migration
references, asking it to flag any that reference deprecated patterns.

Usage:
  python validate_conventions.py data/conventions_FINAL.md
  python validate_conventions.py data/conventions_FINAL.md --output data/conventions_validated.md
"""

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LEAN3_CONTEXT = """
## Key Lean 3 → Lean 4 changes that make conventions outdated:

### Syntax
- λ x, → fun x => (or fun x ↦)
- Π x, → ∀ x, or (x : ...) →
- { field := val, ..parent } → { parent with field := val }
- match uses => not :=, no end keyword
- (+ n) → (· + n)
- Whitespace-sensitive blocks instead of begin/end

### Tactics renamed/removed
- cases → cases' (Lean 3 version), Lean 4 has its own cases
- induction → induction' (Lean 3 version)
- split → constructor
- split_ifs → split
- library_search → exact?
- squeeze_simp → simp?
- suggest → apply?
- finish → aesop
- refl → rfl (as a tactic)
- intros → intro
- by_contradiction → by_contra
- repeat → repeat'
- Commas between tactics removed (use newlines or semicolons)
- {} goal blocks → · (cdot) focus

### Tactic semantics changed
- ; now does what , did in Lean 3
- <;> now does what ; did in Lean 3
- _ vs ?_ distinction (implicit arg vs new subgoal)
- refine in Lean 4 is different from Lean 3 refine (Lean 3's is refine')

### Naming conventions
- snake_case for proofs/theorems
- UpperCamelCase for types/propositions
- lowerCamelCase for terms/functions
- Acronyms as coherent units (not ALL_CAPS)

### Variable handling
- include/omit removed
- All variables auto-included (including named instances)
- autoImplicit on by default (Mathlib disables it)

### Attributes
- @[simp, priority 100] → @[simp 100] or @[simp high/low]

### Imports
- import data.nat.basic → import Mathlib.Data.Nat.Basic
- #align removed (was for Lean 3→4 porting)

### Recent Lean 4 / Mathlib changes (2024-2026)
- grind tactic added (powerful automation)
- omega now in core
- Prefer ↦ over => in fun/match (Mathlib convention)
- Prefer induction/cases over induction'/cases' (native Lean 4 versions)
- @[deprecated] with since field required
- public import syntax
- module keyword for files
"""

VALIDATE_PROMPT = """You are an expert in Lean 4 / Mathlib. You are given a list of coding conventions and a reference of Lean 3→4 changes.

Your task: Review each convention and flag any that are OUTDATED or reference deprecated patterns.

For each convention, output one of:
- VALID: [number]. [title] — the convention is current and correct
- OUTDATED: [number]. [title] — [brief explanation of what's wrong]
- UPDATE: [number]. [title] — [the corrected version of the convention]

Only flag conventions that are genuinely outdated. Most conventions about general coding style, API design, and proof structure are timeless and should be marked VALID. Focus on:
1. References to Lean 3 syntax or tactics
2. References to removed/renamed features
3. Advice that contradicts current Lean 4 / Mathlib best practices
4. References to porting-era tools (#align, mathport) that are no longer relevant

Be conservative — when in doubt, mark VALID."""


def validate_file(client, input_path, output_path):
    """Validate conventions in a markdown file."""
    with open(input_path) as f:
        content = f.read()

    # Split into categories
    categories = re.split(r'^# ', content, flags=re.MULTILINE)
    header = categories[0]  # everything before first #
    categories = categories[1:]  # actual category sections

    results = []
    total_valid = 0
    total_outdated = 0
    total_updated = 0

    for cat_block in categories:
        lines = cat_block.strip().split('\n')
        cat_title = lines[0].strip()
        cat_content = '\n'.join(lines[1:]).strip()

        if not cat_content or '---' == cat_content.strip():
            results.append(f"# {cat_title}\n\n{cat_content}")
            continue

        print(f"Validating: {cat_title}...", end=" ", flush=True)

        resp = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {"role": "system", "content": VALIDATE_PROMPT + "\n\n" + LEAN3_CONTEXT},
                {"role": "user", "content": f"Category: {cat_title}\n\n{cat_content}"},
            ],
            max_completion_tokens=16000,
            temperature=0.1,
        )

        result = resp.choices[0].message.content or ""
        valid = result.count("VALID:")
        outdated = result.count("OUTDATED:")
        updated = result.count("UPDATE:")
        total_valid += valid
        total_outdated += outdated
        total_updated += updated

        print(f"{valid} valid, {outdated} outdated, {updated} updated")
        results.append(f"# {cat_title}\n\n{result}")

    # Write output
    with open(output_path, "w") as f:
        f.write(header)
        for r in results:
            f.write(r + "\n\n---\n\n")

    print(f"\nTOTAL: {total_valid} valid, {total_outdated} outdated, {total_updated} updated")
    print(f"Written to: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input conventions markdown file")
    parser.add_argument("--output", help="Output file (default: input with _validated suffix)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "_validated")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    validate_file(client, input_path, output_path)


if __name__ == "__main__":
    main()
