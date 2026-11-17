# 🎯 20 Perguntas Que Vão Te Fazer Sobre o DarkFactory

> **Scripts de Resposta em Formato STAR (Situation, Task, Action, Result)**
> Cada resposta foi estruturada e cronometrada para entrega em **60 a 90 segundos**, com linguagem técnica natural, assertiva e foco em maturidade de engenharia (Senior / Staff level).

---

## 🏗️ Bloco 1: Arquitetura & Decisões Fundamentais

### 1. "Me explica a arquitetura geral do sistema e como as peças se conectam."
- **⏱️ Duração Alvo**: ~75 segundos
- **🔑 Buzzwords**: Pipeline Architecture, Orchestrator Pattern, Subprocess Isolation, Fail-Fast, Imutabilidade de Artefatos.
- **S (Situation)**: Precisávamos de uma fábrica autônoma capaz de produzir documentários históricos de alta fidelidade cinematográfica (14 a 30 minutos) sem intervenção humana manual, orquestrando dezenas de modelos de IA, ferramentas de áudio e FFmpeg.
- **T (Task)**: Desenvolver uma esteira ponta a ponta previsível, testável e auditável, que não ficasse em estado inconsistente caso uma API externa ou processo de renderização falhasse.
- **A (Action)**: Projetei uma arquitetura em esteira (*Pipeline Architecture*) com um Orquestrador central (`run_pilot_pipeline.py`) dividida em 11 etapas sequenciais. Cada etapa roda em isolamento de subprocesso com entradas e saídas versionadas em disco via contratos JSON e artefatos imutáveis. Adotei o princípio *fail-fast*: se a validação de roteiro ou a autenticação de GPU falhar no início, o pipeline aborta antes de queimar créditos de renderização.
- **R (Result)**: Renderizamos documentários completos de 40 cenas (13.91 minutos) com 314 testes automatizados cobrindo o ecossistema, zero dead air e conformidade broadcast estrita.

---

### 2. "Por que Python foi a escolha principal e não Go ou Node.js?"
- **⏱️ Duração Alvo**: ~65 segundos
- **🔑 Buzzwords**: Ecosystem Dominance, ONNX Runtime, Binding FFmpeg, Polyglot Overhead, I/O Bound.
- **S (Situation)**: O projeto exigia orquestração de modelos neurais de áudio locais, visão computacional, renderização de vídeo e automação web.
- **T (Task)**: Escolher uma linguagem com produtividade máxima e suporte nativo às bibliotecas de inteligência artificial.
- **A (Action)**: Avaliei Go e Node.js. Go seria excelente para concorrência de rede pura, mas não possui ecossistema para inferência ONNX de áudio local (`Kokoro-82M`), manipulação de áudio com `scipy`/`numpy` ou bindings maduros para o ecossistema científico. Node.js seria viável para o dashboard e Playwright, mas introduziria polyglot overhead e duplicidade de contratos de dados. Python cobriu todo o espectro: FastAPI com async nativo para o dashboard, Playwright nativo para RPA, `onnxruntime` para fallback local e bindings FFmpeg. Como nosso gargalo são chamadas externas de rede e GPU externa (I/O bound), o GIL do Python não é fator limitante.
- **R (Result)**: Unificação de 100% da stack em um único runtime gerenciado com tipagem estrita via Pydantic e Type Hints.

---

