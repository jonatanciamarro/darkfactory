# 🌐 Glossário Técnico Bilíngue (PT-BR ↔ EN) para Entrevistas Técnicas

> **Dicionário Técnico Fonético & Contextual de Engenharia, Áudio Broadcast, IA e Cinema**
> Criado para eliminar hesitações de vocabulário e garantir pronúncia correta de termos internacionais perante bancas avaliadoras de empresas globais.

---

## 🏛️ 1. Arquitetura de Software & Engenharia de Sistemas

| Termo em Português | English Term | Pronúncia (IPA + Guia Fonético) | Contexto no DarkFactory | Dica para Entrevistas |
|:---|:---|:---|:---|:---|
| **Esteira de Produção** | **Pipeline** | `/ˈpaɪp.laɪn/` *(paip-lain)* | `run_pilot_pipeline.py` orquestra os 11 passos sequenciais. | Em entrevistas em inglês, nunca diga *"production mat"*; use sempre *"data/media pipeline"*. |
| **Plano de Contingência** | **Fallback** | `/ˈfɔːl.bæk/` *(fól-bék)* | Transição de CosyVoice → Kokoro-82M → Edge-TTS no `voice_router.py`. | Fale de *"fallback strategy"* ou *"graceful degradation"* para soar sênior. |
| **Fila de Mensagens Mortas** | **Dead Letter Queue (DLQ)** | `/dɛd ˈlɛt.ər kjuː/` *(déd léter quiú)* | Diretório `data/quarantine/` para takes de vídeo rejeitados pelo QA. | Explique que aplicou o conceito de DLQ de mensageria para artefatos de arquivos físicos. |
| **Idempotência** | **Idempotency** | `/ˌaɪ.dɛmˈpoʊ.tən.si/` *(ai-dem-pôuten-si)* | Executar novamente o passo de áudio com o mesmo script não gasta GPU se o arquivo já existir. | *"An idempotent operation can be applied multiple times without changing the result beyond the initial run."* |
| **Orquestrador** | **Orchestrator** | `/ˈɔːr.kɪ.streɪ.tər/` *(ór-kestrei-tor)* | Padrão arquitetural central em `run_pilot_pipeline.py`. | Não confunda com *Choreography*. O Orchestrator centraliza a decisão de controle do fluxo. |
| **Inversão de Dependência** | **Dependency Inversion** | `/dɪˈpɛn.dən.si ɪnˈvɜːr.ʒən/` *(di-pên-dên-si in-vêr-jan)* | O `voice_router.py` depende de abstrações de motor, e não das bibliotecas concretas. | É a letra **D** do SOLID: módulos de alto nível não devem depender de módulos de baixo nível. |
| **Degradação Graciosa** | **Graceful Degradation** | `/ˈɡreɪs.fəl ˌdɛɡ.rəˈdeɪ.ʃən/` *(greis-ful dégra-dei-shan)* | Quando a GPU remota cai, o áudio continua rodando via CPU local mais lento, mas sem crash. | Mostra que seu sistema foi desenhado para tolerar falhas parciais em produção. |
| **Disjuntor / Fusível** | **Circuit Breaker** | `/ˈsɜːr.kɪt ˈbreɪ.kər/` *(sêr-kit brei-ker)* | Interrompe requisições para provedores em nuvem após 3 timeouts consecutivos. | Evita esgotar threads e recursos locais tentando alcançar um serviço que está comprovadamente fora do ar. |
| **Verificação Prévia** | **Pre-flight Check** | `/ˌpriːˈflaɪt tʃɛk/` *(pri-flait tchék)* | `auth_gate.py` valida credenciais e cookies antes de disparar o pipeline pesado. | Destaque como economia de custos: checar requisitos antes de alocar instâncias caras de GPU. |
| **Contrato de Dados** | **Data Contract / Schema** | `/ˈskiː.mə/` *(skí-ma)* | Schemas Pydantic v2 em `src/dashboard/schemas.py`. | Use *"schema enforcement"* ao defender a tipagem entre o frontend e a API. |
| **Exceção Silenciosa** | **Silent Failure** | `/ˈsaɪ.lənt ˈfeɪl.jər/` *(sai-lent fei-liur)* | Anti-pattern eliminado no `auth_gate.py` onde `except: pass` escondia erros. | Fale sobre seu compromisso com o princípio *Fail-Fast* e observabilidade de erros. |
| **Isolamento de Processo** | **Process Isolation** | /ˈprɑː.sɛs ˌaɪ.səˈleɪ.ʃən/ *(pró-cess ai-so-lei-shan)* | Cada etapa da esteira roda em um processo independente do Python. | Argumente que isso dá *crash safety* contra segfaults em bibliotecas nativas de C. |
| **Gerenciamento de Ciclo de Vida** | **Lifespan Context Manager** | `/ˈlaɪf.spæn ˈkɑːn.tɛkst/` *(laif-spén con-tekst)* | `@asynccontextmanager async def lifespan` no `src/dashboard/app.py`. | Relacione com o padrão RAII do C++ (*Resource Acquisition Is Initialization*). |

