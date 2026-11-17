---
name: orchestrator-v2
description: Meta-orquestrador inteligente com cálculo dinâmico de afinidade, cadeias em estágios e circuit breakers de quota.
---

# Master Orchestrator v2.0 (`/orchestrator-v2`)

Acione o meta-orquestrador autônomo para analisar, compor e coordenar a execução multi-agente de qualquer tarefa de engenharia.

---

## 🚀 Como Executar

```bash
/orchestrator-v2 <Demanda, Funcionalidade ou Ticket>
```

### Exemplo:
```bash
/orchestrator-v2 Implementar nova esteira de renderização com Webhooks e fallbacks assíncronos
```

---

## 📋 Protocolo de Execução

1. **Cálculo de Afinidade**: Avalia o catálogo de skills e subagentes disponíveis.
2. **Encadeamento em Estágios**: Monta a cadeia `grill-v2` $\rightarrow$ `plan-v2` $\rightarrow$ `corp-pipeline`.
3. **Supervisão de DoD**: Assegura que nenhum código chegue ao usuário sem testes 100% verdes, linter limpo e branch de feature protegida.