### 3. "Por que escolher FastAPI em vez de Django ou Flask para o Cinema Dashboard?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Native Async/Await, Lifespan Context Manager, Pydantic v2 DTOs, OpenAPI Contract, Lightweight SPA.
- **S (Situation)**: O dashboard precisava monitorar execuções longas de pipeline, transmitir logs de subprocessos em tempo real e fornecer uma interface SPA de controle.
- **T (Task)**: Construir um backend enxuto, tipado e com excelente suporte a operações assíncronas.
- **A (Action)**: Descartei Django porque sua estrutura pesada (ORM relacional, engine de templates, painel admin, sistema de migrações) seria puro overhead para uma aplicação onde o estado da esteira é baseado em arquivos JSON e processos do sistema operacional. Flask exigiria múltiplos plugins de terceiros para validação e async. O FastAPI entregou suporte nativo a `async/await`, integração nativa com `Pydantic v2` para validação de esquemas de dados, documentação Swagger automática e o `lifespan context manager` para inicialização e shutdown seguro de processos em segundo plano.
- **R (Result)**: Uma API de baixa latência na porta 8502, com zero dependências de banco de dados e gerenciamento resiliente do ciclo de vida dos subprocessos.

---

### 4. "Por que o estado do sistema é baseado em arquivos JSON e não em um banco PostgreSQL?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Write-Once-Read-Many (WORM), Zero External Dependencies, Portable Artifacts, Git-Auditability.
- **S (Situation)**: O pipeline gera metadados em cada etapa: dossiês de pesquisa, roteiros de 40 cenas, timestamps de áudio, relatórios de conformidade e manifests de vídeo.
- **T (Task)**: Definir a camada de persistência para as entidades do pipeline.
- **A (Action)**: Optei deliberadamente por persistência em arquivos JSON estruturados em diretórios organizados (`data/scripts/`, `data/processed/`, `data/audio/`). Para o cenário de um pipeline industrial em lote, o padrão de acesso é WORM (*Write Once, Read Many*). Arquivos JSON garantem portabilidade total, podem ser inspecionados com qualquer editor sem necessidade de rodar daemons de banco de dados, podem ser versionados ou arquivados junto com os binários de mídia (`.mp4`, `.wav`) e eliminam migrations em fases exploratórias.
- **R (Result)**: Zero overhead de infraestrutura, facilidade de mock nos 314 testes automatizados e histórico de builds auto-contido.

---

## 🎙️ Bloco 2: Engenharia de Áudio & Resiliência

### 5. "Como funciona a cadeia de fallback de voz e o que é o 'NarratorLock'?"
- **⏱️ Duração Alvo**: ~80 segundos
- **🔑 Buzzwords**: Circuit Breaker, Fallback Chain, Domain Invariant, Fail-Safe, Acoustic Identity.
- **S (Situation)**: Modelos de TTS em nuvem (como CosyVoice via RunningHub) podem sofrer instabilidade temporária de rede ou exaustão de cotas de GPU durante a síntese de um documentário de 40 cenas.
- **T (Task)**: Criar resiliência para que a produção de áudio não trave, sem permitir que a voz do documentário mude no meio do vídeo.
- **A (Action)**: Implementei no `voice_router.py` uma cadeia de três níveis: CosyVoice em nuvem → Kokoro-82M neural local (ONNX em CPU) → Edge-TTS. No entanto, criei uma regra de negócio invariante chamada `NarratorLock`: quando a primeira cena é sintetizada, o identificador de timbre e velocidade é travado para o projeto inteiro. Se o motor primário falhar na cena 20, o sistema só faz o fallback se conseguir preservar o mesmo perfil acústico do narrador; caso contrário, dispara a exceção `NarratorConsistencyViolationError` e interrompe o job.
- **R (Result)**: Zero inconsistências vocais no episódio final. Se houver falha irrecuperável, o sistema prefere falhar expressamente a entregar um documentário com vozes misturadas.

---

