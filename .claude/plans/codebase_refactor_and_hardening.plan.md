# Plan: DarkFactory Codebase Hardening & Refactoring

**Source PRD**: `docs/AUDIT_REPORT.md`  
**Complexity**: Medium  
**Estimated Effort**: 1 Sessão Focada (3 a 4 horas)  
**Status**: Proposto (Aguardando Confirmação do Usuário)

---

## 1. Summary

Este plano estabelece a blindagem técnica, resolução de erros silenciosos e desambiguação arquitetural do DarkFactory identificados na auditoria de 16/11/2026. O objetivo é elevar a confiabilidade da esteira de produção para 100% de previsibilidade operacional:
1. Eliminar o mascaramento de falhas em automações web e parsing (`auth_gate.py`, `runninghub_bot.py`).
2. Blindar comandos FFmpeg e chamadas HTTP com timeouts e checagens explícitas de código de saída.
3. Desambiguar o namespace crítico (`research_engine.py` vs `public_domain_research.py`).
4. Purgar scripts órfãos/obsoletos sem afetar os 308 testes aprovados.
5. Atualizar a dependência depreciada `PyPDF2` para `pypdf`.

---

## 2. Patterns to Mirror

| Category | Source File | Pattern |
|---|---|---|
| Encoding & Windows Guard | `src/auth_gate.py:27` | `sys.stdout.reconfigure(encoding="utf-8")` sob Windows (ADR-01) |
| Structured Logging | `src/audio_mixer_master.py:25` | `logging.getLogger(...)` com nível e formato estruturado |
| Atomic File Writing | `src/video/research_engine.py:27` | `_atomic_write_json(path, payload)` com `.tmp.<pid>` e `os.replace()` |
| Subprocess Checking | `src/video/ffmpeg_processor.py:120` | `subprocess.run(..., check=True, timeout=120.0, capture_output=True)` |
| Test Coverage | `tests/test_auth_gate.py` | Pytest fixtures com mocks isolados, sem dependências de rede externa |

---

## 3. Files to Change

| File | Action | Why |
|---|---|---|
| `src/auth_gate.py` | UPDATE | Substituir 23 blocos `except Exception: pass` por `logger.debug` / `logger.warning`, expondo erros de cookies e sessões. |
| `src/factory/runninghub_bot.py` | UPDATE | Substituir 39 blocos `except Exception: pass` por log de seletores e raise de falhas de navegação críticas. |
| `src/cosyvoice_master.py` | UPDATE | Adicionar checagem de `res.returncode == 0` na concatenação FFmpeg (linha 293). |
| `src/render_pilot_video.py` | UPDATE | Adicionar validação de saída de render e concatenação do FFmpeg (linhas 456, 488). |
| `src/generate_pilot_audio.py` | UPDATE | Validar código de saída do FFmpeg nas conversões WAV/MP3 (linhas 67, 154). |
| `src/video/minimax_h3_engine.py` | UPDATE | Adicionar `timeout=60.0` nas chamadas `requests.post` e `requests.get` (linhas 189, 317, 347). |
| `src/video/minimax_music_engine.py` | UPDATE | Adicionar `timeout=60.0` nas requisições HTTP de polling (linhas 167, 269). |
| `src/video/voice_engine.py` | UPDATE | Adicionar `timeout=30.0` nas requisições de TTS via HTTP (linha 231). |
| `src/video/research_engine.py` | RENAME / MOVE | Renomear para `src/video/public_domain_research.py` para eliminar colisão com `src/research_engine.py`. |
| `src/research_engine.py` | UPDATE | Atualizar import de `from src.video.public_domain_research import PublicDomainResearchEngine`. |
| `src/video/documentary_composer.py` | UPDATE | Atualizar import de `public_domain_research`. |
| `tests/test_public_domain_research_engine.py` | UPDATE | Atualizar import para `public_domain_research`. |
| `src/generate_sound_design.py` | DELETE / ARCHIVE | Remover script órfão obsoleto com durações hardcoded. |
| `src/generate_cinematic_lut.py` | MOVE | Mover para `scripts/tools/generate_cinematic_lut.py` como utilitário offline. |
| `requirements.txt` | UPDATE | Substituir `PyPDF2>=3.0.0` por `pypdf>=4.0.0`. |
| `src/video/knowledge_distiller.py` | UPDATE | Atualizar import de `pypdf` e chamada `PdfReader`. |
| `run_pilot_pipeline.py` | UPDATE | Adicionar flag `--clean-cache` para purga de sessões e quarentena antiga (> 7 dias). |
| `state.md` | UPDATE | Registrar a conclusão do refactor e hardening da esteira. |

