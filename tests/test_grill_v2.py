"""
Tests for grill-me-v2 (grill-v2) - Shift-Left TDD Suite
Phase 2: Red Phase (Ensures automated tests exist and fail before implementation)
"""

import os
import json
import pytest
from pathlib import Path

# Tentativa de importação dos módulos que serão desenvolvidos
try:
    from agents.skills.grill_v2.scripts.grill_analyzer import (
        GrillAnalyzer,
        CodebaseContext,
        SocraticQuestion,
        GrillSessionResult,
        ADRGenerator,
    )
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "grill-v2" / "scripts"))
        from grill_analyzer import (
            GrillAnalyzer,
            CodebaseContext,
            SocraticQuestion,
            GrillSessionResult,
            ADRGenerator,
        )
    except ImportError:
        GrillAnalyzer = None
        CodebaseContext = None
        SocraticQuestion = None
        GrillSessionResult = None
        ADRGenerator = None


class TestGrillV2Contracts:
    """Verifica os contratos e a inteligência expandida da skill grill-v2."""

    def test_modules_and_classes_must_exist(self):
        """Garante que as classes e módulos essenciais do grill-v2 estão definidos."""
        assert GrillAnalyzer is not None, "GrillAnalyzer deve estar implementado em grill_analyzer.py"
        assert CodebaseContext is not None, "CodebaseContext deve estar implementado"
        assert SocraticQuestion is not None, "SocraticQuestion deve estar implementado"
        assert GrillSessionResult is not None, "GrillSessionResult deve estar implementado"
        assert ADRGenerator is not None, "ADRGenerator deve estar implementado"

    def test_codebase_deep_grounding(self, tmp_path):
        """GrillAnalyzer deve varrer o repositório e extrair padrões e contexto preditivo."""
        # Simula workspace com arquivos e padrões
        (tmp_path / "pyproject.toml").write_text("[tool.pytest]\npython_files = 'test_*.py'", encoding="utf-8")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "models.py").write_text("class UserModel:\n    id: int\n    email: str", encoding="utf-8")

        analyzer = GrillAnalyzer(workspace_path=str(tmp_path))
        ctx = analyzer.analyze_codebase()

        assert isinstance(ctx, CodebaseContext)
        assert ctx.stack == "python"
        assert any("model" in p.lower() or "pyproject" in p.lower() for p in ctx.existing_patterns)

    def test_socratic_quadrants_question_generation(self):
        """Deve estruturar perguntas opinativas cobrindo os 4 quadrantes socráticos."""
        analyzer = GrillAnalyzer()
        demand = "Implementar upload assíncrono de vídeo com processamento de thumbnails e webhook de callback"
        questions = analyzer.formulate_socratic_inquiry(demand)

        assert len(questions) >= 4, "Deve gerar ao menos 1 pergunta por quadrante socrático"

        quadrants = {q.quadrant for q in questions}
        expected_quadrants = {"contracts", "failure_modes", "security_compliance", "pragmatism_yagni"}
        assert expected_quadrants.issubset(quadrants), f"Quadrantes faltando: {expected_quadrants - quadrants}"

        # Verifica características Staff-level em cada pergunta
        for q in questions:
            assert q.question.strip(), "Pergunta não pode ser vazia"
            assert q.opinionated_recommendation.strip(), "Deve fornecer recomendação opinativa sênior"
            assert len(q.options) >= 2, "Deve fornecer alternativas de escolha"
            assert q.tradeoffs, "Deve incluir análise explícita de trade-offs (prós/contras)"

    def test_adr_and_tdd_seed_generator(self):
        """ADRGenerator deve formatar um Architectural Decision Record executável com sementes de TDD."""
        generator = ADRGenerator()
        adr_content = generator.create_adr(
            title="Async Video Upload Architecture",
            feature_slug="video-async-upload",
            context="Usuários corporativos necessitam enviar arquivos de vídeo de até 4GB sem travar a API HTTP.",
            decisions={
                "Storage": "Upload direto para S3 via Presigned URL (Recomendado)",
                "Queue": "Redis + Celery para transcodificação assíncrona",
                "Callback": "Webhooks assinados com HMAC-SHA256"
            },
            failure_modes=[
                "Timeout de upload no cliente -> Retentativa com multipart upload",
                "Webhook receptor fora do ar -> Dead Letter Queue (DLQ) com backoff exponencial"
            ],
            tdd_scenarios=[
                "test_presigned_url_generation_rejects_unauthorized_token",
                "test_webhook_signature_verification_succeeds_with_valid_secret",
                "test_upload_failure_redirects_to_dlq"
            ]
        )

        assert "# ADR: Async Video Upload Architecture" in adr_content
        assert "## 1. Context & Business Drivers" in adr_content
        assert "## 2. The Socratic Decisions Matrix" in adr_content
        assert "## 3. Failure Modes & Resilience Architecture" in adr_content
        assert "## 4. Shift-Left TDD Seeds (Executable Specs)" in adr_content
        assert "test_presigned_url_generation_rejects_unauthorized_token" in adr_content

    def test_grill_v2_skill_and_workflow_files_exist(self):
        """Verifica se os arquivos de skill e workflow do grill-v2 estão presentes no repositório."""
        skill_path = Path(".agents/skills/grill-v2/SKILL.md")
        workflow_path = Path(".agents/workflows/grill-v2.md")
        script_path = Path(".agents/skills/grill-v2/scripts/grill_analyzer.py")

        assert skill_path.exists(), f"Skill file {skill_path} deve existir"
        assert workflow_path.exists(), f"Workflow file {workflow_path} deve existir"
        assert script_path.exists(), f"Script file {script_path} deve existir"
