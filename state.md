# DarkFactory Pipeline State

> Sincronizado em **2026-11-16** com **Episódio Completo Renderizado de Ponta a Ponta** (40 Cenas / 834.77s / 13.91 Minutos), conformidade EBU R128 (-14 LUFS / -1.0 dBTP), **Orquestração Visual Quádrupla Concluída (Vídeos IA + Fotos 4K SeedVR + Motion Step 6.5 + Texto Kinetic)**, **3 Shorts Funnel 9:16 Produzidos**, **Pacote Completo de Distribuição Algorítmica em 7 Idiomas**, **Auditoria Green Dollar 100/100 Aprovada com Kit de Disputa Content ID** e **308 Testes Automatizados 100% Verificados**.

## 🔌 Status do Ecossistema & Escopo Ativo
- **6 Padrões Canônicos de Produção (Golden Standards)**:
  1. *Pré-Autenticação Obrigatória*: Google Flow, RunningHub e Flow Music autenticados antes de qualquer disparo.
  2. *Dual-Shot Visual*: Google Flow (Veo 3.1 Shot B Macro + Omni Flash Shot A Drama) com Fallback RunningHub MiniMax H3.
  3. *Narração Cinematográfica*: CosyVoice 3 (Conta 4) com Narrator Consistency Lock e Fallback Kokoro-82M.
  4. *Trilha Sonora Autoral*: Flow Music (Lyria & Zimmer OST) com Fallback RunningHub MiniMax Music 3 calibrado a -14 LUFS.
  5. *Sound Design & Foley*: Biblioteca Curada CC0 Gratuita com posicionamento automático por timestamps das cenas.
  6. *GPU Economy RunningHub*: Cancelamento instantâneo atômico de todo workflow pós-download para economizar 100% de tempo de GPU ocioso.
- **Showrunner Cinematográfico**: Christopher Nolan (`nolan-director.md`, `src/nolan_multi_act.py` e skill `nolan-dark-history-director`).
- **Hard Gate dos 27 Livros Canônicos (`src/video/story_validator.py`)**:
  - Auditoria executável integrada diretamente ao `nolan_director.py` e `run_pilot_pipeline.py`.
  - Verificação rigorosa: Regra dos Seis & Eye-Trace (Walter Murch), Retenção dos 60s & Zero Dead Air (MrBeast), Curiosity Gaps & Conflito Interno (Lisa Cron), STEPPS Viral (Jonah Berger), Hook Point de 3 Segundos (Brendan Kane) e Binge Bridge (Derral Eves / Alex Hormozi).
  - Score auditado: **88.0/100 (Grade: A, Pronto para Produção: SIM)**.
- **Automação Inteligente de Foley & SFX (`src/video/foley_library.py` & `src/audio_mixer_master.py`)**:
  - Posicionamento automático por timestamps das cenas e eventos visuais do roteiro:
    - `whoosh_subtle` (-18 dB) no corte exato de cada cena.
    - `stamp_slam` (-7 dB) em `t = start + 1.2s` sincronizado ao carimbo de dossiê confidencial.
    - `teletype_burst` (-12 dB) e `radar_ping` (-9 dB) em overlays táticos e mapas.
    - `sub_riser` (-11 dB) em quedas dramáticas e silêncios `(pausa: 2s)`.
    - Panning estéreo sutil (-0.15 a +0.15) e mixagem em 48kHz / -14 LUFS sem conflito espectral com a voz.
- **Pre-Flight Authentication Gate (`src/auth_gate.py`)**:
  - Verificação prévia obrigatória antes de gerar qualquer asset.
  - Sessão persistente via cookies/storage state para **Google Flow** (`flow.google.com`), **RunningHub** (`runninghub.ai`, **Conta 1 Unificada**) e **Flow Music** (`flowmusic.app`).
