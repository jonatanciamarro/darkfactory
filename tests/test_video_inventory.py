"""Shift-Left TDD Suite: Video Asset Inventory, Audit & GPU Economy Dispatcher.

Verifies:
1. VideoAssetMetadata and VideoInventoryAuditReport DTO contracts.
2. File naming variant reconciliation (e.g., 'cena 1.mp4' == 'scene_1.mp4', 'cena 1b.mp4' == 'scene_1_b.mp4').
3. Multi-directory asset scanning and media integrity validation.
4. Calculation of coverage metrics and GPU minutes/credits saved.
5. Generation of filtered pending queues ('_pending.json') for zero-waste dispatching.
6. Ingest and standardization of external/loose clips into data/broll/.
"""

import json
from pathlib import Path
import pytest

from src.video.video_inventory import (
    VideoAssetMetadata,
    VideoInventoryAuditReport,
    VideoInventoryManager,
    parse_scene_and_shot_from_filename,
    validate_video_file_integrity,
)


class TestVideoInventoryContracts:
    """Verifies DTO contracts and data structures."""

    def test_asset_metadata_dto(self, tmp_path):
        dummy_file = tmp_path / "scene_2.mp4"
        dummy_file.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"A" * 60000)

        meta = VideoAssetMetadata(
            scene_id=2,
            shot_type="shot_a",
            file_path=dummy_file,
            file_size_bytes=dummy_file.stat().st_size,
            duration_sec=14.5,
            is_valid=True,
            source_folder="data/broll",
        )

        assert meta.scene_id == 2
        assert meta.shot_type == "shot_a"
        assert meta.file_path == dummy_file
        assert meta.file_size_bytes > 50000
        assert meta.is_valid is True

    def test_audit_report_dto_calculations(self):
        report = VideoInventoryAuditReport(
            total_required_scenes=40,
            total_required_takes=80,
            existing_shot_a_count=4,
            existing_shot_b_count=2,
            missing_shot_a_ids=list(range(5, 41)),
            missing_shot_b_ids=list(range(3, 41)),
            coverage_percentage=7.5,
            estimated_gpu_minutes_saved=9.0,
            existing_assets=[],
        )

        assert report.total_required_takes == 80
        assert report.existing_total_takes == 6
        assert report.missing_total_takes == 74
        assert report.coverage_percentage == 7.5
        assert report.estimated_gpu_minutes_saved == 9.0


class TestFilenameParsingAndIntegrity:
    """Verifies regex and heuristic resolution of scene IDs and shot types."""

    @pytest.mark.parametrize(
        "filename,expected_scene,expected_shot",
        [
            ("cena 1.mp4", 1, "shot_a"),
            ("scene_1.mp4", 1, "shot_a"),
            ("cena 1b.mp4", 1, "shot_b"),
            ("cena 1_b.mp4", 1, "shot_b"),
            ("scene_1_b.mp4", 1, "shot_b"),
            ("scene_1b.mp4", 1, "shot_b"),
            ("scene_22.mp4", 22, "shot_a"),
            ("scene_22_b.mp4", 22, "shot_b"),
            ("SCENE_05.MP4", 5, "shot_a"),
            ("Scene 05 b.mp4", 5, "shot_b"),
            ("minimax_h3_cinematic_scene_7.mp4", 7, "shot_a"),
            ("random_background.mp4", None, None),
        ],
    )
    def test_parse_scene_and_shot(self, filename, expected_scene, expected_shot):
        scene_id, shot_type = parse_scene_and_shot_from_filename(filename)
        assert scene_id == expected_scene
        assert shot_type == expected_shot

    def test_validate_video_file_integrity_valid(self, tmp_path):
        valid_file = tmp_path / "valid.mp4"
        valid_file.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"X" * 70000)
        assert validate_video_file_integrity(valid_file) is True

    def test_validate_video_file_integrity_too_small(self, tmp_path):
        small_file = tmp_path / "corrupt.mp4"
        small_file.write_bytes(b"too small")
        assert validate_video_file_integrity(small_file) is False

    def test_validate_video_file_integrity_nonexistent(self, tmp_path):
        ghost_file = tmp_path / "nonexistent.mp4"
        assert validate_video_file_integrity(ghost_file) is False


