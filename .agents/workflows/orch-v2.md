---
description: Run an advanced multi-vector orchestration scan across DarkFactory domains, subagents, and tools.
argument-hint: "[task description]"
---

# /orch-v2 - Master Autonomous Orchestrator v2.0

Synthesize a comprehensive, multi-vector execution plan for the requested task using the Staff-level Orchestrator v2.0 engine.

## Execution Sequence:
1. **Semantic Intent Classification**: Evaluate query across DarkFactory's 7 canonical domains (Nolan Storytelling, Historical Research, Audio Engineering, Video T2V, Cinema Dashboard, Corporate Engineering, Compliance).
2. **Affinity & Capability Scoring**: Calculate match scores (0.00 to 1.00) across all available subagents, skills, and tools.
3. **Fallback Resolution**: Inject deterministic contingencies for API timeouts, quota caps, and browser bottlenecks.
4. **DAG Execution Synthesis**: Output execution steps and emit the canonical operational badge:
   `🎯 Orquestrador: [Skill: <skill> | Agente: <agente> | Ferramenta: <ferramenta>]`
