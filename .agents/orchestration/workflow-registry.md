# Registro de Workflows Operacionais (`workflow-registry.md`)

> **Catálogo de Workflows Determinísticos do Workspace**  
> *Mapeamento dos 16 workflows padronizados disponíveis em `.agents/workflows/`.*

---

## 1. Workflows de Governança, Qualidade & Pre-Flight

| Workflow | Slash Command | Finalidade | Portões / Validações | Arquivo de Definição |
|---|---|---|---|---|
| `preflight` | `/preflight` | Auditoria completa de pre-flight local: Ruff, Mypy, Pytest e Secret Scanner. | 0 erros em todos os 4 cheques. | [.agents/workflows/preflight.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/preflight.md) |
| `quality-gate` | `/quality-gate` | Auditoria e fiscalização de conformidade arquitetural e invariantes corporativos. | Validação estrita de contratos Pydantic e cobertura de testes. | [.agents/workflows/quality-gate.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/quality-gate.md) |
| `security-scan` | `/security-scan` | Auditoria estática e dinâmica de credenciais, chaves e vulnerabilidades. | Scanner de segredos + revisão OWASP. | [.agents/workflows/security-scan.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/security-scan.md) |
| `test-coverage` | `/test-coverage` | Análise e relatório de cobertura de código (`pytest-cov`). | Cobertura global mínima de 80% (meta: 90%+). | [.agents/workflows/test-coverage.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/test-coverage.md) |

---

## 2. Workflows de Ciclo de Vida e Entrega de Software

| Workflow | Finalidade | Sequência Operacional | Arquivo de Definição |
|---|---|---|---|
| `feature-dev` | Desenvolvimento ponta a ponta de novas funcionalidades corporativas. | Requisitos → Gate 1 (ADR/Plano) → TDD RED → Implementação GREEN → Pre-Flight → Gate 2 (PR). | [.agents/workflows/feature-dev.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/feature-dev.md) |
| `orch-add-feature` | Orquestração multi-agente para novas features, delegando pesquisa, TDD e revisão. | Delegação estruturada com isolamento de contexto e checkpoints. | [.agents/workflows/orch-add-feature.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/orch-add-feature.md) |
| `orch-fix-defect` | Correção determinística de defeitos e bugs reportados. | Reprodução obrigatória em teste falho (RED) antes da alteração de código. | [.agents/workflows/orch-fix-defect.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/orch-fix-defect.md) |
| `orch-refine-code` | Refatoração arquitetural com garantia matemática de não-regressão. | Testes verdes antes da refatoração → alteração estrutural → testes verdes mantidos. | [.agents/workflows/orch-refine-code.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/orch-refine-code.md) |
| `build-fix` | Recuperação cirúrgica e autocorreção de falhas de build/lint/testes. | Diagnóstico de traceback → isolamento → máximo de 3 tentativas cirúrgicas. | [.agents/workflows/build-fix.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/build-fix.md) |
| `checkpoint` | Gerenciamento de checkpoints FSM e rollback determinístico de estados no DAG. | Salvamento de snapshot de estado, restauração e histórico de transições. | [.agents/workflows/checkpoint.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/checkpoint.md) |

---

## 3. Workflows de Planejamento, Revisão e Documentação

| Workflow | Slash Command | Finalidade | Arquivo de Definição |
|---|---|---|---|
| `plan` | `/plan` | Planejamento técnico aprofundado com análise STRIDE e matriz de trade-offs. | [.agents/workflows/plan.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/plan.md) |
| `review` | `/review` | Revisão sênior de código focada em arquitetura, imutabilidade e manutenibilidade. | [.agents/workflows/review.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/review.md) |
| `python-review` | `/python-review` | Revisão técnica especializada em Python 3.10/3.11+, tipos estritos e PEP 8. | [.agents/workflows/python-review.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/python-review.md) |
| `refactor-clean` | `/refactor-clean` | Higienização de imports, remoção de dead code e alinhamento com padrões PEP 8. | [.agents/workflows/refactor-clean.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/refactor-clean.md) |
| `update-docs` | `/update-docs` | Sincronização perene de documentação técnica, ADRs e histórico de decisões. | [.agents/workflows/update-docs.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/update-docs.md) |
| `ecc-guide` | `/ecc-guide` | Guia operacional interativo do ecossistema e componentes instalados. | [.agents/workflows/ecc-guide.md](file:///e:/projcts/corporate%20engineer/.agents/workflows/ecc-guide.md) |

---

## 4. Invariantes de Execução

1. **Nunca executar workflows cegamente**: O orquestrador deve checar os pré-requisitos e dependências antes de disparar um workflow.
2. **Respeitar os Gates Humanos**: Workflows com confirmação explícita (Gate 1 e Gate 2) jamais devem prosseguir sem autorização do usuário.
