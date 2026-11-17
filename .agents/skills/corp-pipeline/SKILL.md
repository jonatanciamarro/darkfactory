---
name: corp-pipeline
description: Corporate 5-Phase Engineering Pipeline for enterprise environments. Enforces Scope Alignment, Shift-Left TDD, Surgical Implementation with 3-trial auto-debug, Pre-Flight Quality Gates, and Compliant Git Branching/PR generation.
---

# Corporate 5-Phase Engineering Pipeline (`corp-pipeline`)

This skill automates and governs the software delivery lifecycle for corporate and enterprise environments, ensuring strict quality standards, branch protection, Shift-Left TDD, and team-friendly Pull Requests.

---

## 🎯 When to Activate
- Automatically activated via the `/corp-pipeline` slash command.
- Activated whenever implementing enterprise features, bug fixes, or refactoring subject to corporate compliance, branch protection, or team code review.

---

## 🧭 The 5 Deterministic Phases

```text
[Input: Ticket/Demand]
       │
       ▼
[FASE 1: Alinhamento, Contratos & Escopo] ──► 🔴 GATE 1: Aprovação Humana
       │
       ▼ (Aprovado)
[FASE 2: Shift-Left TDD] ──────────────────► Testes falhando (RED)
       │
       ▼
[FASE 3: Implementação Cirúrgica] ─────────► Testes passando (GREEN) (Máx 3 retentativas)
       │
       ▼
[FASE 4: Pre-Flight Gate & Auditoria] ─────► Linter + Typecheck + Secret Scan
       │
       ▼
[FASE 5: Entrega Corporativa] ─────────────► 🔴 GATE 2: Aprovação Final ──► Branch & PR
```

---

### Fase 1: Alinhamento, Contratos & Escopo (Gate 1)
1. **Entrada do Usuário**: Ticket JIRA/Linear ou descrição da demanda.
2. **Definição de Contratos**:
   - DTOs, schemas de validação e interfaces de dados (Pydantic, TypeScript interfaces, Go structs).
   - Mapeamento de edge cases, status de erro e respostas esperadas.
   - Breve ADR (Architecture Decision Record) justificando as escolhas.
3. **🔴 GATE 1 (Confirmação Obrigatória)**:
   - Apresente os contratos e premissas ao usuário.
   - **PARE e aguarde** a confirmação explícita (`proceed` / `sim`) antes de escrever qualquer código.

---

### Fase 2: Shift-Left TDD (Contratos em Código)
1. **Detecção de Stack**:
   - Execute o detector automatizado:
     ```powershell
     python .agents/skills/corp-pipeline/scripts/stack_detector.py
     ```
   - Obtém `test_cmd`, `lint_cmd`, e `typecheck_cmd`.
2. **Escrever Testes Automatizados**:
   - Crie testes unitários e de integração baseados estritamente nos contratos da Fase 1.
3. **Certificação RED**:
   - Execute o comando de teste.
   - **Assegure que os testes falham** pelo motivo esperado antes de prosseguir.

---

### Fase 3: Implementação Cirúrgica & Auto-recuperação
1. **Implementação Mínima**:
   - Escreva apenas o código de produção necessário para satisfazer os testes da Fase 2.
2. **Execução de Testes (GREEN)**:
   - Execute o `test_cmd`.
3. **Auto-recuperação Cirúrgica (Teto: 3 tentativas)**:
   - Se o teste falhar, analise o traceback isolado e aplique correções cirúrgicas.
   - Tentativa 1: Correção de lógica interna.
   - Tentativa 2: Ajuste de tipagem ou contrato de mock.
   - Tentativa 3: Ajuste fino final.
   - *Se persistir após a 3ª tentativa*: Interrompa, exiba o diagnóstico exato e solicite orientação do usuário.

---

### Fase 4: Pre-Flight Gate & Auditoria Local
Execute a suíte de conformidade corporativa:
1. **Linter**: Execute o `lint_cmd` (ex: `ruff check .` ou `eslint`).
2. **Typecheck**: Execute o `typecheck_cmd` (ex: `mypy .` ou `tsc --noEmit`).
3. **Secret Scan**: Verifique se nenhum arquivo rastreado contém tokens, credenciais ou segredos expostos.
4. **Regressão Global**: Execute a suíte completa de testes do projeto para garantir zero regressões.

---

### Fase 5: Entrega Corporativa (Gate 2)
1. **🔴 GATE 2 (Confirmação Final)**:
   - Apresente o diff resumido, status dos testes e proposta de mensagem de commit.
   - Aguarde o `proceed` do usuário.
2. **Branching & Git Governance**:
   - Verifique a branch atual: **NUNCA realize push ou commits diretos na `main` ou `master`**.
   - Crie branch de feature:
     ```bash
     git checkout -b feat/<TICKET_ID>-<slug>
     ```
3. **Commits Semânticos**:
   - Realize commits atômicos no padrão Conventional Commits (`feat:`, `fix:`, `refactor:`).
4. **Geração de Pull Request**:
   - Gere o resumo do PR preenchido com o template em `.agents/skills/corp-pipeline/templates/pr_template.md`.
   - Se o `gh` CLI estiver disponível, dispare `gh pr create`. Caso contrário, forneça o markdown completo pronto para abertura na interface web corporativa.
