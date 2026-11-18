# DarkFactory — Autonomous Meta-Orchestrator Protocol (Orquestrador Mestre Corporativo)

@[Contexto do Projeto](PROJECT_CONTEXT.md)

> **DIRETIVA MANDATÓRIA PERMANENTE**: O assistente opera sob o **CORPORATE 5-PHASE PIPELINE (`corp-pipeline`)** como padrão canônico para qualquer solicitação, nova feature, correção de bug ou refatoração. A esteira garante alinhamento de escopo (Gate 1), Shift-Left TDD (testes RED antes do código), implementação cirúrgica (GREEN, máx 3 tentativas), auditoria local pré-flight e entrega corporativa rastreável (Gate 2, feature branch, nunca direto na `main`).

---

## 🧭 O Ciclo Corporativo de 5 Fases (Padrão Mandatório)

### Fase 1: Alinhamento, Contratos & Escopo (🔴 Gate 1 de Confirmação)
1. **Análise de Requisitos**: Receba a demanda ou ticket JIRA/Linear e mapeie regras de negócio e edge cases.
2. **Definição de Contratos & DTOs**: Especifique os tipos de dados, schemas de validação (Pydantic, interfaces) e um breve ADR (Architecture Decision Record) justificando as decisões técnicas.
3. **Gate 1 Humano**: Apresente a proposta de contratos e **PARE** para obter a confirmação explícita (`proceed` / `sim`) do usuário antes de criar ou modificar qualquer código de produção.

### Fase 2: Shift-Left TDD (Contratos em Código)
1. **Detecção de Stack**: Execute `python .agents/skills/corp-pipeline/scripts/stack_detector.py` para identificar comandos de teste e lint da stack ativa.
2. **Criação de Testes Automatizados**: Escreva os testes unitários e de integração baseados estritamente nos contratos da Fase 1.
3. **Certificação RED**: Execute a suíte e garanta que os testes **falham estritamente pelo motivo esperado** antes de qualquer implementação.

### Fase 3: Implementação Cirúrgica & Auto-Recuperação
1. **Implementação Mínima**: Escreva apenas o código de produção necessário para fazer a suíte passar (GREEN).
2. **Auto-Recuperação Cirúrgica (Teto: 3 Tentativas)**: Se testes falharem, diagnostique o traceback isolado e aplique ajustes pontuais (lógica -> tipagem -> contrato). Se a falha persistir após 3 tentativas, interrompa, exiba o diagnóstico e solicite direcionamento.

### Fase 4: Pre-Flight Gate & Auditoria Local
Antes de prosseguir para entrega, execute e aprove todos os 4 pilares:
1. **Linter & Compilação**: Zero warnings ou erros de sintaxe (`py_compile`, `ruff`, `eslint`).
2. **Tipagem Estrita**: Verificação de tipos (`mypy`, `tsc`).
3. **Secret Scan**: Varredura regex assegurando zero credenciais, tokens de API ou senhas expostas.
4. **Regressão Global**: Suíte completa de testes do repositório 100% verde.

### Fase 5: Entrega Corporativa & Governança Git (🔴 Gate 2 de Confirmação)
1. **Gate 2 Humano**: Apresente o resumo das alterações, diff e evidências da auditoria para validação final.
2. **Governança de Branches (Zero Push na Main)**:
   - **É TERMINANTEMENTE PROIBIDO realizar commits ou push direto na `main` ou `master`**.
   - Crie obrigatoriamente uma branch convencional: `git checkout -b feat/<ticket>-<slug>` ou `fix/<ticket>-<slug>`.
3. **Commits Semânticos**: Commits atômicos no padrão Conventional Commits (`feat:`, `fix:`, `refactor:`).
4. **Push Remoto & Pull Request**: Sincronize a feature branch com a origin (`git push -u origin <branch>`) e gere a descrição completa do Pull Request via template corporativo (`.github/PULL_REQUEST_CORP_PIPELINE.md`).

---

## 🎭 Matriz de Roteamento Especializado DarkFactory

| Tipo de Demanda | Subagente Recomendado | Skill / Regra a Consultar | Ferramentas Críticas |
| :--- | :--- | :--- | :--- |
| **Nova Feature, Bugfix & Engenharia Corporativa** | `tdd-guide` / `architect` | `corp-pipeline`, `tdd-workflow` | `run_command`, `write_file`, `edit_file` |
| **Showrunner, Roteiro & Storyboard Não-Linear** | `nolan-director` | `darkfactory-nolan`, `nolan-dark-history-director` | `read_file`, `write_file` |
| **Pesquisa Histórica & Verificação de Fontes** | `architect` | `api-design`, `verification-loop` | `run_command`, `read_file` |
| **Engenharia Vocal & Mixagem Acústica (-14 LUFS)** | `python-reviewer` | `python-patterns`, `darkfactory-review` | `run_command`, `edit_file` |
| **Fábrica de Vídeo T2V (RunningHub / MiniMax / Wan)** | `e2e-runner` | `darkfactory-pipeline`, `error-handling` | `run_command`, `edit_file` |
| **Cinema Dashboard Web SPA (:8502)** | `architect` | `darkfactory-deploy`, `api-design` | `run_command`, `edit_file` |
| **Qualidade & Testes Automatizados (Pytest)** | `tdd-guide` | `python-testing`, `tdd-workflow` | `run_command` |
| **Segurança & Credenciais (.env)** | `security-reviewer` | `verification-loop` | `read_file` |
| **Orquestração Autônoma & Despacho Multivetorial** | `architect` / `planner` | `orchestrator-v2`, `corp-pipeline` | `run_command`, `write_file` |
| **Frescor Arquitetural & Eliminação de Código Obsoleto** | `codebase-freshness-sentinel` | `codebase-freshness-sentinel`, `verification-loop` | `run_command`, `read_file`, `edit_file` |

---

### Transparência Operacional
Ao executar ações no projeto, identifique brevemente a rota corporativa:
`🎯 Orquestrador: [Skill: <nome> | Agente: <nome> | Ferramenta: <nome>]`
