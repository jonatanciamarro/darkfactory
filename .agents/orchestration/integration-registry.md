# Registro de Integrações e MCPs (`integration-registry.md`)

> **Catálogo de Clientes MCP, Plugins e Integrações Externas**  
> *Mapeamento de protocolos de integração, transportes, autenticação e fronteiras de permissão.*

---

## 1. Conectores e Clientes MCP do Sistema (`src/corporate_engineer/mcp/`)

O framework implementa conectores robustos para o Model Context Protocol (MCP) com validação rígida via Pydantic v2:

| Conector / Transporte | Classe de Implementação | Protocolo Suportado | Status Operacional | Recursos & Segurança |
|---|---|---|---|---|
| **MCP Stdio Local** | `StdioMCPClient` | JSON-RPC 2.0 via `stdin`/`stdout` de subprocessos | `AVAILABLE` | Isolamento em processo filho; timeout configurável; extração tipada de schemas. |
| **MCP SSE Remoto** | `RemoteMCPSSEClient` | Server-Sent Events (SSE) / JSON-RPC 2.0 HTTP | `AVAILABLE` | Injeção de Bearer Tokens e headers corporativos (`X-Corporate-*`); streaming de eventos. |

### Validação de Conectividade MCP via CLI:
```powershell
# Teste de ping e schemas de ferramentas:
.venv\Scripts\python -m corporate_engineer.cli mcp ping --transport stdio --command "python -m dummy_server"
.venv\Scripts\python -m corporate_engineer.cli mcp list-tools --transport sse --url "https://mcp.internal.corp/events"
```

---

## 2. Servidores MCP no Ambiente Antigravity (`mcp_config.json`)

- **Escopo do Projeto**: `.agents/mcp_config.json` (ou empacotado em plugins).
- **Escopo Global**: `~/.gemini/config/mcp_config.json`.
- **Status Atual no Workspace**: Nenhum servidor MCP persistente configurado em `.agents/mcp_config.json`. Os testes de cliente cobrem mocks e servidores dinâmicos.

---

## 3. Plugins e Integrações do Marketplace

O ecossistema Antigravity suporta plugins oficiais e de parceiros. O status de autenticação deve ser sempre verificado via `list_plugin_accounts` antes de operações que exigem credenciais.

| Categoria | Plugins em Destaque | Status | Fronteira de Permissão |
|---|---|---|---|
| **Google Workspace** | `gdocs`, `gsheets`, `gslides` | `AVAILABLE_VIA_MARKETPLACE` | Leitura e escrita sob demanda; requer autenticação da conta Google. |
| **Developer Tools** | `chrome-devtools-plugin`, `android-cli-plugin` | `AVAILABLE_VIA_MARKETPLACE` | Depuração via Puppeteer e Android SDK. |
| **Cloud Hosting** | `netlify`, `railway` | `AVAILABLE_VIA_MARKETPLACE` | Deploy, monitoramento e inspeção de logs. Operações de deploy exigem Gate 2. |
| **Project Tracking** | `linear`, `atlassian-twg-cli` | `AVAILABLE_VIA_MARKETPLACE` | Sincronização de tickets e issues. |

---

## 4. Integração Remota Git & GitHub CLI

- **Repositório Remoto**: `origin` (`https://github.com/jonatanciamarro/corporate-engineer.git`).
- **Automação de PR**: Script `pr_automator.py` interage com o GitHub CLI (`gh`).
- **Regra de Proteção**: Proibido push direto na branch `main`. Todo código de feature deve ser submetido via branch `feat/<TICKET_ID>-<slug>` ou `fix/<TICKET_ID>-<slug>`.
