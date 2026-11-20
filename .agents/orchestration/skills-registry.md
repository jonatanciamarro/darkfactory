# Registro de Skills do Ecossistema (`skills-registry.md`)

> **Catálogo de Conhecimento e Procedimentos Reutilizáveis**  
> *Mapeamento de skills essenciais para operação diária e catálogo de 318+ skills da biblioteca sob demanda.*

---

## 1. Skills de Operação Diária (DAILY Core Skills)

Estas skills foram selecionadas e perfiladas especificamente para o ecossistema `corporate-engineer`. São ativadas prioritariamente pelo orquestrador:

| Skill | Status | Finalidade Operacional | Gatilho / Invocação | Localização |
|---|---|---|---|---|
| `corp-pipeline` | `AVAILABLE` | Pipeline corporativo em 5 fases com Gate 1 (Escopo/ADR), TDD, Auto-debug, Pre-Flight e Gate 2 (PR). | `/corp-pipeline` | [.agents/skills/corp-pipeline](file:///e:/projcts/corporate%20engineer/.agents/skills/corp-pipeline/SKILL.md) |
| `grill-me_v2` | `AVAILABLE` | Entrevista investigativa e hierárquica para descoberta de requisitos e geração formal de ADRs. | `/grill-me_v2` | [.agents/skills/grill-me_v2](file:///e:/projcts/corporate%20engineer/.agents/skills/grill-me_v2/SKILL.md) |
| `plan_v2` | `AVAILABLE` | Planejamento técnico corporativo com Matriz de Trade-offs, STRIDE e contratos DTO tipados. | `/plan_v2` | [.agents/skills/plan_v2](file:///e:/projcts/corporate%20engineer/.agents/skills/plan_v2/SKILL.md) |
| `python-patterns` | `AVAILABLE` | Padrões idiomáticos de Python 3.10/3.11, tipagem rigorosa, PEP 8 e arquitetura limpa. | Contexto Python | [.agents/skills/python-patterns](file:///e:/projcts/corporate%20engineer/.agents/skills/python-patterns/SKILL.md) |
| `python-testing` | `AVAILABLE` | Estratégias de teste com Pytest, fixtures, mocks, parametrização e cobertura. | Contexto de Testes | [.agents/skills/python-testing](file:///e:/projcts/corporate%20engineer/.agents/skills/python-testing/SKILL.md) |
| `tdd-workflow` | `AVAILABLE` | Metodologia rigorosa Test-Driven Development (Red-Green-Refactor) com 80%+ cobertura. | `/tdd` | [.agents/skills/tdd-workflow](file:///e:/projcts/corporate%20engineer/.agents/skills/tdd-workflow/SKILL.md) |
| `security-review` | `AVAILABLE` | Checklist corporativo de segurança: segredos, sanitização, autenticação e autorização. | `/security-scan` | [.agents/skills/security-review](file:///e:/projcts/corporate%20engineer/.agents/skills/security-review/SKILL.md) |
| `api-design` | `AVAILABLE` | Padrões de design de APIs RESTful, contratos DTO e tratamento padronizado de erros. | Design de Interfaces | [.agents/skills/api-design](file:///e:/projcts/corporate%20engineer/.agents/skills/api-design/SKILL.md) |
| `mcp-server-patterns` | `AVAILABLE` | Padrões para clientes e servidores MCP: stdio, SSE, schemas de ferramentas e validação. | Módulo MCP | [.agents/skills/mcp-server-patterns](file:///e:/projcts/corporate%20engineer/.agents/skills/mcp-server-patterns/SKILL.md) |
| `agentic-engineering` | `AVAILABLE` | Engenharia orientada a agentes com decomposição de tarefas e execução orientada a evals. | Orquestração | [.agents/skills/agentic-engineering](file:///e:/projcts/corporate%20engineer/.agents/skills/agentic-engineering/SKILL.md) |
| `conventional-commit-review`| `AVAILABLE` | Auditoria de diffs para redação de commits semânticos no padrão Conventional Commits. | Pré-commit | [.agents/skills/conventional-commit-review](file:///e:/projcts/corporate%20engineer/.agents/skills/conventional-commit-review/SKILL.md) |
| `verification-loop` | `AVAILABLE` | Ciclo contínuo de verificação pós-implementação com checagem estática e dinâmica. | Pós-implementação | [.agents/skills/verification-loop](file:///e:/projcts/corporate%20engineer/.agents/skills/verification-loop/SKILL.md) |
| `agent-sort` | `AVAILABLE` | Auditoria e perfilamento de repositório para distribuição de skills DAILY vs LIBRARY. | `/agent-sort` | [.agents/skills/agent-sort](file:///e:/projcts/corporate%20engineer/.agents/skills/agent-sort/SKILL.md) |

---

## 2. Catálogo de Skills da Biblioteca Sob Demanda (LIBRARY)

O repositório possui **318 skills adicionais** instaladas em `.agents/skills/`, gerenciadas pelo Antigravity via **progressive disclosure** (apenas nomes e descrições são visíveis inicialmente; o conteúdo completo de `SKILL.md` é carregado apenas quando a skill é ativada).

### Principais Domínios da Biblioteca:
1. **Engenharia de Backend & APIs**:
   - `fastapi-patterns`, `django-patterns`, `django-celery`, `django-tdd`, `nestjs-patterns`, `springboot-patterns`, `springboot-tdd`, `golang-patterns`, `golang-testing`, `rust-patterns`, `rust-testing`, `dotnet-patterns`.
2. **Dados, Persistência & Bancos**:
   - `postgres-patterns`, `mysql-patterns`, `redis-patterns`, `clickhouse-io`, `jpa-patterns`, `kotlin-exposed-patterns`, `database-migrations`.
3. **Qualidade, Testes & E2E**:
   - `e2e-testing`, `react-testing`, `csharp-testing`, `cpp-testing`, `godot-testing`, `windows-desktop-e2e`.
4. **Segurança & Conformidade**:
   - `security-bounty-hunter`, `hipaa-compliance`, `django-security`, `laravel-security`, `defi-amm-security`, `prediction-market-risk-review`.
5. **Automação, Multi-Agente & LLM Ops**:
   - `continuous-agent-loop`, `autonomous-loops`, `devfleet`, `dmux-workflows`, `cost-aware-llm-pipeline`, `cost-tracking`, `eval-harness`, `gan-style-harness`.
6. **Infraestrutura, Redes & DevOps**:
   - `deployment-patterns`, `kubernetes-patterns`, `docker-patterns`, `terraform-patterns`, `canary-watch`, `cisco-ios-patterns`, `netmiko-ssh-automation`, `network-bgp-diagnostics`.

---

## 3. Diretriz de Progressive Disclosure

O Corp-Pipeline Orchestrator consulta o catálogo de skills conforme o domínio da tarefa, garantindo economia de tokens de contexto e precisão técnica cirúrgica.
