# 📐 Design Patterns no DarkFactory — Mapeamento Real no Código

> **Catálogo de Padrões GoF e Arquiteturais Modernos Extraídos da Base de Código Real**
> Cada padrão é documentado com o arquivo e linhas exatos onde é aplicado no DarkFactory, seu propósito no sistema e o script de defesa para entrevistas técnicas.

---

## 1. Strategy Pattern (Padrão Estratégia)

- **📁 Arquivo**: `src/video/voice_router.py`
- **📍 Linhas**: 39-45 e 160-220
- **Código no Projeto**:
  ```python
  # Narration Engines (src/video/voice_router.py:39-45)
  ENGINE_COSYVOICE = "cosyvoice"          # Tier 1: Gold Standard Lossless (RunningHub)
  ENGINE_KOKORO_LOCAL = "kokoro_local"    # Tier 2: Fallback 1 (Local Neural ONNX)
  ENGINE_DEEPGRAM = "deepgram"            # Tier 3: Fallback 2 (Deepgram Aura API)

  DEFAULT_KOKORO_VOICE = "bm_george"
  DEFAULT_DEEPGRAM_VOICE = "aura-helios-en"
  ```
- **Conceito & Aplicação**: O `MasterVoiceRouter` encapsula diferentes algoritmos de síntese de voz (TTS) sob uma interface comum. O chamador invoca `synthesize_scene(scene_id, text, instruct)` sem precisar saber se a renderização ocorrerá via GPU remota no RunningHub, inferência neural local via ONNX Runtime ou requisição HTTP à Deepgram.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Aplicamos o Strategy Pattern no roteador de voz para desacoplar a política de narração das implementações concretas dos sintetizadores. O cliente solicita a síntese de uma cena documental e o router seleciona a estratégia em tempo de execução com base em disponibilidade e cotas. Isso segue o Open/Closed Principle: adicionar um novo provedor como ElevenLabs significa apenas plugar uma nova estratégia sem alterar nenhuma linha do pipeline de montagem."*

---

## 2. Chain of Responsibility (Cadeia de Responsabilidade)

- **📁 Arquivo**: `src/kokoro_fallback.py`
- **📍 Linhas**: 35-65
- **Código no Projeto**:
  ```python
  # Voice & Pacing Profile Mapping for Documentary Production (src/kokoro_fallback.py:35-50)
  INSTRUCT_PROFILE_MAP = [
      {
          "keywords": ["urgent", "urgency", "mounting dread", "alarm", "crisis"],
          "voice": "bm_lewis",
          "speed": 1.02,
          "pitch": "-1Hz",
          "edge_fallback": "en-US-ChristopherNeural",
          "style_desc": "High tension, mounting dread, articulate dramatic urgency (Lewis)",
      },
      {
          "keywords": ["grim", "somber", "heavy", "existential", "tragic", "grave"],
          "voice": "bm_george",
          "speed": 0.96,
          "pitch": "-2Hz",
          "edge_fallback": "en-US-EricNeural",
          "style_desc": "Somber, heavy existential baritone, historical gravitas (George)",
      },
      ...
  ]
  ```
- **Conceito & Aplicação**: O pipeline de fallback de voz atua como uma cadeia onde cada manipulador tenta satisfazer a requisição: primeiro CosyVoice 3; em caso de falha de conexão ou quota, a requisição é passada automaticamente para o motor local Kokoro-82M; se o modelo neural local falhar por falta de dependências ONNX, o handler transfere a responsabilidade para a síntese via Edge-TTS.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Utilizamos a Chain of Responsibility para resiliência de áudio. Se um elo da cadeia falhar, a requisição propaga sequencialmente para o próximo manipulador até que um deles consiga gerar o stem de áudio. É o mesmo princípio adotado em middlewares de frameworks como Express.js ou Django, garantindo que o documentário continue sendo produzido mesmo em cenário de degradação parcial de infraestrutura."*

---