---

## 🎧 2. Engenharia de Áudio & Broadcast

| Termo em Português | English Term | Pronúncia (IPA + Guia Fonético) | Contexto no DarkFactory | Dica para Entrevistas |
|:---|:---|:---|:---|:---|
| **Intensidade Sonora Percebida** | **Loudness** | `/ˈlaʊd.nəs/` *(laud-ness)* | Normalização acústica global em `src/audio_mixer_master.py`. | Diferencie volume de pico (dBFS) de loudness integrado (LUFS). |
| **Unidades de Loudness** | **LUFS / LKFS** | `/lʌfs/` *(lâfs)* | Norma EBU R128 calibrada em exatos **-14.0 LUFS (±0.5)** para o YouTube. | LUFS significa *Loudness Units relative to Full Scale*, padrão broadcast de áudio digital. |
| **Pico Verdadeiro Inter-Amostras** | **True Peak (dBTP)** | `/truː piːk/` *(tru pik)* | Teto configurado em **-1.0 dBTP** no limiter do FFmpeg. | Explique que -1.0 dBTP previne distorção harmônica quando codecs lossy (AAC/Opus) reconstroem a onda. |
| **Atenuação Dinâmica por Cadeia Lateral** | **Dynamic Ducking / Sidechain** | /ˈdaɪ.næk ˈdʌk.ɪŋ/ *(dai-né-mik dâ-king)* | A trilha sonora abaixa -16 dB automaticamente quando a narração vocal entra. | Demonstre que isso substitui automações manuais de volume na ilha de edição. |
| **Faixas / Canais Isolados de Áudio** | **Stems** | `/stɛmz/` *(stémz)* | O mixer combina 4 stems: voz limpa, trilha musical, efeitos foley e sub-bass braams. | Em produção de mídia profissional, nunca use "tracks" ou "files"; chame sempre de *"audio stems"*. |
| **Efeitos Sonoros Realistas** | **Foley** | `/ˈfoʊ.li/` *(fôu-li)* | Biblioteca de passos, estalos de relógio e sirenes sincronizados no `foley_library.py`. | O termo homenageia Jack Foley, pioneiro em criar ruídos físicos sincronizados para cinema. |
| **Alinhamento Forçado** | **Forced Alignment** | `/fɔːrst əˈlaɪn.mənt/` *(fórst a-lain-ment)* | `src/video/voice_aligner.py` correlaciona o texto fonético ao áudio para gerar SRTs. | Explique como a transcrição fonética mapeia milissegundos precisos para legendas cinéticas. |
| **Estiramento Temporal sem Troca de Tom** | **Time-Stretch / Pitch Warp** | `/taɪm strɛtʃ/` *(taim strétch)* | Ajuste de velocidade do áudio para sincronizar com a duração exata do take visual. | Mencione que algoritmos como Complex Pro preservam o timbre do narrador sem efeito "esquilo". |

---

## 🎬 3. Cinema, Vídeo & Técnicas Nolan

