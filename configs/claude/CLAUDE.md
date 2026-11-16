# Global agent instructions

Guidelines for software development. Project-level CLAUDE.md files add to these, and win where they conflict. These rules favour care over speed; for trivial tasks, use judgment.

## 1. Think before coding

- State your assumptions explicitly. If something is unclear, stop, name what is confusing, and ask.
- If a request has several reasonable interpretations, present them instead of picking one silently.
- If a simpler approach exists, say so. Push back when warranted.
- Ask clarifying questions before implementing, not after mistakes.

## 2. Pick the best design, then write the least code for it

- Judge technical options by quality, simplicity, robustness, scalability and long-term maintainability. Development cost is not a good reason to choose a worse design.
- Build what was asked, nothing speculative: no extra features, no unrequested configurability, no abstractions for single-use code.
- Handle the failure modes that can really happen; skip error handling for impossible ones.
- If 200 lines could be 50, rewrite it. Ask: "Would a senior engineer call this overcomplicated?"

## 3. Keep changes focused

- Every line of the main change should trace directly to the request.
- Match the existing style, even if you would do it differently. Don't refactor, reword or reformat working code outside the task.
- Clean up your own mess: remove imports, variables and functions that your change made unused. Leave pre-existing dead code alone and mention it instead.
- Never manually edit CHANGELOG.md or files marked as auto-generated. Change their source or generator instead.

## 4. Fix real defects you come across

Focus applies to style and structure, not to things that are broken. When you see any of these, fix them even if your task didn't cause them:

- lint errors
- failing or flaky tests
- UI that clearly looks off (alignment, spacing, overflow, clipping, broken states)

Keep each such fix separate from the main change and report it clearly. If a fix is large or risky, describe it and ask first.

## 5. Bug fixes: reproduce first

1. Reproduce the bug end to end, as close as possible to how a user experiences it. This makes sure you have found the real problem, so the fix actually solves it.
2. Capture it in an automated test that fails for the right reason.
3. Fix it, then confirm both the test and the original end-to-end reproduction pass.

## 6. Goal-driven execution

Turn tasks into verifiable goals:

- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → reproduce it (section 5), then make the test pass.
- "Refactor X" → tests pass before and after.

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Loop until each check passes. When testing a product end to end, look at the real UI and be obsessed with pixel perfection. Report results honestly: say what was verified, what wasn't, and what failed.

## 7. Writing and git

- Never use the em dash (U+2014). Use a plain dash "-" instead.
- Never add your agent name as a co-author in commit messages.

---

These rules are working if diffs contain only intended changes (plus clearly separated defect fixes), designs rarely need rewriting for being overcomplicated, and questions come before implementation rather than after mistakes.
