# Backlog Contínuo de Melhorias — DarkFactory (`improvement-backlog.md`)

> **Repositório Persistente de Oportunidades de Evolução do DarkFactory**  
> *Governança estrita: Descoberta → Recomendação via `[CORP-PIPELINE / IMPROVEMENT DETECTED]` → Salvamento com Aprovação do Usuário → Implementação.*

---

## 1. Protocolo de Governança do Backlog

Este catálogo preserva ideias e melhorias identificadas pelo **Corp-Pipeline Master Orchestrator** para o projeto **DarkFactory**, garantindo que nenhuma oportunidade valiosa de otimização da esteira cinematográfica seja perdida ou implementada sem aprovação prévia.

### Estados do Ciclo de Vida:
- `PROPOSED`: Descoberta inicial pela inteligência do orquestrador; aguardando apreciação do usuário.
- `SAVED_NOT_APPROVED`: Usuário aprovou o salvamento para backlog, mas ainda não autorizou a implementação.
- `APPROVED`: Usuário autorizou formalmente o início do desenvolvimento.
- `IN_PROGRESS`: Em desenvolvimento ativo seguindo o Corp-Pipeline (Fase 1 a 5).
- `IMPLEMENTED`: Código implementado e pre-flight aprovado com testes verdes.
- `VERIFIED`: Validado formalmente em produção ou mergeado no branch principal.
- `REJECTED`: Analisado e descartado com justificativa documentada.
- `DEFERRED`: Postergado para milestones futuras.
- `SUPERSEDED`: Substituído por uma proposta ou arquitetura mais moderna.

---

## 2. Tabela de Registro Geral de Melhorias

| ID | Título da Melhoria | Categoria | Complexidade | Status Atual | Data de Descoberta |
|---|---|---|---|---|---|
| `IMP-0001` | Contratos Fortemente Tipados Pydantic v2 nos Retornos de `ai_engine_suite.py` | `QUALITY` | Média (M) | `PROPOSED` | `2026-11-20` |
| `IMP-0002` | Redução da Complexidade Ciclomática e Modularização de `StoryValidator` | `ARCHITECTURE` | Média (M) | `PROPOSED` | `2026-11-20` |
| `IMP-0003` | Integração do DAG Orchestrator com Checkpoints de Recuperação no `run_pilot_pipeline.py` | `RELIABILITY` | Média (M) | `PROPOSED` | `2026-11-20` |

---

## 3. Especificação Detalhada das Propostas

### 🔹 IMP-0001: Contratos Fortemente Tipados Pydantic v2 nos Retornos de `ai_engine_suite.py`
- **Categoria**: `QUALITY` | `GOVERNANCE`
- **Status**: `PROPOSED`
- **Observação**: A auditoria EDD (`corporate-engineer eval`) detectou múltiplos retornos de dicionários soltos (`dict`) em funções centrais como `check_engine_auth_status` e `test_flow_video`.
- **Solução Proposta**: Criar modelos DTO imutáveis Pydantic v2 para padronizar os contratos entre os motores de vídeo e o dashboard.
- **Benefícios**: Eliminação de `KeyError`, validação em tempo de compilação/teste e tipagem estrita no Mypy.
