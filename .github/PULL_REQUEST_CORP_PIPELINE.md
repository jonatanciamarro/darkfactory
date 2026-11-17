# feat(pipeline): implement 5-phase corporate engineering pipeline with shift-left tdd

> **Ticket/Issue**: `CORP-101`  
> **Type**: Feature / Architecture & Governance Delivery  
> **Target Branch**: `main`  
> **Source Branch**: `feat/CORP-101-enterprise-pipeline`

---

## 1. Business Context & Problem Statement
Para suportar o trabalho em ambientes corporativos com requisitos estritos de conformidade, segurança de dados, branch protection e revisão por pares, este PR introduz uma esteira determinística de 5 fases (`corp-pipeline`) no ecossistema Antigravity.

Elimina o antipadrão de commits diretos na `main`, previne a queima excessiva de tokens de IA através de limites cirúrgicos de auto-recuperação e ancora o desenvolvimento no paradigma **Shift-Left TDD**.

---

## 2. Technical Decisions & Trade-offs
1. **Human-in-the-Loop em 2 Gates Críticos**:
   - Gate 1: Aprovação de escopo, contratos (DTOs) e ADRs antes de qualquer linha de código.
   - Gate 2: Aprovação da auditoria de segurança e diff antes de push ou abertura de PR.
2. **Shift-Left TDD com Certificação RED**:
   - Criação mandatória de testes automatizados que falham antes do código de produção.
3. **Detecção Multi-Stack e Polyglot**:
   - `stack_detector.py` identifica Python (Pytest/Ruff/Mypy), Node.js (Vitest/Jest/ESLint/TSC) e Go, com suporte a overrides via `.corp-pipeline.json`.
4. **Auto-Recuperação Cirúrgica Limitada**:
   - Teto rígido de até 3 tentativas baseado em tracebacks isolados, evitando loops infinitos e context rot.
5. **Governança de Branches**:
   - Rejeição determinística de branches desprotegidas (`main`, `master`, `develop`) para push direto, padronizando convenções `feat/<ticket>-<slug>`.

---

## 3. How to Test & Verification Commands

Para reproduzir os testes da esteira localmente:
```bash
# 1. Executar os 9 testes de contrato da esteira corporativa
.\venv\Scripts\python.exe -m pytest -v tests/test_corp_pipeline.py

# 2. Executar o smoke test de detecção de stack e políticas Git
.\venv\Scripts\python.exe .agents/skills/corp-pipeline/scripts/stack_detector.py

# 3. Executar a suíte de regressão global do repositório
.\venv\Scripts\python.exe -m pytest -q
```

---

## 4. Rollback & Disaster Recovery Plan
Esta funcionalidade é puramente aditiva e modular:
- Caso necessário reverter, basta realizar o revert deste merge commit:
  ```bash
  git revert <MERGE_COMMIT_HASH> -m 1
  ```
- Nenhuma alteração destrutiva ou bloqueante foi introduzida no core do DarkFactory.

---

## 5. Security & Compliance Checklist
- [x] **Zero Hardcoded Secrets**: Varredura regex contra tokens (`ghp_*`, `sk-*`, `AIza*`) e chaves privadas executada com sucesso (0 findings).
- [x] **Branch Protection Compliance**: Código commitado em feature branch `feat/CORP-101-enterprise-pipeline` e nunca direto na `main`.
- [x] **Strict Type Safety & Compilation**: Validado via `py_compile` e análise de AST com 0 warnings.
- [x] **Full Regression Integrity**: Suíte global com 339+ testes passando 100%.

---

## 6. Reviewer Checklist & Verification Evidence
- [x] `.agents/skills/corp-pipeline/SKILL.md`: Documentação executável e prompt da skill.
- [x] `.agents/workflows/corp-pipeline.md`: Slash command `/corp-pipeline` registrado.
- [x] `.agents/skills/corp-pipeline/scripts/stack_detector.py`: Detector e validadores testados.
- [x] `tests/test_corp_pipeline.py`: 9 cenários unitários cobrindo todos os contratos.