- **Estrutura Master do Documentário**: 5 Atos completos (8 cenas por ato = 40 cenas cinematográficas contínuas, totalizando **834.77 segundos / 13.91 minutos**).
- **Master Final Concluído (`data/output/the_1983_soviet_glitch_final_1080p.mp4`)**:
  - Resolução: 1080p Full HD com letterbox 2.39:1 Anamorphic Cinema Scope.
  - Gradação de cor: CinematicColorGrader perfil `kodak_2383` (Cold War Bleach-Bypass 3D LUT + granulação analógica 35mm).
  - Áudio: Mix 4-stems masterizado a -14 LUFS com sidechain dynamic ducking (-16 dB).
  - Legendas: Burn-in calibrado na margem inferior preta para legibilidade teatral.
- **Funnel de Retenção Mobile (3 YouTube Shorts 9:16)**:
  - `the_1983_soviet_glitch_final_1080p_short_01_hook.mp4` (50s, gancho da sirene em Serpukhov-15).
  - `the_1983_soviet_glitch_final_1080p_short_02_radar.mp4` (50s, telemetria dos 5 mísseis balísticos).
  - `the_1983_soviet_glitch_final_1080p_short_03_dilemma.mp4` (50s, a contagem regressiva de 20 minutos).
  - Composição: Fundo com desfoque cinematográfico 1080x1920 + centro nítido + legendas amarelas/brancas de alta visibilidade + botão de 'Related Video' direcionando ao documentário longo.
- **Pacote Completo de Distribuição Algorítmica (`the_1983_soviet_glitch_algorithm_package.json`)**:
  - 5 Capítulos com timestamps exatos ao longo dos 834.77s.
  - Metadados otimizados em 7 idiomas (EN, ES, PT-BR, DE, JA, KO, ZH).
  - Faixas de legendas e dublagem preparadas.
  - Comentário fixado de alta retenção + enquete da aba Comunidade.
  - Pacote de teste A/B/C de miniaturas para o YouTube Studio.
- **Auditoria de Conformidade & Green Dollar (`data/processed/compliance_report.json`)**:
  - Pontuação: **100/100 (APPROVED)** com proteção total EDSA e isenção educacional BBC/PBS.
  - Kit de Disputa Legal gerado contra alegações falsas de Content ID (`the_1983_soviet_glitch_content_id_dispute_kit.txt`).
- **Gerador Automático de Temas YouTube (15 a 30 min) (`src/topic_generator.py`)**:
  - 16 temas canônicos + motor procedural calibrado para 15 a 30 minutos em 5 categorias históricas.
  - Endpoints no Dashboard: `/api/topics/suggestions`, `/api/topics/generate`, `/api/topics/validate`.
- **Cinema Dashboard**: FastAPI Web SPA na porta `8502` com cockpit de autenticação triplo, painel dos 6 Golden Standards, gerador de temas e aprovação em 1 clique.

---

## 📊 Telemetria Atual do Pipeline

