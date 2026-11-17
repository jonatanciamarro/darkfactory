# 📖 DarkFactory Learning Journal

> **Registro de Conhecimento Técnico & Mentorias Auditáveis**  
> Documentação viva das decisões arquiteturais, padrões de design, lições de produção e resiliência do projeto **DarkFactory**, estruturada especificamente para preparação e defesa em **Entrevistas Técnicas Sênior / Staff**.

---

## 🎯 Por Que Organização por TEMA e Não por Data?

Em ambientes profissionais de engenharia e na preparação para processos seletivos, **ninguém estuda decisões técnicas em ordem cronológica**. 

Quando um entrevistador questiona:
- *"Como você lida com degradação graciosa em APIs externas?"*
- *"Por que optou por orquestração monolítica com isolamento de processos em vez de microserviços?"*
- *"Como estruturou contratos de dados e prevenção de silent failures?"*

Você precisa localizar instantaneamente o conhecimento acumulado por **assunto e padrão técnico**, e não caçar em um diário por "o que foi feito em 14 de novembro".

---

## 🧭 Estrutura Temática de Diretórios

O repositório de conhecimento é dividido em **6 diretórios temáticos**, alinhados aos 5 pilares do `professor-mode`:

| Diretório Temático | Foco & Domínio Técnico | Exemplos de Tópicos no DarkFactory |
| :--- | :--- | :--- |
| [📁 `architecture/`](architecture/) | Decisões estruturais de alto nível, orquestração, monólito vs microserviços, isolamento de processos. | Subprocess vs Threading, Orchestrator Pattern no pipeline (`run_pilot_pipeline.py`), FastAPI Lifespan. |
| [📁 `patterns/`](patterns/) | Design patterns clássicos (GoF) e modernos, princípios SOLID, Clean Code e tipagem. | Strategy & Invariant em `voice_router.py`, Chain of Responsibility em `kokoro_fallback.py`, Abstract Factory em `darkfactory_t2v.py`. |
| [📁 `errors/`](errors/) | Gestão de falhas, resiliência, eliminação de silent failures, circuitos de fallback e idempotência. | Eliminação de bare `except: pass` no `auth_gate.py`, validação estrita de exit code no FFmpeg. |
| [📁 `security/`](security/) | Autenticação, gestão de credenciais (.env), pre-flight checks, contratos de dados com Pydantic. | Pre-flight Auth Gate, sanitização de inputs de prompt, prevenção de vazamento de chaves de API. |
| [📁 `data/`](data/) | Persistência, integridade de arquivos, encoding defensivo e formatos de serialização. | ADR-01 UTF-8 no Windows, JSON-based storage vs SQLite, transações atômicas de escrita. |
| [📁 `infra/`](infra/) | Engenharia de áudio/vídeo, tuning de FFmpeg, economia de GPU e automação RPA. | ADR-02 Normalização -14 LUFS (EBU R128), otimização de cotas no RunningHub via cancelamento pós-download. |

---

## 📝 Como Adicionar uma Nova Entrada ao Journal

1. Identifique o tema predominante da decisão técnica (`architecture`, `patterns`, `errors`, `security`, `data` ou `infra`).
2. Copie o template oficial disponível em:  
   [journal-entry-template.md](file:///e:/projcts/darkfactory/.agents/skills/professor-mode/resources/journal-entry-template.md)
3. Crie um novo arquivo no respectivo diretório com o padrão de nomenclatura:  
   `docs/learning-journal/<tema>/<id>-<slug-da-decisao>.md`  
   *(Exemplo: `docs/learning-journal/errors/001-eliminacao-silent-failures-auth-gate.md`)*
4. Preencha todos os campos, dando ênfase especial ao roteiro de resposta rápida **STAR (Situation, Task, Action, Result)**.
5. Adicione a referência ao novo arquivo na tabela do tema correspondente abaixo.

---

## 📚 Índice de Entradas Registradas

### 🏗️ Arquitetura (`architecture/`)
- *Aguardando registro de novas mentorias via `/professor`.*

### 📐 Design Patterns (`patterns/`)
- *Aguardando registro de novas mentorias via `/professor`.*

### 🐛 Erros & Resiliência (`errors/`)
- *Aguardando registro de novas mentorias via `/professor`.*

### 🔐 Segurança & Contratos (`security/`)
- *Aguardando registro de novas mentorias via `/professor`.*

### 💾 Dados & Formatos (`data/`)
- *Aguardando registro de novas mentorias via `/professor`.*

### ⚡ Infra & Performance (`infra/`)
- *Aguardando registro de novas mentorias via `/professor`.*

---

## 🎓 Como Estudar Este Journal Para Entrevistas Técnicas

1. **Simule a Pergunta**: Leia apenas a seção *"Pergunta Provável do Entrevistador"* e tente responder em voz alta em até 90 segundos.
2. **Confira os Trade-offs**: Entrevistadores experientes sempre desafiam sua primeira resposta ("Mas e se o tráfego aumentar 100x?"). Consulte a seção de *Trade-offs e Ponto de Inflexão*.
3. **Use o Vocabulário Certo**: Revise a tabela bilíngue da entrada para garantir fluência nos termos em inglês mais comuns em sabatinas internacionais.
