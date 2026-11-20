# Corp-Pipeline Master Capability Registry (`capability-registry.md`)

> **Autonomous Capability Intelligence & Routing Registry**  
> *Authoritative mapping of all agents, skills, workflows, tools, and integrations available in `corporate-engineer`.*

---

## 1. Visão Geral da Arquitetura

O **Corp-Pipeline** opera como a camada permanente de orquestração e inteligência do projeto. Este registro centraliza a descoberta de recursos, estabelece a matriz de roteamento inteligente e mapeia as interfaces operacionais de todo o ecossistema.

```text
                               [REQUISIÇÃO DO USUÁRIO]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Corp-Pipeline Master Orchestrator  │
                      │  (Planejamento, Roteamento & Gates)   │
                      └──────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌──────────────┐                 ┌──────────────┐                 ┌──────────────┐
│    Agentes   │                 │    Skills    │                 │  Workflows   │
│ Especialistas│                 │  Reutilizáveis│                │  Operacionais│
└───────┬──────┘                 └───────┬──────┘                 └───────┬──────┘
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                      ┌───────────────────────────────────────┐
                      │ Ferramentas, MCPs, APIs & Automações  │
                      └──────────────────┬────────────────────┘
                                         │
                                         ▼
                             [Pre-Flight & Validação]
```

---

## 2. Matriz de Roteamento Inteligente

O orquestrador seleciona automaticamente a menor combinação efetiva de recursos para cada tarefa, seguindo a matriz abaixo:

| Natureza da Tarefa | Recurso Primário | Recurso Secundário / Apoio | Validação Mandatória |
|---|---|---|---|
| **Nova Feature Corporativa** | `/corp-pipeline` | Subagentes `architect`, `tdd-guide`, `code-reviewer` | Gate 1 (ADR + Plano), TDD (RED→GREEN), Gate 2 |
| **Arquitetura & Design de Contratos** | Subagente `architect` | Skills `grill-me_v2`, `plan_v2`, `api-design` | Síntese de ADR em `docs/adr/` e Pydantic DTOs |
| **Implementação e Testes TDD** | Subagente `tdd-guide` | Skills `tdd-workflow`, `python-testing` | Teste RED inicial, GREEN, 80%+ cobertura |
| **Revisão de Código & Padrões** | Subagente `code-reviewer` | Subagente `python-reviewer`, skill `python-patterns` | Ruff, Mypy, checklist de imutabilidade |
| **Auditoria de Segurança & OWASP** | Subagente `security-reviewer` | Skill `security-review`, script `secret_scanner.py` | 0 segredos expostos, conformidade OWASP |
| **Indexação AST & Code Intelligence** | Subagente `rag-pipeline-reviewer` | Módulo `src/corporate_engineer/rag/` | PBT com Hypothesis, integridade de grafos |
| **Correção Rápida de Build/Testes** | Subagente `build-error-resolver` | Workflow `build-fix.md` | Máximo 3 iterações cirúrgicas |
| **Refatoração Segura** | Subagente `refactor-cleaner` | Workflow `orch-refine-code.md` | Preservação comportamental com testes verdes |
| **Conexão e Ferramentas MCP** | Módulo `mcp/` & CLI `mcp` | Skill `mcp-server-patterns` | Ping, schema validation, fallback robusto |
| **Pre-Flight e Governança** | Workflow `preflight.md` | Script `secret_scanner.py`, `quality/gate.py` | 0 erros em Ruff, Mypy, Pytest e Scanner |

---

## 3. Classificação de Status Operacional

Cada capacidade catalogada possui um status operacional rigorosamente verificado:

- `AVAILABLE`: Testado e pronto para execução imediata no ambiente atual.
- `AVAILABLE_WITH_RESTRICTIONS`: Operacional com dependências ou limitações documentadas.
- `REQUIRES_AUTHENTICATION`: Necessita de tokens de autenticação ou chaves de API.
- `REQUIRES_APPROVAL`: Operação sensível que requer confirmação explícita do usuário (ex: push, PR, escrita destrutiva).
- `UNAVAILABLE`: Não suportado ou com dependência faltante no host.
- `UNKNOWN`: Descoberto, mas ainda não testado empiricamente.
- `DEPRECATED`: Mantido temporariamente para compatibilidade, com substituto designado.

---

## 4. Sub-Registros Especializados

Para detalhamento técnico completo de cada categoria de recursos, consulte os sub-registros:

1. [Subagentes Especializados](file:///e:/projcts/corporate%20engineer/.agents/orchestration/agent-registry.md) (`agent-registry.md`)
2. [Skills e Conhecimento Reutilizável](file:///e:/projcts/corporate%20engineer/.agents/orchestration/skills-registry.md) (`skills-registry.md`)
3. [Workflows e Pipelines](file:///e:/projcts/corporate%20engineer/.agents/orchestration/workflow-registry.md) (`workflow-registry.md`)
4. [Ferramentas Nativas e CLI](file:///e:/projcts/corporate%20engineer/.agents/orchestration/tool-registry.md) (`tool-registry.md`)
5. [Integrações, MCPs e Plugins](file:///e:/projcts/corporate%20engineer/.agents/orchestration/integration-registry.md) (`integration-registry.md`)
6. [Backlog Contínuo de Melhorias](file:///e:/projcts/corporate%20engineer/.agents/orchestration/improvement-backlog.md) (`improvement-backlog.md`)

---

## 5. Diretriz de Não-Suposição

O orquestrador **NUNCA** deve inventar nomes de ferramentas, arquivos de configuração ou status de execução. Toda capacidade deve ser descoberta, registrada e testada de acordo com as permissões reais do ambiente.
