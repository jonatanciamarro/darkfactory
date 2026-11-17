---
name: grill-v2
description: Interrogatório socrático pró-ativo de nível Staff Engineer com grounding preditivo, análise dos 4 quadrantes e geração de ADR executável.
---

# Grill-Me v2.0 (`/grill-v2`)

Acione o interrogatório socrático pró-ativo para alinhar arquitetura, desarmar edge cases e formalizar contratos antes de qualquer código.

---

## 🚀 Como Executar

```bash
/grill-v2 <Contexto da Feature ou Arquitetura a Desafiar>
```

### Exemplo:
```bash
/grill-v2 Implementar sistema de cache distribuído em Redis com invalidação orientada a eventos
```

---

## 📋 Protocolo de Execução

1. **Varredura Preditiva**: O orquestrador roda `grill_analyzer.py` e inspeciona o repositório sem fazer perguntas óbvias.
2. **O Quadrante Socrático**: Formula perguntas com recomendações opinativas claras cobrindo Contratos, Modos de Falha, Segurança e Pragmatismo.
3. **Consolidação de Decisões**: Ao finalizar, gera automaticamente o ADR da arquitetura e as sementes de TDD prontas para a Fase 2 do `corp-pipeline`.