---

## 4. Implementation Tasks

### Task 1: Blindagem de Erros Silenciosos (Logging Estruturado & Subprocess)
- **Action**:
  1. No `src/auth_gate.py`, substituir `pass` silenciosos por `logger.warning(..., exc_info=True)`.
  2. No `src/cosyvoice_master.py`, `src/render_pilot_video.py` e `src/generate_pilot_audio.py`, verificar `res.returncode == 0` e levantar `RuntimeError` explicativo se o FFmpeg abortar.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_auth_gate.py tests/test_narration.py tests/test_cinematic_pipeline.py -q
  ```

### Task 2: Resiliência de Rede (Timeouts em Chamadas HTTP)
- **Action**:
  1. Fixar `timeout=60.0` em todas as chamadas de rede do MiniMax (`minimax_h3_engine.py`, `minimax_music_engine.py`).
  2. Fixar `timeout=30.0` em `src/video/voice_engine.py`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_minimax_h3_video.py tests/test_minimax_music.py -q
  ```

### Task 3: Desambiguação de Namespace (`research_engine` -> `public_domain_research`)
- **Action**:
  1. Renomear `src/video/research_engine.py` para `src/video/public_domain_research.py`.
  2. Atualizar imports em `src/research_engine.py`, `src/video/documentary_composer.py` e `tests/test_public_domain_research_engine.py`.
  3. Mover `src/generate_cinematic_lut.py` para `scripts/tools/` e remover `src/generate_sound_design.py`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_research_engine.py tests/test_public_domain_research_engine.py -q
  ```

### Task 4: Modernização de Dependências & Purga de Quarentena
- **Action**:
  1. No `requirements.txt`, trocar `PyPDF2` por `pypdf`.
  2. Atualizar `src/video/knowledge_distiller.py` para usar `import pypdf`.
  3. No `run_pilot_pipeline.py`, implementar `--clean-cache` que apaga arquivos em `data/quarantine/` com mais de 7 dias e limpa `chrome_session/Default/Cache`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest -q
  ```
  (Verificar que o warning de depreciação do PyPDF2 desaparece completamente e todos os 308 testes continuam verdes).

---

## 5. Validation Matrix

```powershell
# 1. Validação unitária rápida
.\venv\Scripts\python.exe -m pytest tests/test_auth_gate.py tests/test_public_domain_research_engine.py -q

# 2. Suíte completa de regressão (308 testes)
.\venv\Scripts\python.exe -m pytest -q

# 3. Dry-run do pipeline
.\venv\Scripts\python.exe run_pilot_pipeline.py --step auth --dry-run
```

---

## 6. Risks & Mitigations

| Risco | Probabilidade | Severidade | Mitigação |
| :--- | :---: | :---: | :--- |
| Quebra de imports em testes ao renomear `research_engine.py` | Média | Baixa | `tests/test_public_domain_research_engine.py` atualizado no mesmo commit atômico |
| Exceções antes mascaradas no `runninghub_bot` quebrando testes | Baixa | Média | Usar `logger.warning` em fluxos tolerantes a falha e `raise` apenas em falhas irrecuperáveis |
| Regressão na suíte de testes (308 testes) | Baixa | Alta | Executar `pytest -q` após cada Task individual antes de prosseguir |
