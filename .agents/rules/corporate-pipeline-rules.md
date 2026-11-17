# Corporate Engineering Pipeline Rules (`corp-pipeline`)

This rule governs software engineering standards, quality gates, and git workflow for corporate and enterprise development.

---

## 1. Mandatory 5-Phase Development Lifecycle

Every engineering request (feature, bugfix, refactoring) MUST follow these 5 phases:

```text
[Demand/Ticket] 
      │
      ▼
1. Alinhamento, Contratos & Escopo ──► [🔴 Gate 1: Confirmação do Usuário]
      │
      ▼
2. Shift-Left TDD ───────────────────► [Testes Unitários RED (Devem Falhar)]
      │
      ▼
3. Implementação Cirúrgica ──────────► [Código Mínimo GREEN (Máx 3 auto-debugs)]
      │
      ▼
4. Pre-Flight Gate & Auditoria ──────► [Linter + Typecheck + Secret Scan + Testes]
      │
      ▼
5. Entrega Corporativa & Git ────────► [🔴 Gate 2: Validação] ──► [Feature Branch + PR]
```

---

## 2. Gate Specifications

### Gate 1 (Post-Scope & Pre-Implementation)
- **Trigger**: Conclusão da análise de requisitos, contratos de dados (DTOs) e ADR preliminar.
- **Action**: O orquestrador apresenta os contratos e PAUSA. É obrigatório aguardar a resposta explícita do usuário (`proceed` / `sim`).

### Gate 2 (Pre-Commit & Pre-PR)
- **Trigger**: Aprovação da auditoria local (Linter, Typecheck, Secret Scan e Testes 100% GREEN).
- **Action**: O orquestrador exibe o resumo executivo, diff de arquivos e proposta de branch. Aguarda validação antes do push final.

---

## 3. Git Governance & Branch Protection (Enterprise Zero-Main Rule)

1. **PROIBIDO commit ou push direto na `main` ou `master`**:
   - Viola políticas corporativas, branch protection e integridade de CI/CD.
2. **Nomenclatura Obrigatória de Branches**:
   - `feat/<ticket>-<slug>` (ex: `feat/AUTH-102-refresh-cookie`)
   - `fix/<ticket>-<slug>` (ex: `fix/CORE-304-null-pointer`)
   - `refactor/<ticket>-<slug>` (ex: `refactor/API-501-clean-routes`)
3. **Commits Semânticos**:
   - Padrão Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).
4. **Pull Request Corporativo**:
   - Todo PR deve conter as 6 seções mandatórias do template `.agents/skills/corp-pipeline/templates/pr_template.md`.

---

## 4. Test-Driven Development (Shift-Left) & Contained Debugging
1. **Red Before Green**: Nenhum código de produção deve ser escrito antes de haver um teste automatizado validando a falha (RED).
2. **Auto-Debug Cap**: Em caso de falha de teste na Fase 3, o orquestrador está limitado a **3 tentativas cirúrgicas**. Se não resolver, deve parar e expor o log ao engenheiro.
