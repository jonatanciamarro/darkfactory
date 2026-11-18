#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator v2.0 — Autonomous Multi-Vector Routing Engine
DarkFactory Generative Core (Senior / Staff Level Architecture)

Provides semantic intent classification, multi-vector affinity scoring, deterministic
fallbacks, operational badge formatting, and topological DAG plan synthesis.
"""

import sys
import os
import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any


class IntentCategory(str, Enum):
    NOLAN_STORYTELLING = "nolan_storytelling"
    HISTORICAL_RESEARCH = "historical_research"
    AUDIO_ENGINEERING = "audio_engineering"
    VIDEO_SYNTHESIS_T2V = "video_synthesis_t2v"
    CINEMA_DASHBOARD = "cinema_dashboard"
    CORPORATE_ENGINEERING = "corp_engineering"
    COMPLIANCE_AND_LEGAL = "compliance_and_legal"


class ResourceKind(str, Enum):
    SUBAGENT = "subagent"
    SKILL = "skill"
    TOOL = "tool"
    WORKFLOW = "workflow"


@dataclass
class ResourceMatch:
    name: str
    kind: ResourceKind
    score: float
    rationale: str
    priority: int = 1


@dataclass
class FallbackRoute:
    primary: str
    fallback: str
    trigger_condition: str
    timeout_seconds: Optional[int] = None


@dataclass
class OrchestrationPlan:
    intent: IntentCategory
    confidence: float
    primary_agent: str
    supporting_skills: List[str]
    critical_tools: List[str]
    fallbacks: List[FallbackRoute]
    execution_steps: List[str]
    operational_badge: str
    dag_hint: Optional[Dict[str, Any]] = None


class OrchestratorV2Engine:
    """Motor de inferência, classificação e roteamento autônomo multivetorial."""

    # Padrões léxico-semânticos com peso associado
    INTENT_PATTERNS = {
        IntentCategory.NOLAN_STORYTELLING: [
            (r"\b(nolan|christopher\s*nolan)\b", 4.0),
            (r"\b(roteiro|roteiriza[çc][ãa]o|storyboard|5\s*atos?|cinematogr[áa]fic[oa])\b", 3.0),
            (r"\b(crosscutting|kodak|vision3|70mm|imax|chiaroscuro|dual-shot)\b", 3.5),
            (r"\b(murch|eye-trace|regra\s*dos\s*seis|curiosity\s*gap)\b", 2.5),
        ],
        IntentCategory.HISTORICAL_RESEARCH: [
            (r"\b(pesquis[ae]|research|desclassificad[oa]s?|declassified)\b", 3.5),
            (r"\b(arquivos?|fontes?|dom[íi]nio\s*p[úu]blico|public\s*domain)\b", 2.5),
            (r"\b(cia|kgb|guerra\s*fria|cold\s*war|soviet|1983|documentos?)\b", 3.0),
            (r"\b(fact-checking|verific[aã]o\s*de\s*fatos)\b", 2.5),
        ],
        IntentCategory.AUDIO_ENGINEERING: [
            (r"\b(cosyvoice|kokoro|narra[çc][ãa]o|voice|voz|tts)\b", 3.5),
            (r"\b(mixagem|audio|stem|loudness|-14\s*lufs|-1\.0\s*dbtp|ebu\s*r128)\b", 3.5),
            (r"\b(zimmer|ost|trilha|soundtrack|foley|sfx|braams?|shepard)\b", 3.0),
            (r"\b(sidechain|ducking|complex\s*pro|warp)\b", 2.0),
        ],
        IntentCategory.VIDEO_SYNTHESIS_T2V: [
            (r"\b(veo|veo\s*3\.1|omni\s*flash|google\s*flow)\b", 3.5),
            (r"\b(runninghub|comfyui|minimax|wan\s*2\.2|t2v|render(izar)?|take)\b", 3.5),
            (r"\b(quarentena|quarantine|qc\s*failure|v[íi]deo)\b", 3.0),
            (r"\b(gpu\s*economy|cancelamento\s*autom[áa]tico)\b", 2.5),
        ],
        IntentCategory.CINEMA_DASHBOARD: [
            (r"\b(dashboard|painel|8502|cockpit)\b", 3.5),
            (r"\b(fastapi|web\s*spa|server|porta\s*8502)\b", 3.0),
            (r"\b(topic_generator|sugest[õo]es?\s*de\s*temas?)\b", 2.5),
            (r"\b(deploy|start.*dashboard)\b", 2.5),
        ],
        IntentCategory.CORPORATE_ENGINEERING: [
            (r"\b(corp-pipeline|shift-left|tdd|testes?|pytest)\b", 3.5),
            (r"\b(branch|pull\s*request|pr|git|feature\s*branch)\b", 3.0),
            (r"\b(refatora[çc][ãa]o|bug(fix)?|corre[çc][ãa]o|corrigir|ast|freshness|c[óo]digo\s*zumbi)\b", 3.0),
            (r"\b(plan-v2|grill-v2|gate\s*1|gate\s*2)\b", 2.5),
        ],
        IntentCategory.COMPLIANCE_AND_LEGAL: [
            (r"\b(green\s*dollar|compliance|edsa|fair\s*use)\b", 3.5),
            (r"\b(content\s*id|disput[ae]|direitos?\s*autorais?)\b", 3.5),
            (r"\b(youtube\s*compliance|algor[íi]tmic[oa]|seo\s*global)\b", 3.0),
            (r"\b(monetiza[çc][ãa]o|100/100)\b", 2.5),
        ],
    }

    # Mapa de recursos canônicos por intenção
    RESOURCE_REGISTRY = {
        IntentCategory.NOLAN_STORYTELLING: {
            "agents": [("nolan-director", 0.96, "Showrunner autoral DarkFactory & especialista em 5 Atos Nolan")],
            "skills": [
                ("darkfactory-nolan", 0.94, "Diretiva Christopher Nolan e templates de prompts Dual-Shot"),
                ("nolan-dark-history-director", 0.90, "Modelagem de tensão psicológica e ritmo Walter Murch"),
            ],
            "tools": ["write_file", "read_file", "edit_file"],
        },
        IntentCategory.HISTORICAL_RESEARCH: {
            "agents": [("architect", 0.88, "Especialista em estruturação de dossiês e análise documental")],
            "skills": [
                ("verification-loop", 0.90, "Validação de fontes primárias e fact-checking rigoroso"),
                ("api-design", 0.85, "Estruturação de DTOs para dossiês históricos"),
            ],
            "tools": ["run_command", "read_file", "write_file"],
        },
        IntentCategory.AUDIO_ENGINEERING: {
            "agents": [("python-reviewer", 0.91, "Especialista em processamento de áudio, normalização e DSP")],
            "skills": [
                ("darkfactory-review", 0.92, "Inspeção de compliance EBU R128 (-14 LUFS / -1.0 dBTP)"),
                ("python-patterns", 0.88, "Arquitetura limpa para pipelines de DSP e stems"),
            ],
            "tools": ["run_command", "edit_file", "read_file"],
        },
        IntentCategory.VIDEO_SYNTHESIS_T2V: {
            "agents": [("e2e-runner", 0.93, "Automação RPA de browsers, RunningHub ComfyUI e Google Flow")],
            "skills": [
                ("darkfactory-pipeline", 0.92, "Orquestração completa dos 6 Golden Standards de vídeo"),
                ("error-handling", 0.89, "Quarentena atômica de takes defeituosos e circuit breaker"),
            ],
            "tools": ["run_command", "edit_file", "read_file"],
        },
        IntentCategory.CINEMA_DASHBOARD: {
            "agents": [("architect", 0.92, "Arquiteto de sistemas web FastAPI e SPAs")],
            "skills": [
                ("darkfactory-deploy", 0.94, "Validação pre-flight e startup FastAPI na porta 8502"),
                ("api-design", 0.87, "Design de endpoints REST para cockpit de produção"),
            ],
            "tools": ["run_command", "edit_file", "read_file"],
        },
        IntentCategory.CORPORATE_ENGINEERING: {
            "agents": [
                ("tdd-guide", 0.96, "Especialista em Shift-Left TDD e cobertura de testes"),
                ("architect", 0.92, "Design arquitetural, ADRs e análise de blast-radius"),
            ],
            "skills": [
                ("corp-pipeline", 0.97, "Esteira corporativa de 5 fases, branch protection e PRs"),
                ("plan-v2", 0.93, "Planejamento topológico com DAG e cálculo de blast-radius"),
                ("grill-v2", 0.91, "Interrogador socrático proativo de staff engineer"),
            ],
            "tools": ["run_command", "write_file", "edit_file"],
        },
        IntentCategory.COMPLIANCE_AND_LEGAL: {
            "agents": [("security-reviewer", 0.93, "Auditoria de segurança, conformidade e conformidade de dados")],
            "skills": [
                ("darkfactory-review", 0.94, "Verificação Green Dollar 100/100 e enquadramento EDSA"),
                ("verification-loop", 0.88, "Auditoria de licenças de mídia e geração de Dispute Kit"),
            ],
            "tools": ["read_file", "run_command", "write_file"],
        },
    }

    # Matriz canônica de fallbacks
    FALLBACK_MATRIX = {
        IntentCategory.VIDEO_SYNTHESIS_T2V: [
            FallbackRoute(
                primary="Google Flow (Veo 3.1 & Omni Flash)",
                fallback="RunningHub MiniMax H3 / Wan 2.2",
                trigger_condition="Quota esgotada, timeout > 90s ou bloqueio de browser",
                timeout_seconds=90,
            ),
            FallbackRoute(
                primary="RunningHub Conta 1",
                fallback="RunningHub Conta de Contingência",
                trigger_condition="Falha de saldo ou rate limit de GPU",
                timeout_seconds=30,
            ),
        ],
        IntentCategory.AUDIO_ENGINEERING: [
            FallbackRoute(
                primary="CosyVoice 3 (RunningHub API)",
                fallback="Kokoro-82M ONNX local (bm_george)",
                trigger_condition="API inacessível, erro 5xx ou latência > 15s",
                timeout_seconds=15,
            ),
            FallbackRoute(
                primary="Flow Music (Lyria & Zimmer OST)",
                fallback="RunningHub MiniMax Music 3",
                trigger_condition="Falha de conexão com flowmusic.app",
                timeout_seconds=45,
            ),
        ],
        IntentCategory.HISTORICAL_RESEARCH: [
            FallbackRoute(
                primary="Public Domain Research Engine (Arquivos Militares / CIA)",
                fallback="Biblioteca Local de Dossiês Canônicos (data/scripts/)",
                trigger_condition="Timeout de raspagem de rede ou CAPTCHA externo",
                timeout_seconds=20,
            )
        ],
        IntentCategory.CORPORATE_ENGINEERING: [
            FallbackRoute(
                primary="Shift-Left TDD Automatizado (Pytest)",
                fallback="Auditoria Sintática e Tipagem Estrita (py_compile & mypy)",
                trigger_condition="Dependências ausentes no venv local",
                timeout_seconds=10,
            )
        ],
        IntentCategory.CINEMA_DASHBOARD: [
            FallbackRoute(
                primary="FastAPI Uvicorn Local (:8502)",
                fallback="CLI de Telemetria e Status (darkfactory-status)",
                trigger_condition="Porta 8502 em uso ou bloqueada por firewall",
                timeout_seconds=5,
            )
        ],
        IntentCategory.COMPLIANCE_AND_LEGAL: [
            FallbackRoute(
                primary="YouTube Compliance QC Automatizado",
                fallback="Checklist Manual EDSA & Template de Disputa Fair Use",
                trigger_condition="YouTube API quota ou metadados incompletos",
                timeout_seconds=15,
            )
        ],
        IntentCategory.NOLAN_STORYTELLING: [
            FallbackRoute(
                primary="Nolan Director 5 Atos (Prompts Dual-Shot Kodak Vision3)",
                fallback="Template Estrutural Canônico de 40 Cenas (Dossiê Serpukhov)",
                trigger_condition="Score do Story Validator < 80.0",
                timeout_seconds=30,
            )
        ],
    }

    def classify_intent(self, query: str) -> Tuple[IntentCategory, float]:
        """Classifica a intenção da solicitação usando scoring multivetorial ponderado."""
        query_lower = query.lower()
        scores: Dict[IntentCategory, float] = {cat: 0.0 for cat in IntentCategory}

        for category, patterns in self.INTENT_PATTERNS.items():
            for regex_str, weight in patterns:
                matches = re.findall(regex_str, query_lower, re.IGNORECASE)
                if matches:
                    scores[category] += weight * len(matches)

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        if max_score == 0.0:
            # Fallback inteligente para Corporate Engineering
            return IntentCategory.CORPORATE_ENGINEERING, 0.75

        # Normalização sigmoidal suave para confiança entre 0.75 e 0.99
        confidence = min(0.99, max(0.75, 0.75 + (max_score / (max_score + 4.0)) * 0.24))
        return best_category, round(confidence, 2)

    def score_resources(self, intent: IntentCategory) -> List[ResourceMatch]:
        """Ranqueia subagentes, skills e ferramentas por relevância ponderada."""
        data = self.RESOURCE_REGISTRY.get(intent, {})
        matches: List[ResourceMatch] = []

        for name, score, rationale in data.get("agents", []):
            matches.append(ResourceMatch(name=name, kind=ResourceKind.SUBAGENT, score=score, rationale=rationale, priority=1))

        for name, score, rationale in data.get("skills", []):
            matches.append(ResourceMatch(name=name, kind=ResourceKind.SKILL, score=score, rationale=rationale, priority=2))

        for tool_name in data.get("tools", []):
            matches.append(ResourceMatch(name=tool_name, kind=ResourceKind.TOOL, score=0.80, rationale=f"Ferramenta crítica para {intent.value}", priority=3))

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def resolve_fallbacks(self, intent: IntentCategory) -> List[FallbackRoute]:
        """Retorna as rotas determinísticas de contingência para o domínio."""
        return self.FALLBACK_MATRIX.get(intent, [])

    def synthesize_plan(self, query: str) -> OrchestrationPlan:
        """Sintetiza um plano completo de orquestração com badge e passos topológicos."""
        intent, confidence = self.classify_intent(query)
        resources = self.score_resources(intent)
        fallbacks = self.resolve_fallbacks(intent)

        agents = [r.name for r in resources if r.kind == ResourceKind.SUBAGENT]
        skills = [r.name for r in resources if r.kind == ResourceKind.SKILL]
        tools = [r.name for r in resources if r.kind == ResourceKind.TOOL]

        primary_agent = agents[0] if agents else "architect"
        top_skill = skills[0] if skills else "corp-pipeline"
        top_tool = tools[0] if tools else "run_command"

        badge = f"🎯 Orquestrador: [Skill: {top_skill} | Agente: {primary_agent} | Ferramenta: {top_tool}]"

        execution_steps = [
            f"1. [Alinhamento]: Validar premissas do domínio '{intent.value}' com agente '{primary_agent}'.",
            f"2. [Preparação]: Carregar diretivas da skill '{top_skill}' e preparar ferramentas {tools[:2]}.",
            f"3. [Execução]: Conduzir o fluxo cirúrgico com fallback ativo para {fallbacks[0].fallback if fallbacks else 'contingência padrão'}.",
            f"4. [Auditoria]: Executar quality gate e conformidade operacional.",
        ]

        dag_hint = {
            "root_intent": intent.value,
            "primary_agent": primary_agent,
            "parallel_skills": skills,
            "sequential_steps": len(execution_steps),
        }

        return OrchestrationPlan(
            intent=intent,
            confidence=confidence,
            primary_agent=primary_agent,
            supporting_skills=skills,
            critical_tools=tools,
            fallbacks=fallbacks,
            execution_steps=execution_steps,
            operational_badge=badge,
            dag_hint=dag_hint,
        )

    def plan_to_json(self, plan: OrchestrationPlan) -> str:
        """Serializa o plano para JSON indentado."""
        raw = asdict(plan)
        raw["intent"] = plan.intent.value
        return json.dumps(raw, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="DarkFactory Master Orchestrator v2.0 Engine")
    parser.add_argument("--task", type=str, required=True, help="Descrição da tarefa para orquestração")
    parser.add_argument("--format", type=str, choices=["text", "json"], default="text", help="Formato de saída")
    parser.add_argument("--badge-only", action="store_true", help="Retorna apenas a badge de transparência")

    args = parser.parse_args()
    engine = OrchestratorV2Engine()
    plan = engine.synthesize_plan(args.task)

    if args.badge_only:
        print(plan.operational_badge)
        return

    if args.format == "json":
        print(engine.plan_to_json(plan))
    else:
        print(plan.operational_badge)
        print(f"\nDomínio Identificado: {plan.intent.value} (Confiança: {plan.confidence * 100:.1f}%)")
        print(f"Agente Primário:      {plan.primary_agent}")
        print(f"Skills de Suporte:    {', '.join(plan.supporting_skills)}")
        print(f"Ferramentas Críticas: {', '.join(plan.critical_tools)}")
        print("\nPassos de Execução:")
        for step in plan.execution_steps:
            print(f"  {step}")
        if plan.fallbacks:
            print("\nRotas de Fallback:")
            for fb in plan.fallbacks:
                print(f"  • {fb.primary} ➔ {fb.fallback} (Gatilho: {fb.trigger_condition})")


if __name__ == "__main__":
    main()