## 3. Invariant Enforcement (Imposição de Invariante de Domínio)

- **📁 Arquivo**: `src/video/voice_router.py`
- **📍 Linhas**: 47-50
- **Código no Projeto**:
  ```python
  class NarratorConsistencyViolationError(RuntimeError):
      """Raised when an attempt is made to switch narrators midway through a video."""
      pass
  ```
- **Conceito & Aplicação**: Em Domain-Driven Design (DDD), invariantes são regras de negócio que devem permanecer sempre verdadeiras durante todo o ciclo de vida da entidade. A troca acidental de narrador no meio de um documentário destrói a imersão cinematográfica. O `NarratorConsistencyViolationError` é uma restrição tipada que impede execuções que violem essa premissa.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Em vez de tratar restrições críticas de negócio com meros ifs e logs, modelamos o invariante como uma exceção semântica de domínio. Se uma rotina tentar sintetizar a cena 15 com uma voz diferente da cena 1 travada no projeto, o sistema aborta com `NarratorConsistencyViolationError`. Preferimos falhar expressamente a permitir corrupção da integridade artística da obra."*

---

## 4. Value Object / Imutabilidade com Dataclass

- **📁 Arquivo**: `src/video/voice_router.py`
- **📍 Linhas**: 52-60 e 62-70
- **Código no Projeto**:
  ```python
  @dataclass
  class NarratorLock:
      """Locks a single voice and engine for an entire video project."""
      video_id: str
      engine: str
      voice_id: str
      created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
      scenes_completed: List[str] = field(default_factory=list)

  @dataclass
  class RoutedNarrationResult:
      """Result of a narration synthesis pass."""
      video_id: str
      scene_id: str
      audio_path: Path
      filename: str
      duration_seconds: float
      filesize_bytes: int
  ```
- **Conceito & Aplicação**: Uso de `@dataclass` como *Value Objects* imutáveis do DDD. O `NarratorLock` e `RoutedNarrationResult` encapsulam dados fortemente tipados, prevenindo que dicionários genéricos e mutáveis circulem pela aplicação carregando inconsistências ou chaves ausentes.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Substituímos dicionários arbitrários por dataclasses estruturadas. Em Python, isso equivale aos Records do Java 16 ou data classes do Kotlin. Ganhamos autocompletion na IDE, validação de tipos estática com mypy e eliminamos bugs onde campos renomeados passavam desapercebidos em tempo de execução."*

---

## 5. Abstract Factory (Fábrica Abstrata)

- **📁 Arquivo**: `src/video/darkfactory_t2v.py`
- **📍 Linhas**: 40-75
- **Código no Projeto**:
  ```python
  NARRATIVE_ARCHETYPES = {
      "cold_war_espionage": {
          "title": "Cold War Nuclear Tension & False Alarm",
          "color_palette": "Military olive drab, CRT phosphor green (#00FF66), blood red alarm strobes...",
          "optics": "Cooke Anamorphic 35mm f/2.0, shallow depth of field, 2.39:1 letterbox, Kodak Vision3 500T 5219...",
          "scenes": [
              {
                  "scene_id": 1,
                  "title": "The First Nuclear Alarm Beacon",
                  "shot_a": {"focus": "character_tension", "camera": "Slow cinematic push-in...", ...},
                  "shot_b": {"focus": "tactical_macro", "camera": "Handheld visceral drift...", ...}
              }, ...
          ]
      }
  }
  ```
- **Conceito & Aplicação**: O Abstract Factory é utilizado para criar famílias de objetos visuais relacionados sem acoplamento à sua representação concreta. Cada arquétipo narrativo (ex: Guerra Fria, Mistério Desclassificado) produz um conjunto coeso de prompts: Shot A (drama humano/chiaroscuro) e Shot B (macro tático/CRT), compartilhando o mesmo perfil óptico e paleta cromática.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Aplicamos Abstract Factory na geração visual: cada arquétipo é uma fábrica que instancia prompts de vídeo acoplados conceitualmente — Shot A focado no drama psicológico e Shot B focado em texturas macro, compartilhando a mesma película Kodak e lentes anamórficas. Isso assegura que 40 takes gerados por modelos de IA mantenham a exata mesma identidade estética."*

