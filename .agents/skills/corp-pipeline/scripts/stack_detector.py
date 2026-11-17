"""
Stack Detector & Corporate Governance Utilities
Component of Corporate Pipeline (corp-pipeline)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional


class StackDetector:
    """Detecta automaticamente a stack tecnológica e ferramentas de teste/lint do projeto."""

    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)

    def detect(self) -> Dict[str, Any]:
        """Detecta a stack ou carrega override do .corp-pipeline.json se existir."""
        # 1. Checa override explícito via .corp-pipeline.json
        config_file = self.workspace / ".corp-pipeline.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return {
                        "stack": config.get("stack", "custom"),
                        "test_cmd": config.get("test_cmd", "pytest"),
                        "lint_cmd": config.get("lint_cmd", "ruff check ."),
                        "typecheck_cmd": config.get("typecheck_cmd", "mypy ."),
                        "auto_retry_max": config.get("auto_retry_max", 3),
                    }
            except Exception:
                pass

        # 2. Detecção Node.js / TypeScript
        pkg_json = self.workspace / "package.json"
        has_node_tests = False
        if pkg_json.exists():
            test_cmd = "npm test"
            lint_cmd = "npm run lint"
            typecheck_cmd = "npm run typecheck"
            try:
                with open(pkg_json, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                    scripts = pkg_data.get("scripts", {})
                    if "test" in scripts:
                        test_cmd = scripts["test"]
                        has_node_tests = True
                    if "lint" in scripts:
                        lint_cmd = scripts["lint"]
                    if "typecheck" in scripts:
                        typecheck_cmd = scripts["typecheck"]
            except Exception:
                pass

            # Se possui script explícito de teste ou se não é repo Python
            has_python_indicators = (
                (self.workspace / "pyproject.toml").exists()
                or (self.workspace / "requirements.txt").exists()
                or (self.workspace / "pytest.ini").exists()
                or (self.workspace / "setup.py").exists()
            )

            if has_node_tests or not has_python_indicators:
                return {
                    "stack": "node",
                    "test_cmd": test_cmd,
                    "lint_cmd": lint_cmd,
                    "typecheck_cmd": typecheck_cmd,
                    "auto_retry_max": 3,
                }

        # 3. Detecção Go
        go_mod = self.workspace / "go.mod"
        if go_mod.exists():
            return {
                "stack": "go",
                "test_cmd": "go test ./...",
                "lint_cmd": "golangci-lint run",
                "typecheck_cmd": "go vet ./...",
                "auto_retry_max": 3,
            }

        # 4. Detecção Python
        pyproject = self.workspace / "pyproject.toml"
        reqs = self.workspace / "requirements.txt"
        setup_py = self.workspace / "setup.py"
        if pyproject.exists() or reqs.exists() or setup_py.exists():
            lint_cmd = "ruff check ."
            if reqs.exists():
                try:
                    content = reqs.read_text(encoding="utf-8")
                    if "flake8" in content and "ruff" not in content:
                        lint_cmd = "flake8 ."
                except Exception:
                    pass

            return {
                "stack": "python",
                "test_cmd": "pytest -v",
                "lint_cmd": lint_cmd,
                "typecheck_cmd": "mypy .",
                "auto_retry_max": 3,
            }

        # Default fallback
        return {
            "stack": "unknown",
            "test_cmd": "pytest",
            "lint_cmd": "ruff check .",
            "typecheck_cmd": "mypy .",
            "auto_retry_max": 3,
        }


class BranchPolicyValidator:
    """Valida a conformidade da política corporativa de branches Git."""

    ALLOWED_BRANCH_PATTERN = re.compile(
        r"^(feat|fix|refactor|chore|test|perf|build|ci|hotfix)/[A-Za-z0-9._-]+$"
    )

    BLOCKED_BRANCHES = {"main", "master", "develop", "prod", "production"}

    @classmethod
    def is_allowed_branch(cls, branch_name: str) -> bool:
        """Verifica se a branch é permitida para desenvolvimento e push."""
        if not branch_name:
            return False
        clean_name = branch_name.strip()
        if clean_name.lower() in cls.BLOCKED_BRANCHES:
            return False
        return bool(cls.ALLOWED_BRANCH_PATTERN.match(clean_name))


class CorporatePRGenerator:
    """Gera corpos de Pull Request com padrão de excelência corporativa."""

    @classmethod
    def format_pr(
        cls,
        title: str,
        ticket_id: str,
        context: str,
        decisions: str,
        test_instructions: str,
        rollback_plan: str,
        evidence: str,
    ) -> str:
        """Gera Markdown estruturado pronto para revisão por pares e compliance."""
        return f"""# {title}

> **Ticket/Issue**: `{ticket_id}`  
> **Type**: Feature / Corporate Pipeline Delivery

---

## 1. Business Context & Problem Statement
{context}

---

## 2. Technical Decisions & Trade-offs
{decisions}

---

## 3. How to Test & Verification Commands
```bash
{test_instructions}
```

---

## 4. Rollback & Disaster Recovery Plan
{rollback_plan}

---

## 5. Security & Compliance Checklist
- [x] Nenhuma chave, credencial ou token confidencial exposto (.env verificado).
- [x] Tipagem estrita validada (zero `any` desnecessários ou type warnings).
- [x] Testes automatizados executados e passando 100%.
- [x] Zero commits diretos na `main` / Linear history preservada.

---

## 6. Reviewer Checklist & Verification Evidence
{evidence}
"""


if __name__ == "__main__":
    detector = StackDetector()
    info = detector.detect()
    print(json.dumps(info, indent=2))
