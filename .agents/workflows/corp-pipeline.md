---
name: corp-pipeline
description: Dispara a esteira corporativa de engenharia de software em 5 fases (Alinhamento, TDD, Implementação, Auditoria, Entrega/PR).
---

# Corporate 5-Phase Pipeline (`/corp-pipeline`)

Este workflow orquestra a esteira corporativa de engenharia de software com 2 checkpoints interativos (Gates), testes Shift-Left, auto-recuperação de até 3 tentativas e conformidade Git para Pull Requests.

---

## 🚀 Como Executar

Chame o comando passando o contexto da demanda corporativa ou ticket JIRA:

```bash
/corp-pipeline JIRA-123 Adicionar rota de autenticação segura com cookies HTTP-only
```

---

## 📋 Fluxo de Execução

### Passo 1: Alinhamento, Contratos & Escopo (Gate 1)
- O orquestrador analisa os requisitos, elabora as interfaces/DTOs e formula as premissas.
- **🔴 GATE 1**: O orquestrador apresenta a proposta de contratos e **pausa**, aguardando seu `proceed`.

### Passo 2: Shift-Left TDD
- Após sua aprovação, o detector de stack (`stack_detector.py`) identifica os comandos do projeto.
- O orquestrador escreve os testes unitários e de integração que validam os contratos da Fase 1.
- Executa a suíte e confirma o estado **RED (testes falhando como esperado)**.

### Passo 3: Implementação Cirúrgica
- Implementa apenas o código necessário para tornar os testes verdes.
- Em caso de falha, aciona auto-recuperação cirúrgica com teto de até 3 tentativas.

### Passo 4: Pre-Flight Gate & Auditoria
- Roda os linters, verificadores de tipo e scanners de segredos.
- Executa a suíte de regressão global do repositório.

### Passo 5: Entrega Corporativa (Gate 2)
- **🔴 GATE 2**: Apresenta o relatório final de validação e aguarda sua aprovação.
- Cria a branch convencional (`feat/<ticket>-<slug>`).
- Executa o commit semântico e gera o corpo do Pull Request estruturado no padrão Senior.