### 6. "O que é normalização EBU R128 (-14 LUFS / -1.0 dBTP) e por que ela é mandatória?"
- **⏱️ Duração Alvo**: ~75 segundos
- **🔑 Buzzwords**: Loudness Normalization, EBU R128, ITU-R BS.1770, True Peak, Codec Clipping, Penalty Algorithms.
- **S (Situation)**: Se você subir um vídeo para o YouTube ou streaming com volume muito alto ou baixo, os algoritmos da plataforma aplicam normalização automática destrutiva ou o espectador abandona o vídeo pelo desconforto auditivo.
- **T (Task)**: Garantir conformidade acústica de nível broadcast em todos os episódios produzidos.
- **A (Action)**: Implementei no `audio_mixer_master.py` uma rotina de normalização two-pass baseada no padrão internacional EBU R128 / ITU-R BS.1770. Na primeira passada, o FFmpeg analisa o Integrated Loudness e o True Peak do áudio. Na segunda passada, aplica ganho linear e compressão com alvo exato em **-14.0 LUFS (±0.5)** e teto de **-1.0 dBTP (True Peak)**. O limite de -1.0 dBTP impede que a compressão lossy subsequente (AAC/Opus do YouTube) gere inter-sample clipping e distorção harmônica.
- **R (Result)**: Áudio com pressão acústica consistente, máxima clareza em dispositivos móveis e zero penalidade de atenuação pelo player do YouTube.

---

### 7. "Como vocês detectaram e trataram o problema de exceções silenciosas no projeto?"
- **⏱️ Duração Alvo**: ~80 segundos
- **🔑 Buzzwords**: Silent Failures, Bare Excepts, Root Cause Analysis, Defensive Logging, Fail-Fast.
- **S (Situation)**: Em execuções noturnas, o pipeline às vezes concluía sem erros explícitos no console, mas os arquivos de vídeo finais não eram gerados.
- **T (Task)**: Realizar auditoria técnica para identificar e erradicar falhas mascaradas no código.
- **A (Action)**: Na análise de causa raiz, descobri blocos com `except: pass` nos módulos `src/auth_gate.py` e `src/factory/runninghub_bot.py`. O código capturava falhas de autenticação de sessão e erros de timeout HTTP e os descartava silenciosamente. O pipeline continuava rodando como se nada tivesse acontecido, gerando erros crípticos em etapas muito posteriores. Refatorei todos os pontos substituindo por tratamento tipado de exceções (`requests.RequestException`, `subprocess.CalledProcessError`), logging estruturado do stack trace com `logger.error()` e propagação explícita com `raise`.
- **R (Result)**: Esse endurecimento de código (*codebase hardening*) foi documentado no `state.md`. O tempo de diagnóstico de falhas caiu de horas para segundos, com mensagens claras no ponto exato do erro.

---

## 🎬 Bloco 3: Fábrica de Vídeo, Automação & Performance

### 8. "Por que usar automação de browser (Playwright) em vez de APIs oficiais para alguns serviços?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Pragmatic Engineering, Time-to-Market, Headless Automation, Stealth Profile, Vendor Lock-in.
- **S (Situation)**: Ferramentas de geração de vídeo de ponta como Google Flow (Veo 3.1) não possuíam APIs públicas abertas no momento da implementação ou possuíam filas de espera de meses.
- **T (Task)**: Viabilizar a produção imediata com as melhores tecnologias visuais do mercado sem depender de aprovações burocráticas de acesso a APIs.
- **A (Action)**: Adotamos automação de browser via Playwright com persistência de sessões de usuário (`chrome_session/`) e um módulo de camuflagem (`stealth_profile.py`) que mascara propriedades de automação do JavaScript. Reconhecemos que isso é um trade-off: aceitamos a fragilidade de mudanças no DOM da interface web em troca da capacidade imediata de usar a melhor qualidade de geração visual disponível.
- **R (Result)**: Conseguimos renderizar cenas cinematográficas com modelos que a concorrência não conseguia integrar, mantendo fallbacks prontos para quando APIs oficiais forem disponibilizadas.

---

