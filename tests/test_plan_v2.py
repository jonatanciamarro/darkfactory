"""
Tests for plan-v2 (Corporate Autonomous Planner) - Shift-Left TDD Suite
Phase 2: Red Phase (Ensures automated tests exist and fail before implementation)
"""

import os
import json
import pytest
from pathlib import Path

# Tentativa de importação dos módulos que serão desenvolvidos
try:
    from agents.skills.plan_v2.scripts.plan_engine import (
        PlanV2Engine,
        BlastRadiusReport,
        DAGTask,
        ExecutionPlanDAG,
    )
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "plan-v2" / "scripts"))
        from plan_engine import (
            PlanV2Engine,
            BlastRadiusReport,
            DAGTask,
            ExecutionPlanDAG,
        )
    except ImportError:
        PlanV2Engine = None
        BlastRadiusReport = None
        DAGTask = None
        ExecutionPlanDAG = None


class TestPlanV2Contracts:
    """Verifica os contratos e a inteligência expandida da skill plan-v2."""

    def test_modules_and_classes_must_exist(self):
        """Garante que as classes e módulos essenciais do plan-v2 estão definidos."""
        assert PlanV2Engine is not None, "PlanV2Engine deve estar implementado em plan_engine.py"
        assert BlastRadiusReport is not None, "BlastRadiusReport deve estar implementado"
        assert DAGTask is not None, "DAGTask deve estar implementado"
        assert ExecutionPlanDAG is not None, "ExecutionPlanDAG deve estar implementado"

    def test_blast_radius_impact_calculation(self, tmp_path):
        """PlanV2Engine deve calcular o raio de impacto mapeando arquivos dependentes no workspace."""
        # Cria módulo central
        src = tmp_path / "src"
        src.mkdir()
        core_file = src / "auth_core.py"
        core_file.write_text("def verify_jwt(): pass", encoding="utf-8")

        # Cria consumidores do módulo
        consumer_a = src / "api_routes.py"
        consumer_a.write_text("import auth_core\nfrom auth_core import verify_jwt", encoding="utf-8")

        consumer_b = src / "webhook_service.py"
        consumer_b.write_text("from auth_core import verify_jwt", encoding="utf-8")

        engine = PlanV2Engine(workspace_path=str(tmp_path))
        report = engine.analyze_blast_radius(target_files=["src/auth_core.py"])

        assert isinstance(report, BlastRadiusReport)
        assert len(report.impacted_dependents) >= 2, "Deve identificar os 2 arquivos consumidores"
        assert report.risk_score >= 5, "Módulo com múltiplos consumidores deve ter score de risco moderado/alto"
        assert report.complexity_tier in ["Small", "Medium", "High", "Critical-Systemic"]

    def test_dag_topological_sort_and_validation(self):
        """PlanV2Engine deve ordenar tarefas em DAG respeitando pré-requisitos e rollback."""
        engine = PlanV2Engine()

        raw_tasks = [
            DAGTask(
                id="task-3",
                title="Integrar rotas da API",
                dependencies=["task-2"],
                affected_components=["api_routes.py"],
                validation_cmd="pytest tests/test_routes.py",
                rollback_action="git checkout HEAD -- api_routes.py"
            ),
            DAGTask(
                id="task-1",
                title="Criar DTOs e Schemas Pydantic",
                dependencies=[],
                affected_components=["schemas.py"],
                validation_cmd="pytest tests/test_schemas.py",
                rollback_action="rm schemas.py"
            ),
            DAGTask(
                id="task-2",
                title="Implementar Service Layer",
                dependencies=["task-1"],
                affected_components=["service.py"],
                validation_cmd="pytest tests/test_service.py",
                rollback_action="git checkout HEAD -- service.py"
            ),
        ]

        ordered_tasks = engine.topological_sort_tasks(raw_tasks)
        task_ids = [t.id for t in ordered_tasks]

        # Ordem topológica estrita: task-1 -> task-2 -> task-3
        assert task_ids == ["task-1", "task-2", "task-3"], f"Ordem DAG incorreta: {task_ids}"

    def test_plan_markdown_generation_with_senior_sections(self):
        """Gera o plano em Markdown contendo as 5 seções executivas corporativas."""
        engine = PlanV2Engine()
        blast_report = BlastRadiusReport(
            target_files=["src/database.py"],
            impacted_dependents=["src/user_repo.py", "src/order_repo.py"],
            risk_score=7,
            complexity_tier="High"
        )
        task = DAGTask(
            id="task-db-1",
            title="Adicionar coluna nullable 'refresh_hash' (Expand Phase)",
            dependencies=[],
            affected_components=["src/database.py"],
            validation_cmd="pytest tests/test_db_migration.py",
            rollback_action="alembic downgrade -1"
        )
        plan_dag = ExecutionPlanDAG(
            feature_slug="db-refresh-token",
            summary="Migração zero-downtime para suporte a refresh token com hash criptográfico.",
            blast_radius=blast_report,
            tasks=[task],
            tdd_contract_seeds=["test_migration_adds_column_without_table_lock"],
            expand_contract_strategy="Phase 1: Add column nullable. Phase 2: Dual-write. Phase 3: Contract."
        )

        md = engine.generate_plan_markdown(plan_dag)

        assert "# Corporate Implementation Plan (DAG): db-refresh-token" in md
        assert "## 1. Blast Radius & System Impact Analysis" in md
        assert "## 2. Dependency Graph & Execution DAG" in md
        assert "## 3. Zero-Downtime & Expand/Contract Strategy" in md
        assert "## 4. Shift-Left TDD Contracts Matrix" in md
        assert "## 5. Rollback & Disaster Recovery Procedures" in md
        assert "alembic downgrade -1" in md

    def test_plan_v2_skill_and_workflow_files_exist(self):
        """Verifica se os arquivos da skill e workflow do plan-v2 existem fisicamente."""
        skill_path = Path(".agents/skills/plan-v2/SKILL.md")
        workflow_path = Path(".agents/workflows/plan-v2.md")
        script_path = Path(".agents/skills/plan-v2/scripts/plan_engine.py")

        assert skill_path.exists(), f"Skill file {skill_path} deve existir"
        assert workflow_path.exists(), f"Workflow file {workflow_path} deve existir"
        assert script_path.exists(), f"Script file {script_path} deve existir"
