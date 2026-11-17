---
name: plan-v2
description: Planejador corporativo avançado com análise de blast radius, grafo de execução DAG e sementes de TDD.
---

# Plan v2.0 (`/plan-v2`)

Gera um plano de implementação executivo corporativo antes de escrever qualquer código.

---

## 🚀 Como Executar

```bash
/plan-v2 <Descrição da Feature ou Arquivos a Alterar>
```

### Exemplo:
```bash
/plan-v2 Refatorar sistema de autenticação para suportar OAuth2 com refresh token em Redis
```

---

## 📋 Protocolo de Execução

1. **Cálculo de Blast Radius**: O orquestrador roda `plan_engine.py` para identificar todos os módulos que consom os arquivos alvo.
2. **Construção do DAG**: Cria a sequência topológica de tarefas com comando de validação e ação de rollback para cada item.
3. **Estratégia Zero-Downtime**: Formaliza o padrão Expand/Contract caso haja migrações de dados ou mudanças em APIs.
4. **Matriz TDD**: Extrai os contratos para a Fase 2 do `corp-pipeline` e aguarda o **Gate 1** de confirmação.