### 9. "Como funciona a otimização de custo de GPU no RunningHub?"
- **⏱️ Duração Alvo**: ~65 segundos
- **🔑 Buzzwords**: Resource Cleanup, Cost Governance, Atomic Cancellation, Polling Loop, Cloud Economics.
- **S (Situation)**: Provedores de workflows ComfyUI em nuvem cobram por segundo de máquina alocada, inclusive o tempo em que o container fica ocioso aguardando encerramento pelo usuário.
- **T (Task)**: Minimizar o custo financeiro operacional em execuções de centenas de takes.
- **A (Action)**: Desenvolvemos o padrão de **Cancelamento Atômico Pós-Download** no `runninghub_bot.py`. O bot dispara o workflow na nuvem, monitora o progresso via polling assíncrono e, no exato milissegundo em que o arquivo `.mp4` é baixado com sucesso e validado em disco, emite uma chamada REST cancelando atomicamente a instância do workflow.
- **R (Result)**: Redução drástica do custo por cena, eliminando 100% do tempo de GPU ociosa que ocorreria se dependêssemos do timeout padrão do provedor.

---

### 10. "Como vocês lidam com processos externos pesados como FFmpeg sem travar a aplicação?"
- **⏱️ Duração Alvo**: ~75 segundos
- **🔑 Buzzwords**: Subprocess Non-Blocking, Stream Piping, Returncode Validation, Zombie Process Prevention, Timeout Enforcement.
- **S (Situation)**: A montagem final de 40 cenas exige concatenar vídeos, aplicar filtros complexos de cor 3D LUT, mixar múltiplos canais de áudio e queimar legendas, operações que consom 100% de CPU/GPU por vários minutos.
- **T (Task)**: Executar essas rotinas pesadas garantindo que a aplicação não trave, não gere processos zumbis e forneça telemetria de progresso.
- **A (Action)**: No `src/video/ffmpeg_processor.py`, encapsulamos as chamadas via `subprocess.Popen` com leitura assíncrona de `stderr` linha a linha para extrair métricas de frames codificados e tempo restante. Definimos timeouts explícitos para impedir travamentos infinitos em caso de corrupção de codec. No caso de cancelamento da tarefa pelo usuário via dashboard, capturamos a árvore de processos pelo PID e enviamos sinal `SIGTERM` seguido de `SIGKILL` em cascata.
- **R (Result)**: Zero travamentos na interface do usuário, proteção total contra processos zumbis e auditoria detalhada de eventuais warnings do FFmpeg.

---

## 🧪 Bloco 4: Qualidade, Testes & Governança

### 11. "Qual é a sua estratégia de testes em um projeto tão acoplado a serviços externos e IA?"
- **⏱️ Duração Alvo**: ~80 segundos
- **🔑 Buzzwords**: Test Pyramid, Contract Mocking, Deterministic Fixtures, Pytest, Zero External Call in CI.
- **S (Situation)**: O projeto possui 314 testes automatizados, mas depende de APIs pagas de IA, automação web e encoders pesados de vídeo. Rodar chamadas reais na suíte de testes seria lento e proibitivamente caro.
- **T (Task)**: Construir uma suíte de testes determinística, rápida e que rode 100% offline.
- **A (Action)**: Estruturei a suíte com base no Pytest utilizando fixtures modulares e o padrão de mock em camadas. Para as APIs de IA (CosyVoice, MiniMax, OpenAI), mockamos os contratos HTTP usando respostas JSON estáticas pré-gravadas. Para o FFmpeg e Playwright, testamos a construção exata dos comandos e seletores sem disparar os binários pesados nos testes unitários. Para regras de negócio puras (validador de roteiro, roteamento de voz, cálculo de LUFS), testamos a lógica com dados determinísticos.
- **R (Result)**: Os 314 testes rodam em poucos segundos, garantindo validação contínua e zero risco de regressão antes de qualquer commit na branch principal.

---

