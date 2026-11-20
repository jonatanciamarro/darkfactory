---
trigger: always_on
description: Mandatory living state synchronization protocol via state.md. Agents MUST read state.md at session start and update it before session end.
---
# State Tracking Protocol (`state.md`)

This repository enforces a strict, living state continuity protocol using `state.md` located at the root of the project.

## Invariants & Requirements

### 1. Session Start Invariant (READ FIRST)
At the start of **any new session, user interaction, or new task**, the AI agent **MUST ALWAYS read `state.md`** first.
- Understand the exact current state of the project.
- Review recent commits and work completed in prior sessions.
- Check the remaining backlog, pending tasks, and immediate next steps.
- Align upcoming actions directly with the roadmap recorded in `state.md`.

### 2. Session Turnover Invariant (UPDATE BEFORE COMPLETION)
Before marking any task complete, opening a PR, or concluding a session, the AI agent **MUST update `state.md`**:
- **Health & Metrics**: Refresh test pass rates, lint status, type check status, and security scanner output.
- **Recent Work**: Record exactly what was implemented, fixed, or modified in the current session.
- **Pending Tasks**: Move finished items out of backlog and note any newly discovered requirements or technical debt.
- **Next Steps**: Clearly state what the next session or developer should tackle.
- **Modification History**: Append a new entry to the changelog table at the end of `state.md`.

### 3. Source of Truth
- `state.md` is the authoritative living pulse of the project for agent sessions.
- Never let `state.md` become stale or out of sync with actual git commits, code changes, or test outcomes.
