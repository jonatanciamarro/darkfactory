"""
Grill-Me-v2 Core Analyzer & Socratic Engine
Grounds architectural context, formulates opinionated inquiry across the 4 quadrants,
and exports executable ADRs + TDD Seeds for Corporate Pipeline.
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal


@dataclass
class CodebaseContext:
    stack: str
    existing_patterns: List[str] = field(default_factory=list)
    identified_risks: List[str] = field(default_factory=list)
    suggested_dto_types: List[str] = field(default_factory=list)


@dataclass
class SocraticQuestion:
    quadrant: Literal["contracts", "failure_modes", "security_compliance", "pragmatism_yagni"]
    question: str
    opinionated_recommendation: str
    tradeoffs: Dict[str, str]
    options: List[str]


@dataclass
class GrillSessionResult:
    feature_slug: str
    business_context: str
    decisions_matrix: Dict[str, str]
    contracts_schema: Dict[str, str]
    edge_cases: List[str]
    tdd_scenarios: List[str]
    adr_markdown: str


class ADRGenerator:
    """Gera Architectural Decision Records (ADRs) executáveis enriquecidos com cenários TDD."""

    @classmethod
    def create_adr(
        cls,
        title: str,
        feature_slug: str,
        context: str,
        decisions: Dict[str, str],
        failure_modes: List[str],
        tdd_scenarios: List[str],
    ) -> str:
        decisions_formatted = "\n".join(
            f"- **{k}**: {v}" for k, v in decisions.items()
        )
        failures_formatted = "\n".join(
            f"- ⚠️ {f}" for f in failure_modes
        )
        tdd_formatted = "\n".join(
            f"- [ ] `{scenario}`" for scenario in tdd_scenarios
        )

        return f"""# ADR: {title}

> **Status**: Accepted (Decidido via Grill-v2 Socrático)  
> **Feature Slug**: `{feature_slug}`  
> **Framework**: Corporate 5-Phase Engineering Pipeline

---

## 1. Context & Business Drivers
{context}

---

## 2. The Socratic Decisions Matrix
{decisions_formatted}

---

## 3. Failure Modes & Resilience Architecture
{failures_formatted}

---

## 4. Shift-Left TDD Seeds (Executable Specs)
{tdd_formatted}
"""


class GrillAnalyzer:
    """Motor de Deep Grounding e Questionamento Socrático Multidimensional."""

    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)

    def analyze_codebase(self) -> CodebaseContext:
        """Inspeciona o repositório para capturar contexto arquitetural antes de questionar."""
        stack = "unknown"
        patterns = []
        risks = []
        suggested_dtos = []

        # Detecção de Stack e Frameworks
        if (self.workspace / "pyproject.toml").exists() or (self.workspace / "requirements.txt").exists():
            stack = "python"
            patterns.append("python-poetry-or-pip")
        elif (self.workspace / "package.json").exists():
            stack = "node"
            patterns.append("node-npm-ecosystem")
        elif (self.workspace / "go.mod").exists():
            stack = "go"
            patterns.append("go-modules")

        # Varredura rasa de modelos e convenções
        for root, dirs, files in os.walk(self.workspace):
            # Ignora pastas de cache e ambiente virtual
            dirs[:] = [d for d in dirs if d not in {".git", ".pytest_cache", "venv", "node_modules", "__pycache__"}]
            for f in files:
                lower_f = f.lower()
                if "model" in lower_f or "schema" in lower_f:
                    patterns.append(f"data-models-found:{f}")
                if "test" in lower_f:
                    patterns.append(f"test-suite-found:{f}")
                if f.endswith((".py", ".ts", ".go")):
                    suggested_dtos.append(Path(f).stem)

        return CodebaseContext(
            stack=stack,
            existing_patterns=patterns or ["standard-project-layout"],
            identified_risks=risks,
            suggested_dto_types=list(set(suggested_dtos))[:5],
        )

    def formulate_socratic_inquiry(self, demand: str) -> List[SocraticQuestion]:
        """Gera perguntas de alto impacto cobrindo os 4 quadrantes socráticos de Staff Engineer."""
        questions = [
            SocraticQuestion(
                quadrant="contracts",
                question=f"Como devemos modelar os contratos de dados e interfaces estritas para '{demand}'?",
                opinionated_recommendation="Contratos tipados com schemas imutáveis (dataclass/Pydantic) e validação em tempo de fronteira.",
                tradeoffs={
                    "Contratos Estritos (Recomendado)": "Prós: Zero type drifts, autocompletion e validação em tempo de compilação. Contras: Leve overhead de tipagem inicial.",
                    "Tipos Flexíveis/Dicionários": "Prós: Rápido de rascunhar. Contras: Erros silenciosos em runtime e quebras em produção."
                },
                options=[
                    "(Recomendado) Schemas imutáveis tipados e DTOs explícitos",
                    "Dicionários soltos com acesso dinâmico por chaves"
                ]
            ),
            SocraticQuestion(
                quadrant="failure_modes",
                question="Quais são os principais modos de falha e como o sistema deve reagir a indisponibilidades parciais?",
                opinionated_recommendation="Estratégia de degradação graciosa com Circuit Breakers, timeouts agressivos e fallbacks assíncronos.",
                tradeoffs={
                    "Resiliência com Fallback (Recomendado)": "Prós: Sistema não trava o usuário final se um serviço externo cair. Contras: Necessita gerenciar estados intermediários.",
                    "Fail-Fast Imediato": "Prós: Implementação trivial. Contras: Falhas em cascata que derrubam o fluxo completo."
                },
                options=[
                    "(Recomendado) Degradação graciosa com fallback e circuit breaker",
                    "Fail-fast com interrupção e log de exceção direta"
                ]
            ),
            SocraticQuestion(
                quadrant="security_compliance",
                question="Quais são os vetores de segurança, vazamento de credenciais e compliance regulatório aplicáveis?",
                opinionated_recommendation="Zero secrets em disco/repositório, injeção estrita via variáveis de ambiente e validação de tokens com expiração curta.",
                tradeoffs={
                    "Segurança Corporativa Estrita (Recomendado)": "Prós: Compliance total SOC2/ISO27001 e zero risco de vazamento de credenciais. Contras: Exige configuração prévia de env.",
                    "Configuração Simplificada": "Prós: Fácil de rodar local. Contras: Risco crítico de exposição acidental de credenciais."
                },
                options=[
                    "(Recomendado) Injeção dinâmica de credenciais via ENV e sanitização prévia",
                    "Armazenamento local em arquivo de configuração sem sanitização"
                ]
            ),
            SocraticQuestion(
                quadrant="pragmatism_yagni",
                question="Qual é o trade-off de pragmatismo versus complexidade (YAGNI) para esta entrega?",
                opinionated_recommendation="Implementar a solução mínima arquiteturalmente elegante que atenda os requisitos sem introduzir microsserviços ou filas prematuras.",
                tradeoffs={
                    "Pragmatismo Cirúrgico (Recomendado)": "Prós: Entrega rápida, código testável e fácil manutenção. Contras: Pode exigir refatoração se o volume escalar 100x.",
                    "Arquitetura Hiper-Genérica": "Prós: Suporta teoricamente qualquer escala futura. Contras: Overengineering severo e lentidão de entrega."
                },
                options=[
                    "(Recomendado) Implementação modular cirúrgica focada nos requisitos atuais",
                    "Arquitetura distribuída complexa antecipando escala massiva hipotética"
                ]
            )
        ]

        return questions