### 12. "O que é o 'Hard Gate' do Story Validator e por que ele impede a geração do vídeo?"
- **⏱️ Duração Alvo**: ~75 segundos
- **🔑 Buzzwords**: Quality Gate, Shift-Left Quality, Rule Engine, Heuristic Scoring, Cost Prevention.
- **S (Situation)**: Gerar áudio e vídeo em modelos de ponta consome tempo e recursos financeiros. Se o roteiro tiver problemas de ritmo ou estrutura, o vídeo final terá baixa retenção de audiência no YouTube.
- **T (Task)**: Implementar uma validação de qualidade anterior ao consumo de recursos pesados (*shift-left*).
- **A (Action)**: Criamos o `story_validator.py`, um motor de regras que audita o roteiro com base em 27 livros canônicos de narrativa e audiovisual (Walter Murch, MrBeast, Lisa Cron). Ele calcula pontuações numéricas para ganchos de retenção nos primeiros 60 segundos, alternância de tensão dramática, ausência de silêncios mortos (*zero dead air*) e conflito interno. Se a pontuação global for inferior a 85/100, o validador levanta um erro fatal e bloqueia a execução do pipeline.
- **R (Result)**: Garantia de que apenas roteiros com narrativa de alta retenção cheguem à fase de renderização, evitando desperdício de GPU em conteúdos fracos.

---

### 13. "O que é a regra 'Zero-Zombie' e o Codebase Freshness Sentinel?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Technical Debt, Dead Code Elimination, AST Static Analysis, Facade Pattern, Single Source of Truth.
- **S (Situation)**: Em projetos que evoluem rapidamente com múltiplos agentes de IA, é comum que novos módulos sejam criados em `src/video/` enquanto o pipeline principal continua chamando versões legadas em `src/`, gerando código morto e divergência funcional.
- **T (Task)**: Prevenir proativamente a proliferação de código zumbi e garantir que novas implementações sejam conectadas à esteira.
- **A (Action)**: Instituímos a regra arquitetural 'Zero-Zombie' e criamos o script `scripts/audit_codebase_freshness.py`. Ele utiliza a biblioteca `ast` do Python para analisar estaticamente o grafo de chamadas de `run_pilot_pipeline.py`. Qualquer módulo novo que não seja referenciado direta ou indiretamente via padrão Facade é marcado como anomalia, bloqueando a suíte de validação até que seja integrado ou removido.
- **R (Result)**: Eliminação contínua de código órfão e garantia de que toda melhoria de engenharia beneficie imediatamente a linha de produção real.

---

### 14. "Como vocês resolveram o problema de encoding de caracteres entre Windows e Linux?"
- **⏱️ Duração Alvo**: ~65 segundos
- **🔑 Buzzwords**: Cross-Platform Portability, Windows cp1252, Defensive Initialization, Unicode Decode Error.
- **S (Situation)**: Em ambientes Windows, o Python frequentemente inicializa `sys.stdout` e `sys.stderr` utilizando o charset legado `cp1252` da Microsoft, enquanto sistemas Unix utilizam UTF-8 por padrão.
- **T (Task)**: Eliminar crashes de `UnicodeEncodeError` ao imprimir logs com acentos ou caracteres cirílicos da Guerra Fria.
- **A (Action)**: Formalizamos a decisão no **ADR-01**. Todo script Python do projeto obrigatoriamente inclui nas primeiras linhas uma rotina defensiva que verifica `if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')` e o mesmo para `stderr`. Além disso, toda operação de abertura de arquivos com `open()` passa explicitamente o parâmetro `encoding="utf-8"`.
- **R (Result)**: Execução 100% imune a problemas de encoding em qualquer sistema operacional, sem depender de variáveis de ambiente configuradas externamente pelo usuário.

---

## ⚖️ Bloco 5: Segurança, Negócios & Autocrítica

