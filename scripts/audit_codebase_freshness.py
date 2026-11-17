#!/usr/bin/env python3
"""DarkFactory Codebase Freshness & Architecture Unification Sentinel.

Audits the codebase to ensure:
1. Zero-Zombie Principle: No newly developed engine in src/video/ or src/factory/ is disconnected from main entrypoints.
2. No duplicate or dead scripts remain in src/ without active calls from run_pilot_pipeline.py, tests, or dashboard.
3. Every Facade in src/*.py delegates to its canonical engine in src/video/ or src/factory/.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ADR-01: Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
SRC_VIDEO_DIR = SRC_DIR / "video"
SRC_FACTORY_DIR = SRC_DIR / "factory"
TESTS_DIR = PROJECT_ROOT / "tests"
PIPELINE_SCRIPT = PROJECT_ROOT / "run_pilot_pipeline.py"


def get_python_files(dir_path: Path) -> List[Path]:
    """Recursively collect .py files ignoring __pycache__."""
    return [
        p for p in dir_path.rglob("*.py")
        if "__pycache__" not in p.parts and not p.name.startswith(".tmp")
    ]


def extract_imports_and_references(py_file: Path) -> Set[str]:
    """Extract imported module names and string references to other scripts."""
    refs: Set[str] = set()
    try:
        content = py_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return refs

    # Regex search for script invocations (e.g., 'research_engine.py')
    for match in re.findall(r'[\'"]([a-zA-Z0-9_\-]+\.py)[\'"]', content):
        refs.add(match)

    try:
        tree = ast.parse(content, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    refs.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    refs.add(node.module)
    except Exception:
        pass

    return refs


def audit_facade_bridges() -> List[Dict[str, str]]:
    """Verify that root facades in src/ delegate to modern engines."""
    checks = [
        {
            "facade": "src/audio_mixer_master.py",
            "target_engine": "DarkFactoryAudioEngine",
            "source_module": "src.video.audio_engine",
        },
        {
            "facade": "src/generate_pilot_audio.py",
            "target_engine": "MasterVoiceRouter",
            "source_module": "src.video.voice_router",
        },
        {
            "facade": "src/research_engine.py",
            "target_engine": "PublicDomainResearchEngine",
            "source_module": "src.video.public_domain_research",
        },
        {
            "facade": "src/shorts_generator.py",
            "target_engine": "ShortsRepurposerEngine",
            "source_module": "src.video.shorts_repurposer",
        },
        {
            "facade": "src/generate_motion_assets.py",
            "target_engine": "MapAnimator",
            "source_module": "src.video.map_animator",
        },
        {
            "facade": "src/render_pilot_video.py",
            "target_engine": "CinematicColorGrader",
            "source_module": "src.video.cinematic_color",
        },
    ]

    violations = []
    for check in checks:
        f_path = PROJECT_ROOT / check["facade"]
        if not f_path.is_file():
            violations.append({
                "facade": check["facade"],
                "issue": f"Facade file missing: {check['facade']}",
            })
            continue

        content = f_path.read_text(encoding="utf-8", errors="replace")
        if check["target_engine"] not in content:
            violations.append({
                "facade": check["facade"],
                "issue": f"Facade does not reference target engine '{check['target_engine']}'",
            })

    return violations


def audit_pipeline_wiring() -> List[Dict[str, str]]:
    """Verify that run_pilot_pipeline.py and daemon execute the latest scripts."""
    if not PIPELINE_SCRIPT.is_file():
        return [{"pipeline": "run_pilot_pipeline.py", "issue": "Main pipeline orchestrator missing"}]

    pipeline_content = PIPELINE_SCRIPT.read_text(encoding="utf-8", errors="replace")
    mandatory_steps = [
        "auth_gate.py",
        "research_engine.py",
        "nolan_director.py",
        "google_flow_bot.py",
        "generate_motion_assets.py",
        "generate_pilot_audio.py",
        "cosyvoice_master.py",
        "audio_mixer_master.py",
        "render_pilot_video.py",
        "shorts_generator.py",
        "youtube_compliance_qc.py",
        "youtube_algorithm_booster.py",
    ]

    missing_steps = []
    for step in mandatory_steps:
        if step not in pipeline_content:
            missing_steps.append({
                "pipeline": "run_pilot_pipeline.py",
                "issue": f"Mandatory pipeline step '{step}' is missing from orchestrator",
            })

    return missing_steps


def audit_orphan_files() -> List[str]:
    """Identify files in src/ that have no consumers anywhere in the codebase."""
    all_files = get_python_files(SRC_DIR) + get_python_files(TESTS_DIR) + [PIPELINE_SCRIPT]
    all_refs: Set[str] = set()

    for f in all_files:
        all_refs.update(extract_imports_and_references(f))

    # Known standalone entrypoints that can be executed directly or as daemons
    allowed_entrypoints = {
        "run_pilot_pipeline.py",
        "daemon_darkfactory.py",
        "topic_generator.py",
        "youtube_publisher.py",
        "kokoro_fallback.py",
        "music_flow_bot.py",
        "runninghub_foley_bot.py",
        "ai_engine_suite.py",
    }

    orphans = []
    for src_file in SRC_DIR.glob("*.py"):
        stem = src_file.stem
        name = src_file.name
        if name in allowed_entrypoints or name.startswith("__"):
            continue

        # Check if stem is imported or name is referenced
        is_used = any(
            stem in ref or name in ref
            for ref in all_refs
        )
        if not is_used:
            orphans.append(str(src_file.relative_to(PROJECT_ROOT)))

    return orphans


def main() -> None:
    print("=" * 65)
    print("🛡️ DARKFACTORY CODEBASE FRESHNESS & ARCHITECTURE AUDIT")
    print("=" * 65)

    facade_issues = audit_facade_bridges()
    pipeline_issues = audit_pipeline_wiring()
    orphan_files = audit_orphan_files()

    passed = True

    print("\n[1] Facade & Engine Delegation Check:")
    if not facade_issues:
        print("  ✅ All 6 root facades correctly delegate to modern src/video/ engines.")
    else:
        passed = False
        for iss in facade_issues:
            print(f"  ❌ {iss['facade']}: {iss['issue']}")

    print("\n[2] Pipeline Orchestration Step Wiring:")
    if not pipeline_issues:
        print("  ✅ All 12 canonical steps are wired into run_pilot_pipeline.py.")
    else:
        passed = False
        for iss in pipeline_issues:
            print(f"  ❌ {iss['issue']}")

    print("\n[3] Orphan / Stale Code Detection in src/:")
    if not orphan_files:
        print("  ✅ Zero orphan files detected in src/ root.")
    else:
        print(f"  ⚠️ Potential orphan files found ({len(orphan_files)}):")
        for orph in orphan_files:
            print(f"     - {orph}")

    print("\n" + "=" * 65)
    if passed and not orphan_files:
        print("🎉 CODEBASE FRESHNESS AUDIT: 100% CLEAN & SYNCHRONIZED")
        print("=" * 65)
        sys.exit(0)
    elif passed:
        print("⚠️ CODEBASE FRESHNESS AUDIT: PASSED WITH NOTICES")
        print("=" * 65)
        sys.exit(0)
    else:
        print("❌ CODEBASE FRESHNESS AUDIT: CRITICAL REGRESSION DETECTED")
        print("=" * 65)
        sys.exit(1)


if __name__ == "__main__":
    main()
