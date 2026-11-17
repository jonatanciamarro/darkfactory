# 🐛 Bugs Reais Encontrados & Lições de Hardening no DarkFactory

> **Casos Reais de Falhas em Produção, Análises de Causa Raiz (RCA) e Mitigações Arquiteturais**
> Extraído diretamente do histórico de telemetria do `state.md` e dos commits de endurecimento de código do projeto.

---

## 🚨 Caso 1: Exceções Silenciosas no Auth Gate & RunningHub Bot

### 1. O Sintoma em Produção
Durante execuções noturnas automatizadas, o pipeline completava seu ciclo reportando "sucesso" no console, mas o diretório final não continha os vídeos gerados ou produzia vídeos com 0 bytes. Não havia nenhum stack trace visível no terminal.

### 2. Análise de Causa Raiz (RCA)
No módulo `src/auth_gate.py` e em `src/factory/runninghub_bot.py`, rotinas críticas de validação de cookies de sessão e chamadas HTTP utilizavam o antipadrão de captura genérica sem relançamento:
```python
# ❌ CÓDIGO PROBLEMÁTICO ORIGINAL (Anti-pattern)
try:
    response = requests.post(RUNNINGHUB_API_URL, json=payload, timeout=30)
    task_id = response.json().get("data", {}).get("taskId")
except:
    pass  # Falha silenciosa! task_id fica como None
```
Quando o cookie do Google Flow ou RunningHub expirava, o `requests` gerava uma exceção 401/403 ou timeout. O bloco `except: pass` engolia o erro. O bot continuava a execução com variáveis nulas, propagando o estado corrompido para as etapas de download que falhavam silenciosamente.

### 3. Correção Aplicada & Refatoração
Substituição de todas as capturas genéricas por exceções tipadas, logging estruturado de severidade `ERROR` contendo o payload e propagação explícita com `raise`:
```python
# ✅ CÓDIGO CORRIGIDO (Production-grade)
try:
    response = requests.post(RUNNINGHUB_API_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "taskId" not in data.get("data", {}):
        raise KeyError(f"RunningHub response missing taskId: {data}")
    task_id = data["data"]["taskId"]
except requests.RequestException as exc:
    logger.error("Falha irrecuperável na chamada RunningHub: %s | URL: %s", exc, RUNNINGHUB_API_URL)
    raise RuntimeError(f"RunningHub API unreachable during video generation: {exc}") from exc
```

### 4. Conceito de Engenharia
- **Fail-Fast Principle**: O sistema deve falhar imediatamente no ponto de detecção da anomalia, e não mascará-la para falhar tardiamente em outro lugar.
- **Error Observability**: Exceções não tratadas sem log são invisíveis para APMs e pipelines de CI/CD.

### 5. 🎓 Como Contar na Entrevista (Script de 60s)
> *"Um dos nossos maiores aprendizados operacionais foi a erradicação de exceções silenciosas. Tínhamos blocos de `bare except: pass` em rotinas de autenticação e bots de scraping. Em caso de timeout de rede, o código continuava rodando com ponteiros nulos e falhava passos depois sem qualquer log explicativo. Refatoramos a base inteira para tipagem estrita de exceções, com re-raise obrigatório e logs com contexto. Aprendi na prática que uma falha explícita com crash é infinitamente melhor do que uma execução 'verde' que produz dados corrompidos."*

---

## 🚨 Caso 2: Falha Silenciosa por Ignorar o Return Code do FFmpeg

### 1. O Sintoma em Produção
Em algumas cenas, o áudio final da montagem ficava mudo ou o vídeo apresentava travamentos de codec a partir do minuto 10. O script Python de renderização concluía com status code 0.

