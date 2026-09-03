---
name: askfirst
description: Explore the codebase, ask at least 3 informed implementation questions, then implement the task autonomously. Use when invoked as /askfirst <task to be done>.
argument-hint: <thing you want done>
---

# Askfirst

The argument is a task the user wants done. Do NOT start implementing yet. Follow these phases in order, all in this turn:

## 1. Explore first

Do as much code exploration as needed to understand the task in the context of this codebase before asking anything: relevant files, existing patterns and conventions, integration points, prior art for similar features, and constraints (build system, tests, project rules). Use subagents for broad searches to keep context lean.

The point of exploring first is that your questions must be informed. Never ask something the code, git history, or project docs already answer.

## 2. Ask at least 3 questions

Ask the user **at least 3 questions** about the implementation using the AskUserQuestion tool, with concrete options grounded in what you found during exploration. Good question territory:

- Scope: what's in and out for this iteration
- Shape: API/UX/data-model choices where more than one design fits the codebase
- Tradeoffs surfaced by exploration (e.g. "there are two existing patterns for X here — follow which?")
- Edge-case and failure behavior
- Compatibility/migration expectations

Rules:
- Minimum 3 real questions. If you can only think of 2, explore deeper — the third question exists, you haven't found it yet.
- Don't pad with fake questions whose answer is obvious or that you could resolve yourself from the code.
- Prefer one AskUserQuestion call with multiple questions; ask a follow-up round if answers open new decisions.

## 3. Do it — autonomously

Once the answers are in, implement the task end to end in this same turn. Do NOT draft a plan, ask for approval, or check in before starting — the questions above were the check-in. Work in auto mode:

- Carry the work through completely: implement, build/test with the project's usual commands, and fix failures yourself.
- Don't stop to ask "should I proceed?" mid-implementation. Only stop for destructive/irreversible actions or a genuine scope change the answers didn't cover.
- Finish the turn with a summary of what was changed and how it was verified.
