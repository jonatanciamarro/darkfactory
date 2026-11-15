# Plan: Orquestração Visual Quádrupla (Vídeos IA + Fotos 4K SeedVR + Motion Step 6.5 + Texto Kinetic)

**Status**: Proposto para Aprovação  
**Data**: 2026-11-15  
**Mandato de Produção**: Todo episódio produzido DEVE conter:  
  1. **Vídeos de IA** (Google Flow Veo 3.1 / Omni Flash + Fallback RunningHub MiniMax H3)  
  2. **Fotos Históricas em 4K** (Upscale SeedVR 2.5 via RunningHub + Ken Burns Anamórfico)  
  3. **Motion Graphics Step 6.5** (Mapas táticos `MapAnimator` + Esquemas isométricos `HyperFrames`)  
  4. **Skills de Motion & Texto Kinetic** (`KineticCaptionEngine` + Overlays disparados por `VoiceAligner`)  
**Complexity**: Medium-High  

---

## 1. Summary
Este plano estabelece o padrão de produção visual definitivo do DarkFactory, garantindo que nenhum episódio seja monótono ou dependa exclusivamente de uma única mídia. O pipeline unifica:
1. Geração de vídeo real de IA (Google Flow / MiniMax H3).
2. Upscale 4K de fotografias de arquivo histórico com SeedVR 2.5 via RunningHub (`src/factory/seedvr_upscaler.py`).
3. Síntese antecipada de motion graphics no Step 6.5 (`src/generate_motion_assets.py`), gerando mapas táticos geopolíticos animados e blueprints CAD isométricos.
4. Tipografia cinética com legendas palavra por palavra (`KineticCaptionEngine`) e carimbos confidenciais (*TOP SECRET // DECLASSIFIED*) sincronizados milissegundo a milissegundo pelo `VoiceAligner`.
5. Color grading cinemático autoral cena a cena (`CinematicColorGrader` com Kodak 2383 / Bleach-Bypass / Oppenheimer Mono) e exportação multi-track OpenTimelineIO (`.otio`).

---

## 2. Patterns to Mirror

| Category | Source File | Pattern |
|---|---|---|
| Encoding | `src/auth_gate.py:27` | `sys.stdout.reconfigure(encoding="utf-8")` sob Windows (ADR-01) |
| Atomic Persistence | `src/video/map_animator.py:68` | Gravação em `.tmp.<pid>` seguida de `replace()` atômico (ADR-02) |
| RunningHub Bot Execution | `src/factory/runninghub_bot.py:1064` | `execute_mode='lite_plus'`, `close_unwanted_tabs`, anti-detection stealth |
| Ken Burns 4K Pan/Zoom | `src/render_pilot_video.py:215` | Movimento de câmera lento e orgânico (0.04 zoom/sec) sem cortes bruscos |
| Kinetic Safe Zones | `src/video/kinetic_captions.py:38` | Estilos `editorial_karaoke`, `hormozi_pop` dentro de `PLATFORM_SAFE_ZONES` |
| Film Grade Look | `src/video/cinematic_color.py:49` | `LOOK_REGISTRY[FilmLookProfile.KODAK_2383]` com curvas S e granulação analógica |
| Multi-Track NLE Timeline | `src/video/otio_exporter.py:83` | `UniversalTimelineExporter` com beat transients, markers e faixas desacopladas |
| Test Coverage | `tests/test_sprint10_shorts_and_captions.py` | Pytest com `tmp_path`, fixtures e zero chamadas externas de rede |

---

## 3. Files to Change

| File | Action | Why |
|---|---|---|
| `src/factory/seedvr_upscaler.py` | CREATE | Motor de Upscale 4K para fotos históricas usando SeedVR 2.5 no RunningHub com fallback local de alta fidelidade (Unsharp Mask + Lanczos 4K) para garantir operação contínua e sem quebras em testes. |
| `src/generate_motion_assets.py` | CREATE | Script CLI dedicado (Step 6.5) que itera o manifesto de cenas e pré-renderiza mapas vetoriais (`MapAnimator`), esquemas CAD/blueprint (`HyperFramesMotionEngine`), fotos históricas 4K (`SeedVR25Upscaler`) e carimbos (`TacticalGraphicsEngine`). |
| `src/render_pilot_video.py` | UPDATE | Suportar os 4 pilares: intercalar tomadas de IA, fotos históricas 4K com Ken Burns, mapas e blueprints; aplicar `CinematicColorGrader` dinamicamente conforme `color_palette_archetype`; sincronizar overlays via `VoiceAligner`; exportar a timeline multi-track `.otio`. |
| `src/nolan_director.py` | UPDATE | Garantir que o algoritmo de roteiro distribua harmonicamente os 4 pilares visuais em todos os episódios (tomadas heroicas de IA, fotos históricas 4K, mapas de teatro de operações e blueprints). |
| `run_pilot_pipeline.py` | UPDATE | Adicionar step `motion` (`generate_motion_assets.py`) nas fases `video` e `all`, antes de `render_pilot_video.py`. |
| `src/daemon_darkfactory.py` | UPDATE | Incluir a execução de `generate_motion_assets.py` no ciclo autônomo 24/7. |
| `tests/test_motion_pipeline.py` | CREATE | Suíte de testes unitários para a fase de motion assets, SeedVR 4K upscale, grading de cor e timeline `.otio`. |
| `state.md` | UPDATE | Atualizar arquitetura registrando o padrão dos 4 Pilares Visuais Obrigatórios. |

---

## 4. Implementation Tasks

### Task 1: Motor SeedVR 2.5 4K Upscaler (`src/factory/seedvr_upscaler.py`)
- **Action**:
  1. Criar `src/factory/seedvr_upscaler.py` com classe `SeedVR25Upscaler`.
  2. Implementar automação do workflow SeedVR 2.5 (3840x2160) no RunningHub (ou via API/Playwright com stealth).
  3. Implementar fallback local de alta nitidez com OpenCV (Lanczos4 4K upscale + CLAHE + Unsharp Masking + granulação sutil 35mm) para dry-run e testes unitários com zero falhas.
  4. Salvar imagens 4K em `data/final/images_4k/` e registrar no catálogo de B-roll histórico.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -c "from src.factory.seedvr_upscaler import SeedVR25Upscaler; print('SeedVR Upscaler import ok')"
  ```

### Task 2: Motor de Pré-Síntese de Motion Assets (Step 6.5 — `src/generate_motion_assets.py`)
- **Action**:
  1. Criar `src/generate_motion_assets.py` aceitando `--script`, `--dry-run`, `--force`.
  2. Varrer as 40 cenas do manifesto:
     - Se `visual_style_type == "TACTICAL_MAP_MOTION"`: acionar `MapAnimator` de `src.video.map_animator` e renderizar o mapa tático animado (pan/zoom, rotas vetoriais e pins de coordenadas).
     - Se `visual_style_type in ("ANATOMY_ISOMETRIC", "DECLASSIFIED_DOSSIER")` ou template `blueprint_notebook`: acionar `HyperFramesMotionEngine` e renderizar a placa vetorial 4-tons.
     - Se `visual_style_type == "ARCHIVAL_KEN_BURNS"`: acionar `SeedVR25Upscaler` para garantir que a foto histórica correspondente esteja upscalada para 4K UHD.
     - Pré-sintetizar carimbos táticos e HUDs com `TacticalGraphicsEngine`.
  3. Persistir todos os clipes em `data/final/motion_overlays/` e `data/broll/`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe src/generate_motion_assets.py --dry-run
  ```

### Task 3: Conexão dos 4 Pilares & Color Grader Dinâmico em `render_pilot_video.py`
- **Action**:
  1. Conectar `CinematicColorGrader` em `render_pilot_video.py`, lendo `color_palette_archetype` (Kodak 2383, Cold War Noir, Oppenheimer Mono).
  2. Suportar a intercalação das tomadas: vídeo de IA (Google Flow / MiniMax), fotos históricas 4K (com Ken Burns anamórfico e grain), mapas animados e blueprints.
  3. Conectar `VoiceAligner` para disparar os carimbos `TOP SECRET // DECLASSIFIED` e HUDs no timestamp exato da fala.
  4. Exportar a linha de tempo universal `.otio` multi-track via `UniversalTimelineExporter` em `data/output/timelines/the_1983_soviet_glitch_timeline.otio`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_render_pilot_video.py -q
  ```

### Task 4: Harmonização do Roteiro Nolan (`src/nolan_director.py`)
- **Action**:
  1. Garantir que `nolan_director.py` distribua nos 5 Atos as cotas mínimas de cada pilar visual:
     - Mínimo 4 cenas de **Fotos Históricas 4K SeedVR** (`ARCHIVAL_KEN_BURNS`).
     - Mínimo 2 cenas de **Mapas Táticos** (`TACTICAL_MAP_MOTION`).
     - Mínimo 2 cenas de **Blueprints/Anatomia** (`ANATOMY_ISOMETRIC` ou `DECLASSIFIED_DOSSIER`).
     - Demais cenas com **Vídeo de IA Dual-Shot** (`HERO_AI_DUAL_SHOT`).
     - Todas as cenas com prescrição de **Overlays Táticos e Texto Kinetic**.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe src/nolan_director.py --mode teaser
  ```

### Task 5: Orquestração no Pipeline e Daemon
- **Action**:
  1. Em `run_pilot_pipeline.py`, adicionar step `motion` (`generate_motion_assets.py`) antes de `render_pilot_video.py`.
  2. Em `src/daemon_darkfactory.py`, incluir `generate_motion_assets.py` no ciclo contínuo.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe run_pilot_pipeline.py --step motion --dry-run
  ```

### Task 6: Suíte de Testes Automatizados (`tests/test_motion_pipeline.py`)
- **Action**:
  1. Criar testes para `SeedVR25Upscaler` (modo local e dry-run).
  2. Criar testes para `generate_motion_assets.py` cobrindo mapas, blueprints e overlays.
  3. Validar a geração e integridade da timeline `.otio` exportada.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_motion_pipeline.py -q
  ```

---

## 5. Validation Commands

```powershell
# 1. Teste isolado do SeedVR 2.5 4K Upscaler
.\venv\Scripts\python.exe -c "from src.factory.seedvr_upscaler import SeedVR25Upscaler; u = SeedVR25Upscaler(); print('SeedVR Engine initialized successfully')"

# 2. Execução da pré-síntese de motion em dry-run
.\venv\Scripts\python.exe src/generate_motion_assets.py --dry-run

# 3. Validação da suíte de testes de motion
.\venv\Scripts\python.exe -m pytest tests/test_motion_pipeline.py -q

# 4. Suíte global garantindo 265+ testes passando
.\venv\Scripts\python.exe -m pytest -q
```

---

## 6. Acceptance Criteria
- [ ] `src/factory/seedvr_upscaler.py` criado com upscale 4K para fotos históricas (RunningHub + fallback de alta fidelidade).
- [ ] `src/generate_motion_assets.py` implementado gerando mapas táticos, blueprints e fotos 4K antes do render.
- [ ] `render_pilot_video.py` aplicando `CinematicColorGrader` dinâmico e exportando timeline multi-track `.otio`.
- [ ] `nolan_director.py` estruturando o roteiro com distribuição garantida dos 4 pilares visuais.
- [ ] `run_pilot_pipeline.py` e `daemon_darkfactory.py` orquestrando o step de motion.
- [ ] Suíte de testes `test_motion_pipeline.py` 100% verde com suíte global de testes passando sem regressões.
- [ ] `state.md` atualizado e commit/push na branch `main`.
