"""
Plan-v2 Engine (Corporate Autonomous Planner)
Computes blast-radius, topological execution DAG, expand/contract strategies,
and produces executable TDD-seeded markdown plans for enterprise environments.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass
class BlastRadiusReport:
    target_files: List[str]
    impacted_dependents: List[str] = field(default_factory=list)
    risk_score: int = 1
    complexity_tier: str = "Small"


@dataclass
class DAGTask:
    id: str
    title: str
    dependencies: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    validation_cmd: str = "pytest"
    rollback_action: str = "git checkout HEAD -- ."


@dataclass
class ExecutionPlanDAG:
    feature_slug: str
    summary: str
    blast_radius: BlastRadiusReport
    tasks: List[DAGTask]
    tdd_contract_seeds: List[str] = field(default_factory=list)
    expand_contract_strategy: Optional[str] = None
    plan_markdown: str = ""


class PlanV2Engine:
    """Motor de Planejamento Avançado com Análise de Impacto e Grafo DAG."""

    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)

    def analyze_blast_radius(self, target_files: List[str]) -> BlastRadiusReport:
        """Mapeia os arquivos consumidores e calcula o score de impacto no workspace."""
        impacted: Set[str] = set()

        for target in target_files:
            stem = Path(target).stem
            # Procura referências no workspace
            for root, dirs, files in os.walk(self.workspace):
                dirs[:] = [d for d in dirs if d not in {".git", ".pytest_cache", "venv", "node_modules", "__pycache__"}]
                for file_name in files:
                    full_path = Path(root) / file_name
                    # Não analisa o próprio arquivo alvo
                    try:
                        rel_path = str(full_path.relative_to(self.workspace)).replace("\\", "/")
                    except Exception:
                        rel_path = str(full_path).replace("\\", "/")

                    if rel_path in target_files or full_path.suffix not in {".py", ".ts", ".js", ".go", ".json"}:
                        continue

                    try:
                        content = full_path.read_text(encoding="utf-8", errors="ignore")
                        if stem in content:
                            impacted.add(rel_path)
                    except Exception:
                        pass

        impacted_list = sorted(list(impacted))
        raw_score = max(1, len(impacted_list) * 2 + len(target_files))
        risk_score = min(10, raw_score)

        if risk_score <= 2:
            tier = "Small"
        elif risk_score <= 5:
            tier = "Medium"
        elif risk_score <= 8:
            tier = "High"
        else:
            tier = "Critical-Systemic"

        return BlastRadiusReport(
            target_files=target_files,
            impacted_dependents=impacted_list,
            risk_score=risk_score,
            complexity_tier=tier
        )

    def topological_sort_tasks(self, tasks: List[DAGTask]) -> List[DAGTask]:
        """Ordena as tarefas do plano topologicamente de acordo com suas dependências."""
        task_map = {t.id: t for t in tasks}
        in_degree = {t.id: 0 for t in tasks}
        adj: Dict[str, List[str]] = {t.id: [] for t in tasks}

        for t in tasks:
            for dep in t.dependencies:
                if dep in adj:
                    adj[dep].append(t.id)
                    in_degree[t.id] += 1

        queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
        ordered = []

        while queue:
            curr = queue.pop(0)
            ordered.append(task_map[curr])
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(tasks):
            # Fallback seguro caso haja dependência circular
            return tasks

        return ordered

    def generate_plan_markdown(self, plan: ExecutionPlanDAG) -> str:
        """Gera o documento do plano estruturado nos 5 pilares de engenharia corporativa."""
        target_files_str = "\n".join(f"- `{f}`" for f in plan.blast_radius.target_files)
        impacted_str = "\n".join(f"- ⚠️ `{f}`" for f in plan.blast_radius.impacted_dependents) or "- Nenhum consumidor externo detectado (módulo isolado)."

        tasks_formatted = []
        for i, t in enumerate(plan.tasks, 1):
            deps = ", ".join(f"`{d}`" for d in t.dependencies) if t.dependencies else "Nenhuma (Execução Imediata)"
            tasks_formatted.append(f"""### Tarefa {i}: {t.title} (`{t.id}`)
- **Componentes**: {', '.join(f'`{c}`' for c in t.affected_components)}
- **Dependências Pré-Requisito**: {deps}
- **Validação Automatizada**: `{t.validation_cmd}`
- **Ação de Rollback**: `{t.rollback_action}`
""")

        tasks_str = "\n".join(tasks_formatted)
        tdd_str = "\n".join(f"- [ ] `{seed}`" for seed in plan.tdd_contract_seeds)
        expand_contract_str = plan.expand_contract_strategy or "N/A (Alteração sem quebra de compatibilidade em banco/API)."

        return f"""# Corporate Implementation Plan (DAG): {plan.feature_slug}

> **Complexity Tier**: `{plan.blast_radius.complexity_tier}` (Risk Score: {plan.blast_radius.risk_score}/10)  
> **Framework**: Corporate 5-Phase Engineering Pipeline  
> **Status**: Pronto para Fase 2 (Shift-Left TDD)

---

## 1. Blast Radius & System Impact Analysis
**Arquivos Alvo**:
{target_files_str}

**Consumidores Impactados (Blast Radius)**:
{impacted_str}

---

## 2. Dependency Graph & Execution DAG
{tasks_str}

---

## 3. Zero-Downtime & Expand/Contract Strategy
{expand_contract_str}

---

## 4. Shift-Left TDD Contracts Matrix
{tdd_str}

---

## 5. Rollback & Disaster Recovery Procedures
Para cada tarefa com falha irremediável:
- Reverta o componente afetado usando a respectiva ação de rollback definida acima.
- Nenhuma alteração incompleta deve permanecer em estado bloqueante no working tree.
"""
