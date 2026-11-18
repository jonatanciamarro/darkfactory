---
name: orchestrator-v2
description: Master Autonomous Orchestrator v2.0 for DarkFactory. Real-time multi-vector semantic routing across subagents, skills, fallback matrices, and DAG execution pipelines.
---

# Master Autonomous Orchestrator v2.0 (`/orch-v2`)

The **Orchestrator v2.0** is DarkFactory's cognitive routing intelligence, elevating resource dispatch to a Staff / Principal Engineer tier. It replaces passive heuristics with real-time multi-vector semantic scoring, deterministic fallback matrices, and native integration with the Corporate 5-Phase Pipeline, Plan v2.0, and Grill-Me v2.0.

---

## 🎯 When to Activate
- Automatically activated via the `/orch-v2` slash command.
- Automatically invoked when triaging complex multi-stage tasks across the 5 documentary phases.
- Used to dynamically determine the optimal lead subagent, supporting skills, critical tools, and contingency fallbacks.

---

## 🧠 The 4-Pillar Multi-Vector Engine (`orchestrator_engine.py`)

```text
               [User Task / JIRA Prompt]
                           │
                           ▼
  [1. Semantic Intent Classifier (7 DarkFactory Domains)]
                           │
                           ▼
  [2. Multi-Vector Affinity Scoring (0.00 to 1.00)]
                           │
                           ▼
  [3. Deterministic Fallback Resolution (Zero-Downtime)]
                           │
                           ▼
  [4. Plan Synthesis & Topological DAG Hint Generation]
                           │
                           ▼
  [Operational Badge: 🎯 Orquestrador: [Skill | Agente | Ferramenta]]
```

### 1. The 7 Canonical DarkFactory Domains
1. **`NOLAN_STORYTELLING`**: 5-Act non-linear narrative, Kodak Vision3 70mm prompts, Walter Murch pacing, Crosscutting.
2. **`HISTORICAL_RESEARCH`**: Declassified archives (CIA/KGB), public domain records, fact-checking dossiers.
3. **`AUDIO_ENGINEERING`**: CosyVoice 3 narration, Kokoro fallback, Zimmer OST, Foley SFX, -14.0 LUFS / -1.0 dBTP.
4. **`VIDEO_SYNTHESIS_T2V`**: Google Flow (Veo 3.1 & Omni Flash), RunningHub ComfyUI / MiniMax H3, automated quarantine.
5. **`CINEMA_DASHBOARD`**: FastAPI Web SPA (:8502), auth cockpit, topic generator, production control.
6. **`CORPORATE_ENGINEERING`**: Corporate 5-phase pipeline, Shift-Left TDD, Plan v2 DAG, Grill-Me v2, AST freshness.
7. **`COMPLIANCE_AND_LEGAL`**: Green Dollar 100/100, EDSA fair use, Dispute Kit, SEO in 7 languages.

---

## 🛠️ Deterministic Fallback Matrix

| Production Domain | Primary Engine | Fallback Contingency | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **Video Generation** | Google Flow (Veo 3.1 & Omni Flash) | RunningHub MiniMax H3 / Wan 2.2 | Quota exhaustion, latency > 90s, or browser block |
| **Vocal Synthesis** | CosyVoice 3 (RunningHub API) | Kokoro-82M ONNX local (`bm_george`) | API timeout > 15s or 5xx server error |
| **Cinematic OST** | Flow Music (Lyria & Zimmer OST) | RunningHub MiniMax Music 3 | Session disconnect on flowmusic.app |
| **Documentary Script** | Nolan 5-Act Storyboard | Canonical 40-Scene Dossiê Template | Story validator score < 80.0 |
| **Engineering Tests** | Automated Pytest Suite | Syntax & Strict Typecheck (`py_compile` + `mypy`) | Missing venv dependencies |

---

## 🚀 CLI Usage & Automation

You can execute the engine directly from terminal or subprocess:

```powershell
# Sintetizar plano completo em texto
.\venv\Scripts\python .agents/skills/orchestrator-v2/scripts/orchestrator_engine.py --task "Renderizar takes no RunningHub com som Zimmer"

# Obter apenas a badge oficial de transparência
.\venv\Scripts\python .agents/skills/orchestrator-v2/scripts/orchestrator_engine.py --task "Escrever roteiro Nolan do ato 2" --badge-only

# Serialização em JSON para CI/CD ou consumo por subagentes
.\venv\Scripts\python .agents/skills/orchestrator-v2/scripts/orchestrator_engine.py --task "Criar teste unitário para auth_gate" --format json
```
