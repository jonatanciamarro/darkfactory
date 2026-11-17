---
name: plan-v2
description: Corporate Autonomous Implementation Planner. Computes blast-radius impact analysis, constructs topological execution DAGs, mandates zero-downtime expand/contract patterns, and outputs TDD seeds for the corporate pipeline.
---

# Plan v2.0 (`plan-v2`)

A skill **`plan-v2`** é o motor de planejamento corporativo de nível Staff/Principal Engineer. Ela transcende o `/plan` original ao substituir listas de tarefas estáticas por **análise de raio de impacto (Blast Radius)**, **grafos de dependência DAG**, **estratégia Expand/Contract para migrações** e **procedimentos explícitos de rollback**.

---

## 🎯 Quando Ativar
- Invocada via slash command `/plan-v2` antes de qualquer alteração média/grande.
- Acionada nativamente na **Fase 1 (Alinhamento & Escopo)** do `corp-pipeline`.

---

## 🚀 Os 4 Pilares da V2

```text
       ┌────────────────────────────────────────────────────────┐
       │             1. BLAST RADIUS & CALL-GRAPH               │
       │ (Mapeia quem consome o arquivo antes de alterá-lo)     │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │             2. GRAFO DE EXECUÇÃO DAG                   │
       │ (Tarefas com ordem topológica estrita e validação)     │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │           3. ZERO-DOWNTIME (EXPAND / CONTRACT)         │
       │ (Mudanças aditivas primeiro, corte de tráfego seguro)  │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │         4. TDD MATRIX & PROCEDIMENTOS DE ROLLBACK      │
       │  (Alimenta a Fase 2 do corp-pipeline com testes RED)   │
       └────────────────────────────────────────────────────────┘
```

---

## 📋 As 5 Seções do Plano Corporativo

Todo plano gerado pelo `plan-v2` obedece rigorosamente à seguinte estrutura:

1. **Blast Radius & System Impact Analysis**: Arquivos alvo, consumidores secundários mapeados e nível de risco sistêmico (1 a 10).
2. **Dependency Graph & Execution DAG**: Lista de tarefas ordenadas topologicamente com comandos de validação automatizados.
3. **Zero-Downtime & Expand/Contract Strategy**: Como a mudança será feita sem quebrar produção nem travar tabelas de banco de dados.
4. **Shift-Left TDD Contracts Matrix**: Lista de cenários de teste que devem ser escritos no estado RED antes da codificação.
5. **Rollback & Disaster Recovery Procedures**: Ação cirúrgica de rollback por tarefa para contenção de falhas.
