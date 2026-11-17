---
name: orchestrator-v2
description: Master Autonomous Meta-Orchestrator v2.0 with Dynamic Affinity Scoring, Multi-Agent Staged Chains, Circuit Breaker Fallbacks, and Autonomous Definition of Done (DoD) Verification.
---

# Master Orchestrator v2.0 (`orchestrator-v2`)

A skill **`orchestrator-v2`** é o cérebro central unificado de engenharia do DarkFactory e do ecossistema corporativo. Ela transcende a v1 ao abandonar regras de roteamento estáticas e introduzir **cálculo dinâmico de afinidade semântica**, **composição de cadeias em estágios multi-agente**, **circuit breakers contra esgotamento de quota** e **garantia autônoma de Definition of Done (DoD)**.

---

## 🎯 Quando Ativar
- Acionada nativamente em qualquer solicitação ou prompt complexo.
- Invocada via slash command `/orchestrator-v2`.

---

## 🚀 Os 4 Pilares da V2

```text
       ┌────────────────────────────────────────────────────────┐
       │             1. MOTOR DE AFINIDADE DINÂMICA             │
       │ (Calcula score semântico 0.0-1.0 para cada skill/agente)│
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │             2. CADEIAS EM ESTÁGIOS (STAGED)            │
       │    [grill-v2]  ──►  [plan-v2]  ──►  [corp-pipeline]    │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │           3. CIRCUIT BREAKER & FALLBACK ROUTING        │
       │ (Comutação transparente instantânea em caso de quota)  │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │         4. VERIFICAÇÃO AUTÔNOMA DE DEFINITION OF DONE  │
       │ (Barra saídas com testes quebrados ou violação git)    │
       └────────────────────────────────────────────────────────┘
```

---

## 🧭 O Fluxo de Execução Unificado da V2

1. **Triagem por Afinidade Semântica**:
   O motor avalia as palavras-chave e a complexidade da demanda, identificando se a tarefa é pontual (cirúrgica) ou requer um pipeline encadeado.

2. **Composição em Estágios**:
   Para novas features e refatorações, orquestra a tríade corporativa canônica:
   * **Estágio 1 (`grill-v2`)**: Interrogatório socrático nos 4 quadrantes e geração do ADR.
   * **Estágio 2 (`plan-v2`)**: Mapeamento do raio de impacto (blast radius) e construção do grafo DAG.
   * **Estágio 3 (`corp-pipeline`)**: Shift-Left TDD (RED), implementação GREEN e governança Git (Gate 2).

3. **Circuit Breakers Ativos**:
   Em caso de rate limits, latência ou instabilidade de modelos externos:
   * Síntese vocal: `CosyVoice` $\rightarrow$ `Kokoro-82M`.
   * Geração visual: `RunningHub` $\rightarrow$ `Local ComfyUI`.
   * LLMs / Agentes: `Subagente Externo` $\rightarrow$ `Execução Inline Resiliente`.

4. **Transparência Executiva**:
   Emite em cada turno o badge avançado de telemetria:
   `🎯 Orquestrador v2: [Modo: staged_pipeline | Cadeia: grill-v2 -> plan-v2 -> corp-pipeline | Fallback: Pronto | DoD: 100% Verified]`
