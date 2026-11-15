import pytest
from pathlib import Path
from src.ai_engine_suite import DarkFactoryAITester


def test_tester_auth_status_structure():
    tester = DarkFactoryAITester(dry_run=True)
    status = tester.check_engine_auth_status()
    assert "google_flow_video" in status
    assert "google_flow_image" in status
    assert "google_flow_music" in status
    assert "runninghub_minimax_h3" in status
    assert "runninghub_minimax_music" in status
    assert "runninghub_cosyvoice" in status


def test_dry_run_all_engines(tmp_path: Path):
    tester = DarkFactoryAITester(output_dir=tmp_path, dry_run=True)
    res = tester.run_all()
    results = res["engine_results"]

    assert results["google_flow_video"]["status"] == "success"
    assert results["google_flow_image"]["status"] == "success"
    assert results["google_flow_music"]["status"] == "success"
    assert results["runninghub_minimax_h3"]["status"] == "success"
    assert results["runninghub_minimax_music"]["status"] == "success"
    assert results["runninghub_cosyvoice"]["status"] == "success"
    assert results["foley_sfx_library"]["status"] == "success"

    assert (tmp_path / "ai_engines_test_report.json").exists()