### 2. Análise de Causa Raiz (RCA)
A chamada ao binário do FFmpeg era feita com `subprocess.run(cmd)` sem validar o retorno:
```python
# ❌ CÓDIGO PROBLEMÁTICO ORIGINAL
subprocess.run(["ffmpeg", "-y", "-i", input_file, "-af", "loudnorm", output_file])
# Python continua mesmo se o FFmpeg abortar com erro de sintaxe de filtro!
```
O FFmpeg pode falhar por sintaxe inválida no `filter_complex`, memória de vídeo insuficiente ou codecs corrompidos. Como o Python não verificava `result.returncode != 0`, ele assumia que o arquivo de saída gerado estava íntegro (quando na verdade estava truncado ou nem existia).

### 3. Correção Aplicada & Refatoração
Implementação de wrapper defensivo no `src/video/ffmpeg_processor.py`:
```python
# ✅ CÓDIGO CORRIGIDO
res = subprocess.run(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    timeout=600  # Timeout defensivo de 10 minutos
)
if res.returncode != 0:
    logger.error("FFmpeg falhou com código %d. Stderr:\n%s", res.returncode, res.stderr[-1000:])
    raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
```

### 4. Conceito de Engenharia
- **External Process Boundary Validation**: Processos externos operam fora do controle do runtime da linguagem. O exit code é o único contrato formal de sucesso.
- **Defensive Timeout**: Processos de renderização de mídia podem entrar em deadlock se o codec encontrar frames corrompidos.

### 5. 🎓 Como Contar na Entrevista (Script de 60s)
> *"Tivemos um caso em que o FFmpeg falhava na aplicação de um filtro de áudio complexo e o script Python continuava como se nada tivesse acontecido porque o `subprocess.run` não checava o exit code. O pipeline tentava montar o documentário com stems vazios. Corrigimos criando um wrapper centralizado que valida obrigatoriamente `returncode == 0`, extrai os últimos 1.000 caracteres de stderr em caso de falha e impõe timeouts rígidos para evitar processos zumbis consumindo CPU."*

---

## 🚨 Caso 3: Windows cp1252 vs UTF-8 (O Bug dos Caracteres Cirílicos)

### 1. O Sintoma em Produção
Ao rodar a geração do documentário sobre a Guerra Fria em máquinas Windows, o pipeline crashava com `UnicodeEncodeError: 'charmap' codec can't encode characters in position X` ao tentar exibir logs no terminal contendo palavras em russo como `'СТАРТ'` ou caracteres acentuados em português.

### 2. Análise de Causa Raiz (RCA)
Por padrão histórico de compatibilidade retroativa, o Python no Windows inicializa os descritores `sys.stdout` e `sys.stderr` utilizando a página de código legada `cp1252` (Windows ANSI), e não UTF-8. Quando uma string Unicode contém caracteres fora do mapa de 256 bytes do cp1252, o runtime dispara exceção fatal.

### 3. Correção Aplicada & Refatoração
Formalização do **ADR-01** (Decisão Arquitetural 01) e blindagem obrigatória no topo de cada ponto de entrada:
```python
# ✅ CÓDIGO CORRIGIDO (Inserido no topo de todos os scripts)
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
```
Além disso, foi padronizado que toda abertura de arquivos via `open()` passa explicitamente `encoding="utf-8"`.

### 4. Conceito de Engenharia
- **Platform-Specific Runtime Quirks**: O comportamento padrão de I/O de um mesmo runtime varia drasticamente entre sistemas operacionais (Windows vs Linux vs macOS).
- **Architectural Decision Record (ADR)**: Decisões cross-cutting devem ser documentadas como regras arquiteturais mandatórias.

### 5. 🎓 Como Contar na Entrevista (Script de 60s)
> *"Esse é um clássico problema de engenharia multiplataforma. O projeto rodava perfeitamente em Linux em containers, mas ao executar na máquina Windows de desenvolvimento, nomes históricos russos e termos acentuados derrubavam o processo com `UnicodeEncodeError` devido ao padrão legado cp1252 do Windows. Criamos o ADR-01, que força a reconfiguração de stdout e stderr para UTF-8 no momento do boot de cada módulo. Mostra a importância de nunca confiar nos defaults implícitos do sistema operacional."*

