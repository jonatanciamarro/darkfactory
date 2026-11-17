# {{TITLE}}

> **Ticket/JIRA**: `{{TICKET_ID}}`  
> **Author**: `{{AUTHOR}}`  
> **Pipeline**: Corporate 5-Phase Pipeline (`/corp-pipeline`)

---

## 1. Business Context & Problem Statement
<!-- Descreva o objetivo de negócio e o problema que este PR soluciona -->
{{CONTEXT}}

---

## 2. Technical Decisions & Trade-offs
<!-- Justifique a arquitetura escolhida, decisões tomadas no /grill-me e alternativas descartadas -->
{{DECISIONS}}

---

## 3. How to Test & Verification Commands
<!-- Comandos exatos para os revisores reproduzirem os testes localmente ou em CI -->
```bash
{{TEST_COMMANDS}}
```

---

## 4. Rollback & Disaster Recovery Plan
<!-- Como reverter esta alteração com segurança caso ocorra incidente em produção -->
{{ROLLBACK_PLAN}}

---

## 5. Security & Compliance Checklist
- [x] **Zero Hardcoded Secrets**: Nenhuma chave de API, senha ou credencial sensível no código.
- [x] **Type Safety**: Tipagem estrita validada (sem warnings ou type-ignores injustificados).
- [x] **Branch Protection Compliance**: Desenvolvido em branch de feature derivada de base atualizada.
- [x] **Test Coverage**: Testes unitários e de integração cobrindo os cenários principais e edge cases.

---

## 6. Reviewer Checklist & Verification Evidence
<!-- Evidências de execução, logs de testes verdes e notas para o time -->
{{EVIDENCE}}
