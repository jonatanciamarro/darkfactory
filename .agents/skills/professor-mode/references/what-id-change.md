# 🔄 O Que Eu Faria Diferente — Autocrítica Arquitetural

> **Análise Retrospectiva Sênior: Trade-offs Conscientes, Dívidas Técnicas Aceitas e Roadmap de Evolução**
> Esta seção foi concebida para responder à clássica pergunta de bancas técnicas e Staff Engineers: *"Se você pudesse começar este projeto do zero hoje com os aprendizados que tem, o que você faria de diferente?"*

---

## 1. De Pipeline Sequencial em Subprocessos para Orquestração de Filas (Celery / RabbitMQ / Temporal)

### O Que É Hoje
O `run_pilot_pipeline.py` orquestra as 11 etapas da esteira de forma sequencial utilizando chamadas síncronas com `subprocess.run()`. O script espera a conclusão do Step 3 (renderização de takes) para poder iniciar o Step 4 (áudio), e assim sucessivamente.

### Limitações da Abordagem Atual
- **Bloqueio em Linha de Produção**: Se a renderização de takes de vídeo demorar 40 minutos devido a filas de provedores de GPU externos, toda a esteira fica parada, mesmo que o Step 4 (síntese de voz) e o Step 5 (geração de legendas) pudessem ser executados em paralelo.
- **Dificuldade de Retentativa Granular**: Se o Step 7 falhar no minuto final, reexecutar a esteira inteira exige flags manuais ou lógica imperativa complexa de verificação de arquivos pré-existentes.
- **Gargalo Monomáquina**: Todo o processamento fica restrito aos núcleos de CPU e GPU de uma única estação de trabalho.

### A Arquitetura Proposta (Escala Industrial)
- Substituir o orquestrador síncrono por um motor de workflows duráveis como **Temporal.io** ou **Celery com RabbitMQ**.
- Cada uma das 11 etapas torna-se uma *Task* isolada e assíncrona com idempotência garantida e política de retry exponencial configurável.
- As etapas independentes (ex.: síntese de narração, download de foley e geração de mapas vetoriais táticos) rodam concorrentemente em workers distribuídos assim que o roteiro da Fase 2 é aprovado.

### Por Que Não Foi Feito Assim no Início? (Defesa Pragmática)
Para o escopo de um operador inicial validando a estética documental e a qualidade de retenção do modelo piloto, adicionar RabbitMQ, Redis e Celery traria um custo operacional desproporcional. Subprocessos locais permitiram iterar rápido, depurar com facilidade via terminal e manter a barreira de entrada da infraestrutura em zero.

### Gatilho de Migração
Quando o volume de produção ultrapassar 3 documentários por dia ou quando a esteira for operada por múltiplos editores em paralelo.

### 🎓 Script de Resposta em Entrevista (60s)
> *"Se eu estivesse desenhando o DarkFactory para escala de estúdio hoje, a primeira mudança seria migrar o orquestrador monolítico de subprocessos para uma arquitetura orientada a eventos com Temporal.io ou Celery. Hoje, as etapas rodam em cascata síncrona; em uma esteira distribuída, o áudio e os gráficos de mapa seriam processados em paralelo com a renderização de vídeo por nós dedicados. Optei por subprocessos inicialmente porque a prioridade era validar a qualidade artística e a retenção do algoritmo sem o overhead de gerenciar brokers de mensageria para um único operador."*

---

## 2. De Estado Baseado em Arquivos JSON para Banco Estruturado (SQLite com WAL / PostgreSQL)

### O Que É Hoje
Todas as entidades do sistema (dossiês de pesquisa, roteiros em 5 Atos, manifests de cena, telemetria de áudio e pacotes de metadados do YouTube) são gravadas como arquivos `.json` individuais espalhados pelos diretórios `data/scripts/` e `data/processed/`.

### Limitações da Abordagem Atual
- **Ausência de Transações ACID Multientidade**: Se o script gravar o áudio mas cair antes de persistir o manifest correspondente, os arquivos em disco podem ficar descasados sem rollback automático.
- **Consultas Analíticas Ineficientes**: Para descobrir qual foi o arquétipo narrativo com melhor retenção histórica ou calcular o custo médio de GPU por minuto de vídeo, é necessário abrir e deserializar dezenas de arquivos JSON via script avulso.
- **Concorrência Limitada de Escrita**: Múltiplos processos escrevendo no mesmo diretório correm risco de conflitos de I/O em arquivos compartilhados.

### A Arquitetura Proposta (Escala Industrial)
- Adotar **SQLite com modo WAL (Write-Ahead Logging)** para execuções locais ou **PostgreSQL** para ambiente corporativo multiusuário.
- Manter o armazenamento de binários pesados (`.mp4`, `.wav`, `.png`) no sistema de arquivos ou storage S3, salvando apenas metadados, timestamps, scores de auditoria e status de tarefas nas tabelas relacionais.

### Por Que Não Foi Feito Assim no Início? (Defesa Pragmática)
Arquivos JSON permitiram inspeção visual imediata com VS Code e ferramentas de terminal sem necessidade de clients de banco de dados. Para a fase de prototipação de prompts e engenharia de áudio, a flexibilidade de alterar campos no JSON sem precisar criar migrações de esquema foi um acelerador essencial de desenvolvimento.

### Gatilho de Migração
No momento em que o Cinema Dashboard precisar suportar múltiplos usuários simultâneos, filtros de busca históricos complexos ou auditoria de analytics agregados.