class TestVideoInventoryManager:
    """Verifies full audit flow, queue filtering, and ingestion."""

    @pytest.fixture
    def manager(self):
        return VideoInventoryManager()

    def test_audit_inventory_detects_existing_and_missing(self, manager, tmp_path):
        broll_dir = tmp_path / "broll"
        broll_dir.mkdir()

        # Criar cena 2 (Shot A) e cena 2_b (Shot B), e cena 3 (Shot A)
        f_scene_2 = broll_dir / "scene_2.mp4"
        f_scene_2.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"A" * 60000)

        f_scene_2b = broll_dir / "cena 2b.mp4"
        f_scene_2b.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"B" * 60000)

        f_scene_3 = broll_dir / "scene_3.mp4"
        f_scene_3.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"C" * 60000)

        report = manager.audit_inventory(
            search_dirs=[broll_dir],
            total_scenes=40,
        )

        assert report.existing_shot_a_count == 2  # scene 2 and scene 3
        assert report.existing_shot_b_count == 1  # scene 2_b
        assert report.existing_total_takes == 3
        assert 2 not in report.missing_shot_a_ids
        assert 3 not in report.missing_shot_a_ids
        assert 2 not in report.missing_shot_b_ids
        assert 1 in report.missing_shot_a_ids
        assert 1 in report.missing_shot_b_ids
        assert report.coverage_percentage == (3 / 80) * 100.0

    def test_generate_pending_queues_filters_existing(self, manager, tmp_path):
        # Queues sintéticas com 3 cenas
        omni_queue_data = {
            "scenes": [
                {"scene_id": 1, "shot_name": "Shot 1", "prompt": "Prompt 1"},
                {"scene_id": 2, "shot_name": "Shot 2", "prompt": "Prompt 2"},
                {"scene_id": 3, "shot_name": "Shot 3", "prompt": "Prompt 3"},
            ]
        }
        veo3_queue_data = {
            "scenes": [
                {"scene_id": 1, "shot_name": "Shot 1B", "prompt": "Prompt 1B"},
                {"scene_id": 2, "shot_name": "Shot 2B", "prompt": "Prompt 2B"},
                {"scene_id": 3, "shot_name": "Shot 3B", "prompt": "Prompt 3B"},
            ]
        }
        omni_file = tmp_path / "omni_full.json"
        veo3_file = tmp_path / "veo3_full.json"
        omni_file.write_text(json.dumps(omni_queue_data), encoding="utf-8")
        veo3_file.write_text(json.dumps(veo3_queue_data), encoding="utf-8")

        # Report simulando que a cena 2 já existe em Shot A e Shot B
        report = VideoInventoryAuditReport(
            total_required_scenes=3,
            total_required_takes=6,
            existing_shot_a_count=1,
            existing_shot_b_count=1,
            missing_shot_a_ids=[1, 3],
            missing_shot_b_ids=[1, 3],
            coverage_percentage=33.3,
            estimated_gpu_minutes_saved=3.0,
            existing_assets=[],
        )

        out_omni, out_veo3 = manager.generate_pending_queues(
            audit_report=report,
            omni_queue_file=omni_file,
            veo3_queue_file=veo3_file,
            output_dir=tmp_path,
        )

        assert out_omni.exists()
        assert out_veo3.exists()

        filtered_omni = json.loads(out_omni.read_text(encoding="utf-8"))
        filtered_veo3 = json.loads(out_veo3.read_text(encoding="utf-8"))

        # Cenas filtradas devem conter APENAS 1 e 3 (a cena 2 foi excluída)
        omni_ids = [s["scene_id"] for s in filtered_omni["scenes"]]
        veo3_ids = [s["scene_id"] for s in filtered_veo3["scenes"]]
        assert omni_ids == [1, 3]
        assert veo3_ids == [1, 3]

    def test_ingest_clips_from_directory(self, manager, tmp_path):
        source_dir = tmp_path / "downloads"
        target_dir = tmp_path / "broll"
        source_dir.mkdir()
        target_dir.mkdir()

        # Criar clipe avulso com nome informal na pasta de download
        loose_clip = source_dir / "Flow_Clip_cena 5_take.mp4"
        loose_clip.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"Z" * 65000)

        ingested = manager.ingest_clips_from_directory(
            source_dir=source_dir,
            target_broll_dir=target_dir,
        )

        assert len(ingested) == 1
        expected_target = target_dir / "scene_5.mp4"
        assert expected_target.exists()
        assert expected_target.stat().st_size > 50000


class TestGoogleFlowBotIntegration:
    """Verifies that GoogleFlowBot uses the inventory recognition to skip existing files."""

    def test_find_existing_clip_variants(self, tmp_path):
        from src.google_flow_bot import GoogleFlowBot
        bot = GoogleFlowBot(broll_dir=tmp_path)

        # Criar cena 1 com nome legado 'cena 1.mp4'
        c1 = tmp_path / "cena 1.mp4"
        c1.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"X" * 60000)

        # Criar cena 4 com nome moderno 'scene_4_b.mp4'
        c4b = tmp_path / "scene_4_b.mp4"
        c4b.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"Y" * 60000)

        found_1a = bot.find_existing_clip(1, shot_type="shot_a")
        assert found_1a == c1

        found_4b = bot.find_existing_clip(4, shot_type="shot_b")
        assert found_4b == c4b

        # Cena 99 não existe
        assert bot.find_existing_clip(99, shot_type="shot_a") is None

