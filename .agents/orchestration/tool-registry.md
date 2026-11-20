# Registro de Ferramentas e CLI (`tool-registry.md`)

> **Catálogo de Ferramentas Nativas, CLI e Automações**  
> *Mapeamento detalhado das ferramentas disponíveis no ecossistema Antigravity e no projeto `corporate-engineer`.*

---

## 1. Ferramentas Nativas da Plataforma Antigravity

| Ferramenta | Categoria | Finalidade | Cuidados / Diretrizes |
|---|---|---|---|
| `read_file` | Sistema de Arquivos | Leitura de arquivos (código, markdown, logs, imagens, pdfs). | Respeita limite de 800 linhas / 46KB por leitura; use `ByteOffset`/`StartLine`. |
| `write_file` | Sistema de Arquivos | Criação ou sobrescrita atômica de arquivos no workspace ou artefatos. | Obrigatório `ArtifactMetadata` apenas ao gerar artefatos em `<appDataDir>\brain`. |
| `edit_file` | Sistema de Arquivos | Edição cirúrgica pontual de blocos de texto por substituição exata. | O alvo (`Target`) deve ser idêntico (incluindo espaços e quebras de linha). |
| `run_command` | Shell Execution | Execução de comandos PowerShell no ambiente Windows do workspace. | Comandos que excedem `WaitMsBeforeAsync` viram tarefas em background. |
| `invoke_subagent` | Multi-Agente | Inicialização de subagentes especialistas com prompts e papéis isolados. | Sistema notifica reativamente no retorno — sem necessidade de polling. |
| `define_subagent` | Multi-Agente | Criação dinâmica de novos tipos de subagentes para o escopo da sessão. | Use quando uma especialização nova for requerida para múltiplas tarefas. |
| `manage_subagents`| Multi-Agente | Listagem e finalização (`kill`) de subagentes da sessão. | Usar com parcimônia para desalocar recursos. |
| `send_message` | Multi-Agente | Canal de comunicação estruturado entre agentes (NUNCA com o usuário). | O usuário recebe output textual padrão, não `send_message`. |
| `run_workflow` | Orquestração | Execução de scripts Python de automação e fanning out de agentes. | Use para pipelines complexos baseados em código. |
| `schedule` | Automação | Agendamento de timers pontuais ou rotinas cron em background. | Notificação reativa por prompt quando o timer dispara. |
| `manage_task` | Tarefas em Fundo | Monitoramento, inspeção de logs e envio de input para tarefas ativas. | Usar TaskId retornado pelo sistema. |
| `ask_question` | Interação Humana | Apresentação de menus de múltipla escolha interativos para o usuário. | Ideal para alinhamento de requisitos e escolhas do `/grill-me_v2`. |
| `search_marketplace`| Extensibilidade | Busca de novos plugins e skills no catálogo oficial da plataforma. | Sugira através de `<plugin-card catalog-id="...">`. |
| `search_web` | Inteligência | Pesquisa na web para obtenção de documentações e dados externos. | Usar para referências públicas e bibliotecas de terceiros. |
| `list_plugin_accounts`| Autenticação | Lista status de login e contas conectadas para plugins instalados. | Verificação prévia antes de chamar CLIs de plugins integrados. |
| `swarm` | Colaboração | Orquestração de múltiplos agentes em quadro de mensagens compartilhado. | Adequado para tarefas com múltiplos ângulos de revisão concorrente. |

---

## 2. Ferramentas da CLI do Projeto (`corporate-engineer`)

O framework disponibiliza comandos utilitários executáveis via Python:

```powershell
# Execução recomendada via ambiente virtual (.venv)
.venv\Scripts\python -m corporate_engineer.cli <subcomando>
```

| Subcomando | Opções | Finalidade | Saídas Suportadas |
|---|---|---|---|
| `audit` | `--strict`, `--format [text\|json]` | Executa auditoria Pre-Flight (Ruff, Mypy, Pytest, Secret Scanner) localmente. | Código de saída 0 (aprovação) ou 1 (reprovação); JSON estruturado. |
| `index` | `<path>`, `--output <file>`, `--format [text\|json]` | Analisa a base de código com AST, extraindo classes, funções, herança e grafos de chamada. | Grafo semântico estruturado em JSON ou sumário textual. |
| `dag` | `--show-phases`, `--checkpoints`, `--format [text\|json]` | Inspeciona a máquina de estados (FSM) do DAG, fases e checkpoints salvos. | Tabela FSM ou JSON com status dos checkpoints. |
| `mcp` | `<ping\|list-tools\|call>`, `--transport [stdio\|sse]`, `--url <url>`, `--command <cmd>` | Testa conectividade e schemas de ferramentas de servidores MCP. | Status da conexão e lista tipada de schemas. |

---

## 3. Scripts Utilitários Corporativos (`.agents/skills/corp-pipeline/scripts/`)

| Script | Execução Recomendada | Finalidade |
|---|---|---|
| `secret_scanner.py` | `.venv\Scripts\python .agents/skills/corp-pipeline/scripts/secret_scanner.py .` | Scanner corporativo de 10 assinaturas de alta confiança para detecção de segredos hardcoded. Retorna 0 se limpo, 1 se vazado. |
| `stack_detector.py` | `.venv\Scripts\python .agents/skills/corp-pipeline/scripts/stack_detector.py .` | Detector universal de stack tecnológica e mapeador dos comandos ideais de teste, lint e typecheck. |
| `pr_automator.py` | `.venv\Scripts\python .agents/skills/corp-pipeline/scripts/pr_automator.py --ticket-id ... --slug ... --title ... --body-file ...` | Criação de branch de feature (`feat/`), commit semântico, push remoto e abertura de PR via GitHub CLI. |
