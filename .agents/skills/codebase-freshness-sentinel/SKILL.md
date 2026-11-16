---
name: codebase-freshness-sentinel
description: >-
  Audits DarkFactory architecture to ensure the Zero-Zombie rule: no newly developed
  engines in src/video/ or src/factory/ are disconnected from the main pipeline (run_pilot_pipeline.py),
  mandates immediate Facade delegation, purges obsolete duplicate code, and prevents code rot.
---

# DarkFactory Codebase Freshness & Architecture Sentinel (`/freshness`)

Esta skill fornece o protocolo operacional e ferramentas de auditoria contínua para garantir que **100% do código avançado desenvolvido no ecossistema DarkFactory esteja efetivamente em uso na esteira de produção**, eliminando de forma agressiva códigos zumbis, módulos duplicados ou dependências de rotinas antigas.

---

## 🧭 Quando Usar Esta Skill
- Imediatamente após implementar ou refatorar qualquer motor em `src/video/`, `src/factory/` ou `src/`.
- Antes de submeter código ou aprovar planos de arquitetura.
- Sempre que houver suspeita de que uma rotina antiga ainda está sendo invocada em vez da versão moderna.
- Durante revisões de código preventivas contra proliferação de código morto.

---

## 🔬 Checklist de Auditoria Arquitetural

### 1. Auditoria de Facade & Delegação
Toda rotina na raiz de `src/*.py` deve atuar exclusivamente como **Facade** apontando para os motores canônicos:

| Script de Entrada | Motor Canônico Obrigatório | Localização |
|---|---|---|
| `src/audio_mixer_master.py` | `DarkFactoryAudioEngine` | `src/video/audio_engine.py` |
| `src/generate_pilot_audio.py` | `MasterVoiceRouter` | `src/video/voice_router.py` |
| `src/research_engine.py` | `PublicDomainResearchEngine` | `src/video/public_domain_research.py` |
| `src/shorts_generator.py` | `ShortsRepurposerEngine` | `src/video/shorts_repurposer.py` |
| `src/generate_motion_assets.py` | `MapAnimator`, `HyperFramesMotionEngine`, `SeedVR25Upscaler` | `src/video/`, `src/factory/` |
| `src/render_pilot_video.py` | `CinematicColorGrader`, `VoiceAligner`, `UniversalTimelineExporter` | `src/video/` |

### 2. Auditoria da Esteira Principal (`run_pilot_pipeline.py`)
A esteira de ponta a ponta (`--step all` ou `--phase all`) deve orquestrar sequencialmente as 12 etapas canônicas:
1. `auth_gate.py`
2. `nolan_director.py`
3. `research_engine.py`
4. `google_flow_bot.py`
5. `generate_pilot_audio.py`
6. `cosyvoice_master.py`
7. `audio_mixer_master.py`
8. `generate_motion_assets.py` (Step 6.5)
9. `render_pilot_video.py`
10. `shorts_generator.py`
11. `youtube_compliance_qc.py`
12. `youtube_algorithm_booster.py`

### 3. Eliminação Imediata de Código Obsoleto
Se um novo motor substituir um arquivo antigo:
1. Valide a integração rodando os testes unitários (`pytest tests/test_<modulo>.py`).
2. Se o script antigo não tiver consumidores ativos, execute `git rm <script_antigo>.py`.
3. Não deixe scripts legados "por precaução". O histórico do Git preserva versões passadas.

---

## ⚡ Comandos de Validação Rápida

```powershell
# 1. Executar auditoria de frescor arquitetural e código órfão
.\venv\Scripts\python.exe scripts/audit_codebase_freshness.py

# 2. Testar dry-run da esteira completa ponta a ponta
.\venv\Scripts\python.exe run_pilot_pipeline.py --step all --dry-run

# 3. Validar integridade da suíte de testes (311+ testes)
.\venv\Scripts\python.exe -m pytest -q
```