---

## 6. Lifespan Context Manager & RAII (Resource Acquisition Is Initialization)

- **📁 Arquivo**: `src/dashboard/app.py`
- **📍 Linhas**: 44-59
- **Código no Projeto**:
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      """Lifecycle manager for startup telemetry and graceful shutdown."""
      runner.broadcast_log("🎬 DarkFactory Cinema Dashboard starting on http://localhost:8502", "SYSTEM")
      yield
      runner.broadcast_log("🛑 DarkFactory Cinema Dashboard shutting down.", "SYSTEM")
      for task_name in list(runner._running_tasks.keys()):
          runner.terminate_task(task_name)

  app = FastAPI(
      title="DarkFactory Cinema Dashboard",
      lifespan=lifespan,
  )
  ```
- **Conceito & Aplicação**: O padrão RAII (originário do C++) assegura que a aquisição e liberação de recursos fiquem amarradas ao ciclo de vida de um objeto de contexto. No FastAPI moderno, `@asynccontextmanager async def lifespan` substitui os antigos eventos `on_event("startup")` e `on_event("shutdown")`, garantindo que processos filhos iniciados pelo dashboard sejam terminados de forma limpa mesmo em caso de crash.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Utilizamos o lifespan context manager para implementar o padrão RAII no FastAPI. Antes do yield executamos o bootstrapping de telemetria; no teardown após o yield, iteramos sobre todos os subprocessos ativos de renderização e enviamos sinais de encerramento seguro. Isso impede que processos órfãos do FFmpeg continuem travando núcleos de CPU caso a aplicação receba um SIGINT."*

---

## 7. Pipeline Pattern & Subprocess Isolation

- **📁 Arquivo**: `run_pilot_pipeline.py`
- **📍 Linhas**: 36-48 e 80-93
- **Código no Projeto**:
  ```python
  def run_script(script_name: str, dry_run: bool = False, extra_args: list = None) -> bool:
      target = SRC_DIR / script_name
      cmd = [PYTHON_EXE, "-u", str(target)]
      if dry_run and script_name in DRY_RUN_SUPPORTED:
          cmd.append("--dry-run")
      if extra_args:
          cmd.extend(extra_args)
      res = subprocess.run(cmd)
      return res.returncode == 0
  ```
- **Conceito & Aplicação**: O Pipeline Pattern decompõe uma tarefa complexa em uma sequência ordenada de estágios independentes (Steps 0 a 11). Cada estágio é executado em um subprocesso Python dedicado.
- **🎓 Script para Entrevista (30-45s)**:
  > *"O isolamento por subprocessos traz crash safety: se uma biblioteca nativa em C do FFmpeg sofrer um segmentation fault durante a codificação do vídeo, o processo do orquestrador principal não é derrubado. Ele intercepta o exit code diferente de zero, loga o incidente e impede a execução dos passos subsequentes, preservando os artefatos intermediários intactos."*

---

## 8. Quarantine Pattern / Dead Letter Queue (DLQ)

- **📁 Arquivo**: `data/quarantine/`, `src/video/motion_qa.py` e **ADR-04** em `AGENTS.md`
- **Conceito & Aplicação**: Takes de vídeo que apresentam deformidades visuais, congelamento óptico ou dessincronização não são simplesmente descartados nem aprovados para a montagem. Eles são isolados em `data/quarantine/vid_<id>/` acompanhados de um relatório descritivo `quarantine_report.json`.
- **🎓 Script para Entrevista (30-45s)**:
  > *"O Quarantine Pattern é a transposição do conceito de Dead Letter Queue (DLQ) de sistemas de mensageria (RabbitMQ, SQS) para o processamento de mídia. Em vez de descartar silenciosamente um take que falhou no QA visual, nós o isolamos com seus metadados. Isso viabiliza post-mortem auditável e treinamento futuro de regras de controle de qualidade sem poluir o diretório de entrega final."*

---

## 9. Observer Pattern / Event Broadcaster (SSE Streaming)

- **📁 Arquivo**: `src/dashboard/runner.py`
- **📍 Linhas**: 28-50
- **Código no Projeto**:
  ```python
  _log_history: collections.deque = collections.deque(maxlen=1000)
  _log_listeners: List[asyncio.Queue] = []

  def broadcast_log(message: str, level: str = "INFO") -> None:
      now = datetime.datetime.now().strftime("%H:%M:%S")
      entry = f"[{now}] [{level}] {message}"
      _log_history.append(entry)
      for q in list(_log_listeners):
          try:
              q.put_nowait(entry)
          except Exception:
              pass
  ```
- **Conceito & Aplicação**: O Observer Pattern desacopla os emissores de eventos de log dos seus consumidores. O método `broadcast_log` notifica de forma assíncrona todas as filas `asyncio.Queue` ativas cadastradas pelos clientes conectados via Server-Sent Events (SSE).
- **🎓 Script para Entrevista (30-45s)**:
  > *"Implementamos o Observer Pattern em memória para a telemetria do dashboard. O runner mantém uma lista de filas de ouvintes e um buffer circular com os últimos 1000 logs. Quando um novo evento de pipeline ocorre, ele é transmitido para todos os clientes conectados sem acoplamento entre a execução do script e a interface web."*

---

## 10. Specification / Rule Engine Pattern

- **📁 Arquivo**: `src/video/story_validator.py`
- **📍 Linhas**: 45-120
- **Conceito & Aplicação**: O Specification Pattern encapsula regras de negócio combináveis que determinam se um objeto atende a critérios estritos. O `story_validator.py` avalia roteiros contra um conjunto de especificações independentes: regra dos 60 segundos de MrBeast, proibição de buzzwords genéricas (`BANNED_HOOK_BUZZWORDS`) e eye-trace de Walter Murch.
- **🎓 Script para Entrevista (30-45s)**:
  > *"O validador de roteiro foi estruturado como um Specification Rule Engine. Cada regra de retenção narrativa é um predicado isolado que avalia o roteiro e retorna um score e uma justificativa. Isso permite adicionar novas regras teóricas de storytelling sem reescrever o algoritmo central de cálculo de aprovação."*

---

## 11. Facade Pattern (Fachada Arquitetural)

- **📁 Arquivos**: `src/video/audio_engine.py` e `src/ai_engine_suite.py`
- **Conceito & Aplicação**: A fachada fornece uma interface de alto nível simplificada para um subsistema complexo com dezenas de dependências internas (FFmpeg, Sox, Kokoro, CosyVoice, Whisper). O `audio_engine.py` permite ao pipeline disparar `compose_soundtrack(scene_manifest)` sem que o cliente conheça a complexidade de sidechains e normalização de LUFS.
- **🎓 Script para Entrevista (30-45s)**:
  > *"Usamos o Facade Pattern para encapsular a engenharia de áudio. Os orquestradores de montagem interagem com um método de alto nível, enquanto a fachada coordena internamente ducking de frequências, renderização de foley e filtros de loudness EBU R128."*

---

## 12. Adapter Pattern (Adaptador)

- **📁 Arquivo**: `src/video/minimax_music_engine.py`
- **Conceito & Aplicação**: Converte a interface e formatos proprietários de uma API de terceiros (MiniMax) na interface padronizada de áudio esperada pelo DarkFactory (`AudioStem`).
- **🎓 Script para Entrevista (30-45s)**:
  > *"O Adapter Pattern protege nosso núcleo de negócio contra variações de APIs externas. Se a MiniMax alterar seu payload de resposta ou formato de amostragem de áudio, alteramos apenas o adaptador correspondente, mantendo o mixer e a timeline completamente isolados."*