---

## 🚨 Caso 4: Quebra de Imports com a Modernização de `pypdf>=4.0.0`

### 1. O Sintoma em Produção
O módulo de mineração de documentos desclassificados (`research_engine.py`) quebrou com `ModuleNotFoundError: No module named 'PyPDF2'` após uma atualização de dependências no ambiente virtual.

### 2. Análise de Causa Raiz (RCA)
O projeto dependia do pacote descontinuado `PyPDF2`. A comunidade oficial do projeto migrou o desenvolvimento para o pacote `pypdf` a partir da versão 4.0.0, com uma API completamente renovada, métodos camelCase renomeados para snake_case (`numPages` → `len(reader.pages)`) e melhorias substanciais de performance e segurança contra PDFs maliciosos.

### 3. Correção Aplicada & Refatoração
Substituição da biblioteca no `requirements.txt`, refatoração das chamadas de extração de texto para a nova API de `pypdf` e adição de testes automatizados com fixtures de PDFs históricos reais.

### 4. Conceito de Engenharia
- **Dependency Hygiene & Deprecation Lifecycle**: Bibliotecas de processamento de binários devem ser mantidas atualizadas contra vulnerabilidades de segurança (CVEs).
- **API Evolution**: Atualizações maiores (Major SemVer) exigem refatoração consciente de código consumidor.

---

## 🚨 Caso 5: Desambiguação de Módulos Duplicados (Anti-Drift Arquitetural)

### 1. O Sintoma em Produção
Bugs corrigidos na extração de fontes de domínio público continuavam acontecendo na esteira. O time descobriu que existiam dois arquivos quase idênticos no repositório: `src/research/public_domain_research_engine.py` e `src/video/public_domain_research.py`. Um agente de IA havia criado uma cópia em `src/video/` sem deletar a original.

### 2. Análise de Causa Raiz (RCA)
Drift arquitetural decorrente de trabalho autônomo sem governança estrita de arquivos. O orquestrador chamava uma versão, enquanto os testes unitários testavam a outra.

### 3. Correção Aplicada & Refatoração
Consolidação definitiva em `src/video/public_domain_research.py`, criação de uma fachada de redirecionamento temporária com aviso de depreciação e posterior remoção física do módulo legado, acompanhada da criação do **Codebase Freshness Sentinel** (auditor AST estático).

### 4. Conceito de Engenharia
- **Single Source of Truth (SSOT)**: Nenhuma entidade ou responsabilidade do sistema pode ter representação duplicada na base de código.
- **Automated Anti-Rot Gates**: Ferramentas mecânicas devem impedir a criação de arquivos redundantes antes que eles cheguem à produção.

---

## 🚨 Caso 6: Distorção de Áudio por Inter-Sample Peak Clipping no YouTube

### 1. O Sintoma em Produção
O áudio do documentário soava limpo no player local VLC, mas apresentava estalos sutis (*harsh digital clipping*) quando assistido no aplicativo do YouTube em celulares com fones de ouvido.

### 2. Análise de Causa Raiz (RCA)
O áudio havia sido normalizado em -14 LUFS com True Peak em 0.0 dBTP. Quando o YouTube transcodifica o áudio linear para codecs de compressão com perdas (AAC a 128 kbps ou Opus a 160 kbps), o processo de decodificação gera picos inter-amostras (*inter-sample peaks*) que ultrapassam 0 dBFS analógico, gerando ceifamento e distorção harmônica.

### 3. Correção Aplicada & Refatoração
Ajuste do filtro no **ADR-02**: o limite de True Peak foi calibrado estritamente para **-1.0 dBTP** com margem de segurança de headroom de 1 dB, absorvendo as oscilações de reconstrução de onda dos codecs de streaming.

### 4. Conceito de Engenharia
- **Codec Artifact Compensation**: Sistemas de produção de áudio para distribuição digital devem prever o comportamento de compressão com perdas das plataformas de destino.