### 🎓 Script de Resposta em Entrevista (60s)
> *"Para persistência de metadados, optei por arquivos JSON pelo pragmatismo: são inspecionáveis a olho nu, portáveis e dispensam migrations enquanto os esquemas de IA ainda estão se estabilizando. No entanto, para um ambiente corporativo, migraria imediatamente para SQLite com WAL ou Postgres. Isso nos daria transações atômicas entre os passos do pipeline, integridade referencial entre cenas e áudios, e a capacidade de rodar queries analíticas para correlacionar parâmetros de prompt com retenção real de audiência."*

---

## 3. De Automação Web via Browser (Playwright) para Integração Direta com APIs REST Oficiais

### O Que É Hoje
O módulo `src/google_flow_bot.py` utiliza Playwright com perfil furtivo (*stealth*) para interagir com a interface web do Google Flow, emulando cliques e downloads para gerar takes com os modelos Veo 3.1 e Omni Flash.

### Limitações da Abordagem Atual
- **Fragilidade a Mudanças de DOM**: Qualquer atualização na interface web do Google (alteração de classes CSS, novos botões ou mudanças no fluxo de navegação) quebra os seletores do bot até que uma manutenção manual seja realizada.
- **Consumo de Memória do Navegador**: Instâncias do Chromium headless consomem gigabytes de memória RAM e ciclos de CPU desnecessários apenas para renderizar elementos visuais.
- **Risco de Bloqueios Antibot**: Plataformas web podem atualizar seus algoritmos de detecção de automação a qualquer momento, exigindo constantes ajustes no módulo de camuflagem.

### A Arquitetura Proposta (Escala Industrial)
- Substituir o scraping do browser por integrações diretas via APIs REST oficiais (Google Vertex AI / Gemini Video API ou provedores de GPU dedicada como RunPod/Replicate).
- Isolar as requisições em clientes HTTP padronizados baseados em `httpx` assíncrono com pool de conexões persistentes.

### Por Que Não Foi Feito Assim no Início? (Defesa Pragmática)
Os modelos de geração de vídeo mais avançados da indústria frequentemente são disponibilizados primeiro em interfaces experimentais para o público antes de receberem endpoints de API para desenvolvedores. O uso pragmático de RPA permitiu que o DarkFactory operasse com tecnologias visuais de ponta meses antes de seus concorrentes poderem acessá-las via API formal.

### Gatilho de Migração
Disponibilização pública de endpoints REST oficiais de alta velocidade com precificação por token ou segundo de renderização.

### 🎓 Script de Resposta em Entrevista (60s)
> *"Usar automação de browser via Playwright para geração de vídeo foi uma decisão consciente de time-to-market. Modelos visuais revolucionários como o Veo 3.1 foram lançados em plataformas web antes de abrirem APIs públicas de larga escala. O trade-off foi aceitar a fragilidade da manutenção de seletores em troca da superioridade estética imediata dos vídeos. Hoje, com a maturação dos endpoints de API, o caminho natural é migrar 100% para chamadas HTTP diretas com SDKs oficiais, eliminando o overhead de browsers headless."*

---

## 4. De Testes com Mocks Pesados para Testes de Contrato e Testcontainers

### O Que É Hoje
A suíte com 314 testes do Pytest é extremamente rápida e determinística porque utiliza mocks e monkeypatching intensivos para simular chamadas de rede, respostas de IA e comandos do FFmpeg.

### Limitações da Abordagem Atual
- **Risco de Drift de Mocks**: Se a API externa do RunningHub ou MiniMax mudar sutilmente a estrutura do payload retornado, a suíte de testes continuará passando com sucesso (*green false-positive*) porque os mocks continuam retornando a estrutura antiga.
- **Não Validação de Binários Reais**: Mocks do FFmpeg testam a concatenação de strings da linha de comando, mas não garantem que a versão instalada do FFmpeg no sistema operacional suporta os filtros específicos exigidos.

### A Arquitetura Proposta (Escala Industrial)
- Introduzir **Contract Testing (Pact)** para validar se os mocks refletem formalmente os contratos das APIs dos fornecedores.
- Adotar **Testcontainers** para subir containers Docker efêmeros com o FFmpeg real e modelos locais em testes de integração executados em pipelines de CI/CD.

### Por Que Não Foi Feito Assim no Início? (Defesa Pragmática)
Testes baseados em containers e requisições reais aumentam o tempo de execução da suíte de segundos para vários minutos, desestimulando a prática constante de TDD durante o ciclo de desenvolvimento rápido.

### Gatilho de Migração
No momento da implantação de uma esteira formal de CI/CD em nuvem com múltiplos desenvolvedores realizando pull requests concorrentes.

---

## 5. De Monorepo com Imports Relativos para Pacotes Modulares Versionados

### O Que É Hoje
Toda a base de código reside sob o diretório `src/` com imports relativos ou globais baseados no `sys.path`.

### Limitações da Abordagem Atual
- **Acoplamento Implícito**: É fácil para um módulo de vídeo importar acidentalmente funções internas de áudio ou do dashboard sem passar por uma interface pública bem definida.
- **Dificuldade de Compartilhamento**: Se outro projeto precisar apenas do motor de normalização de áudio EBU R128 (`audio_mixer_master.py`), é necessário copiar o arquivo em vez de instalá-lo como dependência limpa.

### A Arquitetura Proposta (Escala Industrial)
- Quebrar o monorepo em pacotes Python independentes gerenciados via Poetry/Hatch (`darkfactory-core`, `darkfactory-audio`, `darkfactory-video`, `darkfactory-dashboard`), cada um com seu próprio `pyproject.toml` e semver.
- Utilizar Python Workspace para desenvolvimento local integrado.

### Por Que Não Foi Feito Assim no Início? (Defesa Pragmática)
Manter pacotes versionados para um projeto desenvolvido por um desenvolvedor/operador introduz burocracia desnecessária de releases locais e atualizações de dependências cruzadas em fases onde o código muda diariamente.