### 15. "Como vocês protegem o conteúdo de penalidades de direitos autorais e reivindicações de Content ID no YouTube?"
- **⏱️ Duração Alvo**: ~80 segundos
- **🔑 Buzzwords**: Fair Use, Public Domain Verification, Content ID Dispute Kit, Advertiser-Friendly Guidelines, EDSA.
- **S (Situation)**: Canais de história no YouTube frequentemente sofrem falsas reivindicações de copyright por gravadoras e distribuidores que registram acervos históricos públicos no Content ID.
- **T (Task)**: Blindar o canal de desmonetização e fornecer documentação jurídica automatizada para cada vídeo postado.
- **A (Action)**: Implementamos o `youtube_compliance_qc.py`. Ele audita duas frentes: conformidade editorial contra as diretrizes de anunciantes (Green Dollar 100/100) para evitar desmonetização por violência gráfica, e a geração de um **Legal Dispute Kit**. Para cada trilha e imagem utilizada, o sistema compila links de licença CC0 de domínio público e redige automaticamente um termo de contestação fundamentado nas diretrizes educacionais de Fair Use e EDSA.
- **R (Result)**: O documentário do piloto obteve score de conformidade 100/100 aprovado com kit de contestação pronto para submissão imediata em caso de reivindicação abusiva.

---

### 16. "Por que exportar para OpenTimelineIO (.otio) se o pipeline já gera o MP4 final?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Interoperability, Human-in-the-Loop, Non-Destructive Workflow, NLE Exchange, Industry Standard.
- **S (Situation)**: Embora a automação monte o vídeo completo, produções de alto orçamento para televisão ou streaming podem exigir pequenos ajustes manuais por um colorista ou editor humano.
- **T (Task)**: Permitir transição transparente entre a montagem automatizada por IA e ilhas de edição profissionais (Premiere, DaVinci Resolve, Final Cut).
- **A (Action)**: Implementamos o exportador universal no `src/video/otio_exporter.py` utilizando o padrão aberto OpenTimelineIO (desenvolvido pela Pixar e Academy Software Foundation). Em vez de entregar apenas o arquivo `.mp4` já achatado (*flattened*), exportamos a timeline completa com as 40 faixas de vídeo, stems de áudio e marcadores de transição preservados.
- **R (Result)**: Qualquer editor profissional pode abrir o projeto gerado pela IA no DaVinci Resolve com um clique para refinamento fino, eliminando o aprisionamento da ferramenta.

---

### 17. "Como você escalaria esse sistema de 1 vídeo por dia para 1.000 vídeos por dia?"
- **⏱️ Duração Alvo**: ~85 segundos
- **🔑 Buzzwords**: Horizontal Scalability, Decoupled Workers, Celery/Temporal, Object Storage, Containerized Nodes.
- **S (Situation)**: O pipeline atual é otimizado para um operador executando renderizações sequenciais em uma única máquina workstation.
- **T (Task)**: Desenhar a arquitetura de escala industrial para atender um catálogo massivo de canais dark multibilíngues.
- **A (Action)**: Para escalar 1.000x, quebraríamos o orquestrador monolítico em microsserviços orientados a eventos. Substituiríamos o `subprocess.run()` local por um orquestrador de workflows resilientes como **Temporal.io** ou **Celery com RabbitMQ**. Cada etapa da esteira (pesquisa, roteiro, voz, vídeo, composição FFmpeg) seria um worker desacoplado rodando em containers Docker no Kubernetes, com autoscaling baseado na profundidade das filas. A persistência de arquivos locais migraria para um storage distribuído compatível com S3 (como MinIO ou AWS S3) e os metadados seriam persistidos em PostgreSQL com réplicas de leitura.
- **R (Result)**: Paralelização massiva onde 100 vídeos podem ter suas narrações sintetizadas enquanto outros 100 estão na fila de renderização de GPU, com tolerância total a falhas por nó.

---

