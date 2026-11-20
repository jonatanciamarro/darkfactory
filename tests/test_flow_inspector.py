"""Unit tests for Google Flow Scene Inspector (Shift-Left TDD)."""
import pytest
from pathlib import Path
from src.video.flow_inspector import (
    FlowShotType,
    FlowSceneStatus,
    FlowSceneItemDTO,
    FlowInspectionReportDTO,
    GoogleFlowInspector,
)

def test_flow_scene_item_dto_creation():
    item = FlowSceneItemDTO(
        scene_id=1,
        shot_type=FlowShotType.SHOT_A,
        title_or_prompt="Stanislav Petrov portrait",
        status=FlowSceneStatus.READY,
        card_id="card-001",
        video_stream_url="https://stream.example.com/video1.mp4",
        file_size_bytes=4500000,
    )
    assert item.scene_id == 1
    assert item.shot_type == FlowShotType.SHOT_A
    assert item.status == FlowSceneStatus.READY
    assert item.file_size_bytes == 4500000

def test_flow_inspection_report_dto_reconciliation():
    item1 = FlowSceneItemDTO(
        scene_id=1,
        shot_type=FlowShotType.SHOT_A,
        title_or_prompt="Stanislav Petrov portrait",
        status=FlowSceneStatus.LOCAL_SYNCED,
        local_path=Path("data/broll/cena 1.mp4"),
    )
    item2 = FlowSceneItemDTO(
        scene_id=2,
        shot_type=FlowShotType.SHOT_A,
        title_or_prompt="Red alarm strobe",
        status=FlowSceneStatus.READY,
    )
    report = FlowInspectionReportDTO(
        authenticated=True,
        account_identifier="operator@gmail.com",
        active_project_title="1983 Soviet nuclear incident",
        total_online_scenes=2,
        synced_to_disk=1,
        pending_download=1,
        scenes=[item1, item2],
    )
    assert report.authenticated is True
    assert report.total_online_scenes == 2
    assert report.synced_to_disk == 1
    assert report.pending_download == 1
    assert len(report.scenes) == 2

def test_inspector_reconcile_with_local_inventory(tmp_path):
    # Setup mock local broll
    broll_dir = tmp_path / "broll"
    broll_dir.mkdir(parents=True)
    (broll_dir / "cena 1.mp4").write_text("dummy")

    inspector = GoogleFlowInspector(broll_dir=broll_dir)
    raw_scenes = [
        {"title": "Scene 1: Petrov in bunker", "card_id": "c1"},
        {"title": "Scene 5: Kremlin red telephone", "card_id": "c5"},
    ]
    report = inspector.reconcile_scenes(
        raw_items=raw_scenes,
        authenticated=True,
        account="test@google.com",
        project="Test Project",
    )
    assert report.authenticated is True
    assert report.total_online_scenes == 2
    # Scene 1 exists in broll_dir, so should be marked LOCAL_SYNCED
    s1 = next(s for s in report.scenes if s.scene_id == 1)
    assert s1.status == FlowSceneStatus.LOCAL_SYNCED
    # Scene 5 does not exist in broll_dir, so should be READY
    s5 = next(s for s in report.scenes if s.scene_id == 5)
    assert s5.status == FlowSceneStatus.READY
