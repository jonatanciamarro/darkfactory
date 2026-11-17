"""
Tests for orchestrator-v2 (Master Autonomous Orchestrator v2.0)
Corporate 5-Phase Engineering Pipeline: Phase 2 (Shift-Left TDD - RED Stage)

Tests verify the contracts, semantic intent taxonomy, multi-vector affinity scoring,
deterministic fallbacks, DAG-ready orchestration plans, and operational badge generation.
"""

import json
import pytest
from pathlib import Path

# Tentativa de importação dos módulos da Fase 3
try:
    from agents.skills.orchestrator_v2.scripts.orchestrator_engine import (
        OrchestratorV2Engine,
        IntentCategory,
        ResourceKind,
        ResourceMatch,
        FallbackRoute,
        OrchestrationPlan,
    )
except ImportError:
    try:
        import sys
        sys.path.insert(
            0,
            str(Path(__file__).parent.parent / ".agents" / "skills" / "orchestrator-v2" / "scripts")
        )
        from orchestrator_engine import (
            OrchestratorV2Engine,
            IntentCategory,
            ResourceKind,
            ResourceMatch,
            FallbackRoute,
            OrchestrationPlan,
        )
    except ImportError:
        OrchestratorV2Engine = None
        IntentCategory = None
        ResourceKind = None
        ResourceMatch = None
        FallbackRoute = None
        OrchestrationPlan = None


class TestOrchestratorV2Contracts:
    """Valida a existência dos contratos fundamentais e schemas DTO."""

    def test_core_classes_and_enums_exist(self):
        """Assegura que todas as classes, enums e estruturas de dados do Orchestrator v2.0 estão importadas."""
        assert OrchestratorV2Engine is not None, "OrchestratorV2Engine deve ser implementado"
        assert IntentCategory is not None, "IntentCategory Enum deve ser implementado"
        assert ResourceKind is not None, "ResourceKind Enum deve ser implementado"
        assert ResourceMatch is not None, "ResourceMatch dataclass deve ser implementado"
        assert FallbackRoute is not None, "FallbackRoute dataclass deve ser implementado"
        assert OrchestrationPlan is not None, "OrchestrationPlan dataclass deve ser implementado"

    def test_intent_category_has_darkfactory_domains(self):
        """Assegura os 7 domínios canônicos do DarkFactory na taxonomia de intenções."""
        expected_domains = {
            "NOLAN_STORYTELLING",
            "HISTORICAL_RESEARCH",
            "AUDIO_ENGINEERING",
            "VIDEO_SYNTHESIS_T2V",
            "CINEMA_DASHBOARD",
            "CORPORATE_ENGINEERING",
            "COMPLIANCE_AND_LEGAL",
        }
        actual_domains = {member.name for member in IntentCategory}
        assert expected_domains.issubset(actual_domains), f"Faltam domínios: {expected_domains - actual_domains}"


class TestOrchestratorV2Classification:
    """Testa o classificador semântico e inferência multivetorial de intenções."""

    @pytest.fixture
    def engine(self):
        return OrchestratorV2Engine()

    @pytest.mark.parametrize(
        "query,expected_intent",
        [
            (
                "Escreva um roteiro em 5 atos com Nolan Crosscutting e prompts Kodak Vision3 70mm",
                IntentCategory.NOLAN_STORYTELLING,
            ),
            (
                "Pesquise documentos desclassificados da CIA sobre a Guerra Fria em 1983",
                IntentCategory.HISTORICAL_RESEARCH,
            ),
            (
                "Gere a narração com CosyVoice e faça a mixagem master a -14 LUFS com Zimmer OST",
                IntentCategory.AUDIO_ENGINEERING,
            ),
            (
                "Renderize os takes no RunningHub ComfyUI com fallback MiniMax H3 e envie falhas para quarentena",
                IntentCategory.VIDEO_SYNTHESIS_T2V,
            ),
            (
                "Abra o Cinema Dashboard FastAPI na porta 8502 e verifique o cockpit de autenticação",
                IntentCategory.CINEMA_DASHBOARD,
            ),
            (
                "Execute o corp-pipeline com Shift-Left TDD para criar uma nova feature em feature branch",
                IntentCategory.CORPORATE_ENGINEERING,
            ),
            (
                "Gere o relatório de conformidade Green Dollar 100/100 e o Kit de Disputa EDSA",
                IntentCategory.COMPLIANCE_AND_LEGAL,
            ),
        ],
    )
    def test_classify_intent_accuracy(self, engine, query, expected_intent):
        """Valida que consultas típicas são classificadas com precisão e confiança mínima >= 0.75."""
        intent, confidence = engine.classify_intent(query)
        assert intent == expected_intent, f"Esperava {expected_intent}, obteve {intent} para '{query}'"
        assert confidence >= 0.75, f"Confiança insuficiente: {confidence}"


