# Registro de Agentes Especializados (`agent-registry.md`)

> **Catálogo de Agentes do Ecossistema Corp-Pipeline**  
> *Mapeamento de especializações, responsabilidades, modelos recomendados, ferramentas e critérios de ativação.*

---

## 1. Subagentes Especializados do Workspace (`.agents/agents/`)

| Identificador | Nome | Modelo | Status | Propósito & Ativação | Arquivo de Definição |
|---|---|---|---|---|---|
| `architect` | Enterprise Architect | `pro` | `AVAILABLE` | Design arquitetural, contratos DTOs formais via Pydantic v2, matriz de trade-offs e síntese de ADRs em `docs/adr/`. | [.agents/agents/architect.md](file:///e:/projcts/corporate%20engineer/.agents/agents/architect.md) |
| `planner` | Project & Task Planner | `pro` | `AVAILABLE` | Decomposição técnica de épicos em tarefas granulares, PRDs e planejamento por fases. | [.agents/agents/planner.md](file:///e:/projcts/corporate%20engineer/.agents/agents/planner.md) |
| `tdd-guide` | Shift-Left TDD Guide | `flash` | `AVAILABLE` | Condução do ciclo estrito TDD (RED→GREEN→IMPROVE) e geração de testes baseados em propriedades (PBT com Hypothesis). | [.agents/agents/tdd-guide.md](file:///e:/projcts/corporate%20engineer/.agents/agents/tdd-guide.md) |
| `code-reviewer` | Senior Code Reviewer | `pro` | `AVAILABLE` | Revisão geral de pull requests, conformidade com padrões de codificação, imutabilidade e boas práticas de engenharia. | [.agents/agents/code-reviewer.md](file:///e:/projcts/corporate%20engineer/.agents/agents/code-reviewer.md) |
| `python-reviewer` | Python Specialist Reviewer | `pro` | `AVAILABLE` | Auditoria detalhada de código Python 3.10/3.11+, tipagem estática rigorosa (`mypy`), linting (`ruff`) e performance. | [.agents/agents/python-reviewer.md](file:///e:/projcts/corporate%20engineer/.agents/agents/python-reviewer.md) |
| `security-reviewer` | Corporate Security Auditor | `pro` | `AVAILABLE` | Verificação de vulnerabilidades (OWASP), credenciais/segredos expostos, injeção, autorização e least privilege. | [.agents/agents/security-reviewer.md](file:///e:/projcts/corporate%20engineer/.agents/agents/security-reviewer.md) |
| `rag-pipeline-reviewer` | AST & RAG Pipeline Reviewer | `pro` | `AVAILABLE` | Auditoria de analisadores sintáticos AST (`ast_indexer.py`), grafos de herança, grafos de chamadas e code intelligence. | [.agents/agents/rag-pipeline-reviewer.md](file:///e:/projcts/corporate%20engineer/.agents/agents/rag-pipeline-reviewer.md) |
| `build-error-resolver` | Surgical Build & Test Resolver | `flash` | `AVAILABLE` | Diagnóstico veloz e autocorreção cirúrgica de falhas de build, linter e testes (limite estrito: 3 tentativas). | [.agents/agents/build-error-resolver.md](file:///e:/projcts/corporate%20engineer/.agents/agents/build-error-resolver.md) |
| `refactor-cleaner` | Safe Refactoring Specialist | `flash` | `AVAILABLE` | Limpeza e refatoração de código morto preservando 100% do comportamento funcional validado por testes. | [.agents/agents/refactor-cleaner.md](file:///e:/projcts/corporate%20engineer/.agents/agents/refactor-cleaner.md) |

---

## 2. Subagentes Nativos da Plataforma Antigravity

| Identificador | Modelo Padrão | Status | Descrição de Uso |
|---|---|---|---|
| `self` | `inherit` | `AVAILABLE` | Subagente com herança completa de ferramentas e permissões do agente principal, para execução em contexto limpo e isolado. |
| `research` | `inherit` | `AVAILABLE` | Subagente somente leitura para exploração profunda da base de código, documentações locais e pesquisa web. |
| `browser` | `flash` | `AVAILABLE_WITH_RESTRICTIONS` | Subagente navegador para interação com páginas web, dashboards visuais e workflows cliente. |
| `image-generator` | `inherit` | `AVAILABLE` | Geração e manipulação de diagramas e artefatos de imagem baseados em prompts visuais. |
| `swarm` | Multi-Agent | `AVAILABLE` | Orquestração paralela de múltiplos agentes em quadro de mensagens compartilhado. |

---

## 3. Protocolo de Delegação e Hand-off

Toda delegação de subtarefa pelo Corp-Pipeline Master Orchestrator deve conter explicitamente:
1. **TASK**: Objetivo preciso e sem ambiguidades.
2. **CONTEXT**: Informações arquiteturais e decisões prévias relevantes.
3. **SCOPE**: Lista de arquivos que podem ou não ser modificados.
4. **INPUTS**: Contratos, dados ou referências de entrada.
5. **CONSTRAINTS**: Regras corporativas, restrições de imutabilidade e segurança.
6. **DELIVERABLES**: Saídas esperadas (código, testes, pareceres).
7. **VALIDATION**: Critérios de aceite e comandos de teste obrigatórios.
8. **REPORTING**: Sumário de evidências técnicas e riscos remanescentes.