| Fase / Módulo | Status | Métricas Verificadas no Ambiente |
| :--- | :--- | :--- |
| **Gerador de Temas YouTube** | `ok` | **100% Green Dollar / EDSA Certificado**: Catálogo canônico e gerador procedural calibrado para 15 a 30 minutos |
| **Pre-Flight Auth Gate** | `ok` | **100% Autenticado & Liberado**: Google Flow, RunningHub e Flow Music ativos em `chrome_session/` |
| **6 Golden Standards** | `ok` | **100% Ativo & Enforçado**: Auth Gate, Dual-Shot Veo 3.1/Omni Flash, CosyVoice 3, Flow Music Zimmer, CC0 Foley & GPU Saver |
| **Hard Gate Storytelling (27 Livros)** | `ok` | **Score: 88.0/100 (Grade: A, Pronto para Produção: SIM)** em `data/processed/knowledge_audits/` |
| **Pesquisa & Roteiro Nolan** | `ok` | 40 cenas em 5 Atos (`data/scripts/nolan_soviet_glitch.json`) |
| **Engenharia de Voz & Áudio 4-Stem** | `ok` | 40 stems de voz + OST Zimmer + Foley tático + Sub-bass Braams a **-14.0 LUFS** (`pilot_final_audio_mix.mp3`) |
| **Motion Graphics & Overlays** | `ok` | Mapas vetoriais, esquemas isométricos CAD HyperFrames, fotos 4K SeedVR e 40 overlays táticos sincronizados |
| **Montagem Master 1080p Final** | `ok` | **134.9 MB / 834.77s (13.91 min)**: `the_1983_soviet_glitch_final_1080p.mp4` renderizado com Kodak 2383 3D LUT, letterbox 2.39:1 e legendas embutidas |
| **YouTube Shorts Funnel (3 Cortes)** | `ok` | 3 Shorts 9:16 gerados com background blur e legendas dinâmicas em `data/output/shorts/` |
| **YouTube Algorithm Package** | `ok` | 7 idiomas, 5 capítulos, cards, enquetes, pinned comment e miniaturas A/B/C em `the_1983_soviet_glitch_algorithm_package.json` |
| **YouTube Compliance QC** | `ok` | **Score: 100/100 (APPROVED)**, 100% Green Dollar elegível + Legal Dispute Kit gerado |
| **Cinema Dashboard (:8502)** | `ok` | Cockpit triplo de autenticação, 6 Golden Standards, seleção de temas e visualização do master pronto |
| **Codebase Hardening & Resiliência** | `ok` | **100% Concluído**: Eliminação de exceções silenciosas (`auth_gate` e `runninghub_bot`), validação de returncode FFmpeg, timeouts HTTP/Subprocess, desambiguação para `public_domain_research.py`, modernização para `pypdf>=4.0.0` e flag CLI `--clean-cache` |
| **4-Pillar Motion Orchestration** | `ok` | **100% Concluído**: Quotas de 4 Pilares Nolan (SeedVR 2.5 4K, Mapas Táticos, Blueprints CAD HyperFrames, Hero AI), pré-síntese Step 6.5, correção FFmpeg 7.1.1 e exportação de timeline OpenTimelineIO (.otio) |
| **Qualidade & Testes (Pytest)** | `ok` | **308 passed, 2 skipped, 1 warning** (zero falhas e zero regressões) |

---

## 🚀 Ciclo de Execução Padronizado (`run_pilot_pipeline.py`)
```text
Step 0:   auth_gate.py                 (Verifica/loga sessões persistentes Google Flow, RunningHub & Flow Music)
Step 1:   nolan_director.py            (Estrutura roteiro de 5 Atos, prompts Dual-Shot e distribuição dos 4 pilares)
Step 2:   research_engine.py           (Verificação de fatos e extração de fontes históricas)
Step 3:   google_flow_bot.py           (Geração de vídeo real no Google Flow com fallback MiniMax H3)
Step 4:   generate_pilot_audio.py      (Síntese vocal CosyVoice / Kokoro-82M)
Step 5:   cosyvoice_master.py          (Masterização de voz broadcast & geração de legendas SRT)
Step 6:   audio_mixer_master.py        (Mix 4-stems: voz + OST Zimmer + Foley + Braams a -14 LUFS)
Step 6.5: generate_motion_assets.py    (Mapas táticos, esquemas CAD HyperFrames, fotos 4K e carimbos)
Step 7:   render_pilot_video.py        (Montagem 1080p final, CinematicColorGrader Kodak 2383 e exportação .otio)
Step 8:   shorts_generator.py          (Geração dos 3 cortes verticais 9:16 para YouTube Shorts)
Step 9:   youtube_compliance_qc.py     (Auditoria de conformidade Green Dollar e Legal Dispute Kit)
Step 10:  youtube_algorithm_booster.py (Geração de SEO em 7 idiomas, capítulos e pacote de miniaturas A/B/C)
```
