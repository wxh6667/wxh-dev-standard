---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the frontier in one round and give your recommended answer to each. Then wait for the user's answers before the next round.

**Put every question to the user as a choice, not as prose.** When the host offers an interactive picker (Claude Code: `AskUserQuestion`), ask the frontier through it, so the user picks an option instead of typing an answer. One call carries up to 4 questions with 2–4 concrete options each:

- Recommended answer first, labelled `<option> (recommended)`, with the trade-off in that option's description.
- Single-select when the options are mutually exclusive; `multiSelect` when several can hold at once (e.g. "which of these constraints apply?").
- The user can still pick "Other" and answer freely.

The picker is capped at 4 questions per call and 4 options per question. When the frontier has more independent questions than one call holds, ask the first batch now and the rest once the user answers — never pull a dependent question forward to fill out a batch. Use the text form below when a question resists 2–4 discrete options, is genuinely open-ended, or the host has no picker.

Format a text round like so:

```
❓ **Q1** - **<question title>**: <question body>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), look it up directly, or delegate independent exploration when useful and supported; do not ask the user for facts available from the environment. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
