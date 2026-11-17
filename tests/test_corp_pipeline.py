"""
Tests for Corporate Pipeline (corp-pipeline) - Shift-Left TDD Suite
Phase 2: Red Phase (Ensures automated tests exist and fail before implementation)
"""

import os
import json
import pytest
from pathlib import Path

# Tentativa de importação dos módulos que serão desenvolvidos
try:
    from agents.skills.corp_pipeline.scripts.stack_detector import (
        StackDetector,
        CorporatePRGenerator,
        BranchPolicyValidator,
    )
except ImportError:
    # Fallback para permitir teste direto via caminho relativo durante desenvolvimento
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "corp-pipeline" / "scripts"))
        from stack_detector import (
            StackDetector,
            CorporatePRGenerator,
            BranchPolicyValidator,
        )
    except ImportError:
        StackDetector = None
        CorporatePRGenerator = None
        BranchPolicyValidator = None


class TestCorporatePipelineContracts:
    """Verifica os contratos fundamentais da esteira corporativa."""

    def test_modules_must_exist(self):
        """Garante que as classes e módulos essenciais foram criados."""
        assert StackDetector is not None, "StackDetector deve estar implementado em stack_detector.py"
        assert CorporatePRGenerator is not None, "CorporatePRGenerator deve estar implementado"
        assert BranchPolicyValidator is not None, "BranchPolicyValidator deve estar implementado"

    def test_detect_python_stack(self, tmp_path):
        """Deve detectar corretamente projeto Python (pytest, ruff/flake8, mypy)."""
        # Simula workspace Python
        (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\npython_files = 'test_*.py'", encoding="utf-8")
        (tmp_path / "requirements.txt").write_text("pytest\nruff\nmypy", encoding="utf-8")

        detector = StackDetector(workspace_path=str(tmp_path))
        info = detector.detect()

        assert info["stack"] == "python"
        assert "pytest" in info["test_cmd"]
        assert "ruff" in info["lint_cmd"] or "flake8" in info["lint_cmd"]
        assert "mypy" in info["typecheck_cmd"]

    def test_detect_node_stack(self, tmp_path):
        """Deve detectar projeto Node.js / TypeScript com npm/vitest/jest."""
        pkg = {
            "name": "corp-service",
            "scripts": {
                "test": "vitest run",
                "lint": "eslint .",
                "typecheck": "tsc --noEmit"
            }
        }
        (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

        detector = StackDetector(workspace_path=str(tmp_path))
        info = detector.detect()

        assert info["stack"] == "node"
        assert "vitest" in info["test_cmd"] or "npm test" in info["test_cmd"]
        assert "eslint" in info["lint_cmd"] or "npm run lint" in info["lint_cmd"]
        assert "tsc" in info["typecheck_cmd"] or "npm run typecheck" in info["typecheck_cmd"]

    def test_detect_go_stack(self, tmp_path):
        """Deve detectar projeto Go com go test e golangci-lint."""
        (tmp_path / "go.mod").write_text("module example.com/corp/service\n\ngo 1.22", encoding="utf-8")

        detector = StackDetector(workspace_path=str(tmp_path))
        info = detector.detect()

        assert info["stack"] == "go"
        assert "go test" in info["test_cmd"]
        assert "golangci-lint" in info["lint_cmd"]

    def test_config_override_takes_precedence(self, tmp_path):
        """Arquivo .corp-pipeline.json deve sobrescrever a detecção automática."""
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        custom_config = {
            "stack": "custom-polyglot",
            "test_cmd": "make test-all",
            "lint_cmd": "make lint-strict",
            "typecheck_cmd": "make typecheck",
            "auto_retry_max": 3
        }
        (tmp_path / ".corp-pipeline.json").write_text(json.dumps(custom_config), encoding="utf-8")

        detector = StackDetector(workspace_path=str(tmp_path))
        info = detector.detect()

        assert info["stack"] == "custom-polyglot"
        assert info["test_cmd"] == "make test-all"
        assert info["lint_cmd"] == "make lint-strict"
        assert info["auto_retry_max"] == 3

    def test_branch_policy_blocks_direct_main_or_master(self):
        """BranchPolicyValidator deve rejeitar 'main' ou 'master' para push direto."""
        validator = BranchPolicyValidator()
        assert not validator.is_allowed_branch("main"), "Push direto na 'main' deve ser terminantemente proibido!"
        assert not validator.is_allowed_branch("master"), "Push direto na 'master' deve ser terminantemente proibido!"

    def test_branch_policy_validates_feature_branch_pattern(self):
        """BranchPolicyValidator deve validar padrões corporativos convencionais."""
        validator = BranchPolicyValidator()
        assert validator.is_allowed_branch("feat/JIRA-123-user-auth")
        assert validator.is_allowed_branch("fix/BUG-999-null-pointer")
        assert validator.is_allowed_branch("refactor/CORE-42-cleanup")
        assert not validator.is_allowed_branch("random-branch-without-prefix")
        assert not validator.is_allowed_branch("my_branch")

    def test_corporate_pr_generator_contains_all_senior_sections(self):
        """Gerador de PR corporativo deve conter seções mandatórias de engenharia."""
        generator = CorporatePRGenerator()
        pr_markdown = generator.format_pr(
            title="feat(auth): add secure http-only refresh cookie",
            ticket_id="JIRA-402",
            context="Usuários estavam enfrentando deslogamento indevido.",
            decisions="Optado por cookie SameSite=Strict com HMAC SHA-256.",
            test_instructions="pytest -v tests/test_auth.py",
            rollback_plan="Reverter commit e invalidar chaves de sessão no Redis.",
            evidence="12 testes passando sem regressões."
        )

        assert "## 1. Business Context & Problem Statement" in pr_markdown
        assert "## 2. Technical Decisions & Trade-offs" in pr_markdown
        assert "## 3. How to Test & Verification Commands" in pr_markdown
        assert "## 4. Rollback & Disaster Recovery Plan" in pr_markdown
        assert "## 5. Security & Compliance Checklist" in pr_markdown
        assert "JIRA-402" in pr_markdown

    def test_skill_and_workflow_files_exist(self):
        """Verifica se os arquivos da skill e workflow estão fisicamente presentes."""
        skill_path = Path(".agents/skills/corp-pipeline/SKILL.md")
        workflow_path = Path(".agents/workflows/corp-pipeline.md")
        template_path = Path(".agents/skills/corp-pipeline/templates/pr_template.md")

        assert skill_path.exists(), f"Skill file {skill_path} deve existir"
        assert workflow_path.exists(), f"Workflow file {workflow_path} deve existir"
        assert template_path.exists(), f"Template file {template_path} deve existir"