### 18. "Como vocês evitam alucinações históricas em um sistema que usa LLMs para roteirizar?"
- **⏱️ Duração Alvo**: ~75 segundos
- **🔑 Buzzwords**: Retrieval-Augmented Generation (RAG), Grounding, Declassified Archive Ingestion, Hallucination Prevention.
- **S (Situation)**: Modelos de linguagem generativos possuem tendência natural a inventar detalhes para preencher lacunas narrativas, o que destruiria a credibilidade de um documentário histórico sério.
- **T (Task)**: Garantir fidelidade histórica absoluta dos eventos narrados.
- **A (Action)**: Adotamos uma estratégia rigorosa de *grounding*: o LLM do showrunner (`nolan_director.py`) não tem liberdade para inventar cronologias. Ele recebe obrigatoriamente como contexto de entrada o dossiê minerado na Fase 1 (`research_engine.py` e `public_domain_research.py`), extraído de relatórios militares desclassificados e arquivos de domínio público. O validador de fatos cruza as entidades (nomes de generais, horários exatos, códigos de silos de mísseis) com o dossiê base; se houver discrepância temporal ou nominal, a cena é rejeitada.
- **R (Result)**: Documentários com precisão factual auditável e narrativa envolvente sem invenção de fatos históricos.

---

### 19. "Como vocês garantem segurança e gerenciamento de credenciais em um ambiente com dezenas de APIs?"
- **⏱️ Duração Alvo**: ~70 segundos
- **🔑 Buzzwords**: Least Privilege, Environment Secrets, Session Storage Isolation, Defense in Depth, Zero Hardcoded Secrets.
- **S (Situation)**: A esteira necessita de tokens para YouTube API, RunningHub, Google Cloud, além de cookies de sessão de browsers.
- **T (Task)**: Prevenir vazamento acidental de chaves em repositórios Git ou logs do dashboard.
- **A (Action)**: Implementamos três camadas de proteção: primeiro, política estrita de zero hardcoded credentials, onde todas as chaves são carregadas via variáveis de ambiente com `python-dotenv` a partir de `.env` ignorado no `.gitignore`. Segundo, máscaras de log no dashboard: qualquer saída de terminal ou log que contenha padrões de bearer tokens ou api keys tem seus caracteres ofuscados antes de serem gravados ou transmitidos via SSE. Terceiro, o `auth_gate.py` isola perfis de sessão em diretórios locais com permissões restritas.
- **R (Result)**: Zero incidentes de segurança ou chaves expostas nos commits do repositório, garantindo conformidade com padrões de auditoria.

---

### 20. "Se você fizesse esse projeto do zero hoje, o que faria de diferente?"
- **⏱️ Duração Alvo**: ~85 segundos
- **🔑 Buzzwords**: Architectural Retrospective, Pragmatism vs Purity, Contract-First Testing, Message Broker, Production Maturity.
- **S (Situation)**: O DarkFactory foi construído de forma pragmática e ágil para provar o conceito de ponta a ponta com máxima velocidade e orçamento controlado.
- **T (Task)**: Demonstrar maturidade técnica de nível sênior identificando pontos de evolução arquitetural.
- **A (Action)**: Se começasse do zero hoje com os aprendizados atuais, mudaria quatro decisões principais:
  1. *Fila de Mensagens*: Adotaria uma fila assíncrona leve (Redis + RQ ou Celery) desde o primeiro dia, em vez de depender de chamadas sequenciais de subprocessos no orquestrador.
  2. *Armazenamento de Metadados*: Usaria SQLite estruturado com WAL (Write-Ahead Logging) em vez de dezenas de arquivos JSON avulsos, facilitando consultas de telemetria complexas sem perder a simplicidade de zero infraestrutura externa.
  3. *APIs de Vídeo em vez de Browser*: Aguardaria ou priorizaria APIs REST oficiais para geração de vídeo, reduzindo a manutenção de seletores de DOM e camuflagem no Playwright.
  4. *Testes de Contrato*: Implementaria testes de contrato (como Pact) entre a esteira e os schemas do dashboard desde o sprint inicial.
- **R (Result)**: Ter consciência dessas escolhas demonstra que a arquitetura atual foi uma decisão pragmática e consciente para a fase de MVP e validação de produto, com um roadmap técnico claro de refatoração para escalabilidade futura.
