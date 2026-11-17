"""
Tests for orchestrator-v2 (Master Dynamic Orchestrator) - Shift-Left TDD Suite
Phase 2: Red Phase (Ensures automated tests exist and fail before implementation)
"""

import os
import json
import pytest
from pathlib import Path

# Tentativa de importação dos módulos que serão desenvolvidos
try:
    from agents.skills.orchestrator_v2.scripts.orchestrator_engine import (
        OrchestratorV2Engine,
        AssetCapability,
        OrchestrationChain,
        OrchestrationDecision,
    )
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "orchestrator-v2" / "scripts"))
        from orchestrator_engine import (
            OrchestratorV2Engine,
            AssetCapability,
            OrchestrationChain,
            OrchestrationDecision,
        )
    except ImportError:
        OrchestratorV2Engine = None
        AssetCapability = None
        OrchestrationChain = None
        OrchestrationDecision = None


class TestOrchestratorV2Contracts:
    """Verifica os contratos e a inteligência expandida da skill orchestrator-v2."""

    def test_modules_and_classes_must_exist(self):
        """Garante que as classes e módulos essenciais do orchestrator-v2 estão definidos."""
        assert OrchestratorV2Engine is not None, "OrchestratorV2Engine deve estar implementado em orchestrator_engine.py"
        assert AssetCapability is not None, "AssetCapability deve estar implementado"
        assert OrchestrationChain is not None, "OrchestrationChain deve estar implementado"
        assert OrchestrationDecision is not None, "OrchestrationDecision deve estar implementado"

    def test_dynamic_affinity_scoring(self):
        """OrchestratorV2Engine deve calcular afinidade semântica para selecionar o melhor recurso."""
        engine = OrchestratorV2Engine()

        assets = [
            AssetCapability(name="grill-v2", kind="skill", capabilities=["socratic", "interview", "scope", "contracts"]),
            AssetCapability(name="plan-v2", kind="skill", capabilities=["dag", "blast-radius", "planning", "dependencies"]),
            AssetCapability(name="tdd-guide", kind="subagent", capabilities=["tests", "pytest", "unit", "tdd", "red-green"]),
            AssetCapability(name="security-reviewer", kind="subagent", capabilities=["secrets", "owasp", "tokens", "vulnerability"]),
        ]

        best_asset = engine.calculate_best_asset("preciso escrever testes unitários em pytest com tdd", assets)
        assert best_asset.name == "tdd-guide"
        assert best_asset.affinity_score > 0.5, f"Score de afinidade muito baixo: {best_asset.affinity_score}"

        best_plan = engine.calculate_best_asset("planejar grafo dag de dependências e blast radius", assets)
        assert best_plan.name == "plan-v2"

    def test_staged_pipeline_chain_composition(self):
        """OrchestratorV2Engine deve compor cadeias de execução em estágios para demandas complexas."""
        engine = OrchestratorV2Engine()
        chain = engine.compose_pipeline_chain("Nova feature corporativa de checkout com pagamento e webhook")

        assert isinstance(chain, OrchestrationChain)
        assert chain.execution_mode == "staged_pipeline"
        assert "grill-v2" in chain.stages, "Demanda complexa deve iniciar com alinhamento socrático (grill-v2)"
        assert "plan-v2" in chain.stages, "Demanda complexa deve planejar o grafo DAG (plan-v2)"
        assert "corp-pipeline" in chain.stages, "Demanda complexa deve executar sob o corp-pipeline"

    def test_circuit_breaker_and_fallback_routing(self):
        """OrchestratorV2Engine deve comutar automaticamente para fallback em caso de degradação/quota."""
        engine = OrchestratorV2Engine()

        # Rota normal
        normal_route = engine.resolve_route_with_fallback(primary_asset="cosyvoice", is_degraded=False)
        assert normal_route == "cosyvoice"

        # Rota sob degradação ou limite de quota
        fallback_route = engine.resolve_route_with_fallback(primary_asset="cosyvoice", is_degraded=True)
        assert fallback_route in ["kokoro-voice", "inline-resilient"], f"Fallback incorreto: {fallback_route}"

    def test_orchestration_decision_and_telemetry_badge(self):
        """OrchestratorV2Engine deve gerar a decisão completa com badge de telemetria e checklist DoD."""
        engine = OrchestratorV2Engine()
        decision = engine.decide_orchestration("Refatorar módulo de vídeo com testes automatizados e segurança")

        assert isinstance(decision, OrchestrationDecision)
        assert decision.telemetry_badge.startswith("🎯 Orquestrador v2:"), "Badge deve ter o prefixo da v2"
        assert len(decision.dod_checklist) >= 3, "Deve incluir ao menos 3 critérios de Definition of Done (DoD)"
        assert any("teste" in item.lower() or "tdd" in item.lower() for item in decision.dod_checklist)

    def test_orchestrator_v2_skill_and_workflow_files_exist(self):
        """Verifica se os arquivos da skill e workflow do orchestrator-v2 existem fisicamente."""
        skill_path = Path(".agents/skills/orchestrator-v2/SKILL.md")
        workflow_path = Path(".agents/workflows/orchestrator-v2.md")
        script_path = Path(".agents/skills/orchestrator-v2/scripts/orchestrator_engine.py")

        assert skill_path.exists(), f"Skill file {skill_path} deve existir"
        assert workflow_path.exists(), f"Workflow file {workflow_path} deve existir"
        assert script_path.exists(), f"Script file {script_path} deve existir"