| Termo em Português | English Term | Pronúncia (IPA + Guia Fonético) | Contexto no DarkFactory | Dica para Entrevistas |
|:---|:---|:---|:---|:---|
| **Barras Pretas Teatrais** | **Letterbox** | /ˈlɛt.ər.bɑːks/ *(léter-bóks)* | Proporção 2.39:1 Anamorphic Cinema Scope aplicada em vídeos 1080p. | Dá ar teatral e fornece área limpa de alto contraste para queima de legendas. |
| **Tabela de Consulta de Cor 3D** | **3D LUT (Look-Up Table)** | `/lʌt/` *(lât)* | Emulação da película analógica `Kodak 2383 Bleach-Bypass` no `cinematic_color.py`. | Um mapa tridimensional que recalcula valores de RGB para simular a resposta de emulsões químicas de filme. |
| **Dobradinha de Tomadas** | **Dual-Shot Formulation** | /ˈduː.əl ʃɑːt/ *(dú-al shót)* | Cada cena combina Shot A (Drama Humano) + Shot B (Macro Tático). | Argumente que essa técnica evita o vício de planos genéricos em geradores generativos. |
| **Fluxo Óptico** | **Optical Flow** | /ˈɑːp.tɪ.kəl floʊ/ *(óp-ti-col flôu)* | OpenCV analisa vetores de movimento entre frames para detecção de glitches no QA. | Usado no controle de qualidade automatizado para quarentenar takes com deformações anatômicas. |
| **Guia do Olhar** | **Eye-Trace** | `/aɪ treɪs/` *(ai treis)* | Regra de Walter Murch em `story_validator.py` mantendo o ponto de foco visual coerente entre cortes. | Demonstra erudição cinematográfica combinada com engenharia computacional. |
| **Intercalação Temporal** | **Crosscutting / Interleaving** | /ˈkrɔːsˌkʌt.ɪŋ/ *(cróss-câ-ting)* | Técnica de Christopher Nolan onde 3 linhas de tempo avançam em paralelo. | Base da estrutura dos roteiros em 5 Atos no `nolan_multi_act.py`. |
| **Padrão Aberto de Linha do Tempo** | **OpenTimelineIO (.otio)** | `/ˌoʊ.pən ˈtaɪm.laɪn aɪ.oʊ/` | `otio_exporter.py` gera timelines intercambiáveis para DaVinci Resolve e Premiere. | Ressalte o respeito ao fluxo de trabalho profissional e a interoperabilidade de ferramentas. |
| **Intervalo de Curiosidade** | **Curiosity Gap** | /ˌkjʊr.iˈɑː.sə.ti ɡæp/ *(quiuri-ó-ssiti gép)* | Métrica de retenção inspirada em Lisa Cron para prender o espectador no roteiro. | O roteiro abre perguntas intrigantes e retarda deliberadamente a resposta para maximizar watch time. |

---

## 🤖 4. Inteligência Artificial, Nuvem & Automação

| Termo em Português | English Term | Pronúncia (IPA + Guia Fonético) | Contexto no DarkFactory | Dica para Entrevistas |
|:---|:---|:---|:---|:---|
| **Texto para Vídeo** | **Text-to-Video (T2V)** | `/tɛkst tuː ˈvɪd.i.oʊ/` | Geração de cenas no Wan 2.2, MiniMax H3 e Google Flow Veo 3.1. | Refira-se à categoria como *"generative T2V models"*. |
| **Texto para Fala** | **Text-to-Speech (TTS)** | `/tɛkst tuː spiːtʃ/` | Síntese de narração via CosyVoice 3 e Kokoro-82M. | Destaque a diferença entre modelos determinísticos de concatenativos e redes neurais baseadas em difusão. |
| **Ambiente de Execução ONNX** | **ONNX Runtime** | /ˈɑː.nɪks ˈrʌn.taɪm/ *(óniks ran-taim)* | Inferência de CPU de alta performance para o modelo Kokoro local. | ONNX (*Open Neural Network Exchange*) garante portabilidade de modelos entre PyTorch e C++. |
| **Quantização de Modelos** | **Quantization** | /ˌkwɑːn.təˈzeɪ.ʃən/ *(quan-ti-zei-shan)* | Uso de pesos em 8 bits (int8) para executar modelos neurais na CPU sem GPU. | Reduz footprint de memória e acelera inferência com perda imperceptível de qualidade de áudio. |
| **Ancoragem Factual** | **Grounding** | /ˈɡraʊn.dɪŋ/ *(graun-ding)* | Alimentar o showrunner com fatos de dossiês desclassificados para impedir alucinações. | Use *"hallucination mitigation through factual grounding"* para impressionar entrevistadores. |
| **Perfil Furtivo de Navegador** | **Stealth Profile** | `/stɛlθ ˈproʊ.faɪl/` *(stélth prôu-fail)* | `src/factory/stealth_profile.py` camuflando o Playwright contra detecção antibot. | Explique as técnicas de mascaramento de variáveis de automação em `navigator.webdriver`. |
| **Automação Robótica de Processos** | **RPA (Robotic Process Automation)** | /ˌɑːr.piːˈeɪ/ *(ar-pi-ei)* | Bots autônomos que operam ferramentas de IA sem APIs abertas. | Defenda o RPA como acelerador pragmático de negócios para ferramentas de ponta. |
| **Economia de Recursos em Nuvem** | **Cloud Cost Governance** | /klaʊd kɔːst ˈɡʌv.ər.nəns/ | Cancelamento atômico de jobs no RunningHub para poupar segundos ociosos de GPU. | Mostra maturidade financeira (*FinOps*) além de habilidade técnica pura. |