class TestOrchestratorV2AffinityScoring:
    """Valida o cálculo de afinidade e ranking multivetorial de recursos."""

    @pytest.fixture
    def engine(self):
        return OrchestratorV2Engine()

    def test_nolan_intent_routes_to_nolan_director(self, engine):
        """Para intenções de roteiro, o agente nolan-director deve ter o maior score de afinidade."""
        matches = engine.score_resources(IntentCategory.NOLAN_STORYTELLING)
        assert len(matches) > 0, "Deve retornar recursos ranqueados"
        top_match = matches[0]
        assert top_match.name == "nolan-director"
        assert top_match.kind == ResourceKind.SUBAGENT
        assert top_match.score >= 0.85
        assert "darkfactory-nolan" in [m.name for m in matches if m.kind == ResourceKind.SKILL]

    def test_corp_engineering_routes_to_corp_pipeline(self, engine):
        """Para engenharia corporativa, corp-pipeline e tdd-guide devem ser priorizados."""
        matches = engine.score_resources(IntentCategory.CORPORATE_ENGINEERING)
        agent_names = [m.name for m in matches if m.kind == ResourceKind.SUBAGENT]
        skill_names = [m.name for m in matches if m.kind == ResourceKind.SKILL]
        assert "tdd-guide" in agent_names or "architect" in agent_names
        assert "corp-pipeline" in skill_names


class TestOrchestratorV2FallbackMatrix:
    """Testa as rotas determinísticas de fallback em tempo de execução."""

    @pytest.fixture
    def engine(self):
        return OrchestratorV2Engine()

    def test_video_generation_fallbacks(self, engine):
        """Geração de vídeo deve prever fallback de Veo 3.1 para RunningHub MiniMax H3."""
        fallbacks = engine.resolve_fallbacks(IntentCategory.VIDEO_SYNTHESIS_T2V)
        assert len(fallbacks) >= 1
        video_fb = next((f for f in fallbacks if "veo" in f.primary.lower() or "google_flow" in f.primary.lower()), None)
        assert video_fb is not None, "Deve possuir fallback para gerador de vídeo primário"
        assert "minimax" in video_fb.fallback.lower() or "runninghub" in video_fb.fallback.lower()

    def test_audio_engineering_fallbacks(self, engine):
        """Geração de voz deve prever fallback silencioso de CosyVoice para Kokoro-82M."""
        fallbacks = engine.resolve_fallbacks(IntentCategory.AUDIO_ENGINEERING)
        assert len(fallbacks) >= 1
        voice_fb = next((f for f in fallbacks if "cosyvoice" in f.primary.lower()), None)
        assert voice_fb is not None
        assert "kokoro" in voice_fb.fallback.lower()


class TestOrchestratorV2PlanSynthesis:
    """Testa a síntese completa do plano de orquestração, badge e serialização DAG."""

    @pytest.fixture
    def engine(self):
        return OrchestratorV2Engine()

    def test_synthesize_orchestration_plan(self, engine):
        """Deve gerar um OrchestrationPlan completo e estruturado."""
        task_query = "Quero renderizar o ato 3 no RunningHub com som Zimmer a -14 LUFS"
        plan = engine.synthesize_plan(task_query)

        assert isinstance(plan, OrchestrationPlan)
        assert plan.intent in (IntentCategory.VIDEO_SYNTHESIS_T2V, IntentCategory.AUDIO_ENGINEERING)
        assert plan.primary_agent != ""
        assert len(plan.supporting_skills) > 0
        assert len(plan.critical_tools) > 0
        assert len(plan.execution_steps) > 0
        assert plan.operational_badge.startswith("🎯 Orquestrador:")
        assert "Skill:" in plan.operational_badge
        assert "Agente:" in plan.operational_badge
        assert "Ferramenta:" in plan.operational_badge

    def test_cli_json_serialization(self, engine):
        """O plano gerado deve ser 100% serializável em JSON para interop com ferramentas e CI/CD."""
        task_query = "Criar nova branch para corrigir bug de loudness"
        plan = engine.synthesize_plan(task_query)
        json_output = engine.plan_to_json(plan)
        data = json.loads(json_output)

        assert data["intent"] == IntentCategory.CORPORATE_ENGINEERING.value
        assert "primary_agent" in data
        assert "operational_badge" in data
        assert isinstance(data["execution_steps"], list)
