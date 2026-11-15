"""Unit and integration test suite for DarkFactory Motion & Visual Pipeline.

Tests:
1. SeedVR25Upscaler local Lanczos4 + CLAHE 4K upscale and dry-run execution.
2. MotionAssetPipeline pre-generation (MapAnimator, HyperFrames, 4K stills, Overlays).
3. CinematicColorGrader dynamic filter graph generation for various film profiles.
4. UniversalTimelineExporter multi-track .otio timeline export with beat markers.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.factory.seedvr_upscaler import SeedVR25Upscaler
from src.generate_motion_assets import MotionAssetPipeline
from src.video.cinematic_color import CinematicColorGrader, FilmLookProfile
from src.video.otio_exporter import (
    TimelineClipRef,
    TimelineMarker,
    UniversalTimelineExporter,
)


class TestSeedVR25Upscaler:
    """Tests for SeedVR 2.5 4K photo upscaling engine."""

    def test_upscaler_initialization(self, tmp_path: Path):
        upscaler = SeedVR25Upscaler(output_dir=tmp_path)
        assert upscaler.output_dir.resolve() == tmp_path.resolve()
        assert not upscaler.is_cloud_available()

    def test_upscale_dry_run(self, tmp_path: Path):
        input_img = tmp_path / "test_input.jpg"
        dummy = np.full((100, 100, 3), 128, dtype=np.uint8)
        cv2.imwrite(str(input_img), dummy)

        upscaler = SeedVR25Upscaler(output_dir=tmp_path)
        res = upscaler.upscale_image(
            input_image_path=input_img,
            target_width=3840,
            target_height=2160,
            dry_run=True,
        )
        assert res.success
        assert res.output_path.is_file()
        assert res.mode == "dry_run"

        out_img = cv2.imread(str(res.output_path))
        assert out_img.shape == (2160, 3840, 3)

    def test_upscale_local_high_fidelity(self, tmp_path: Path):
        input_img = tmp_path / "archival_sample.png"
        sample_gradient = np.tile(np.linspace(20, 200, 320, dtype=np.uint8), (180, 1))
        sample_bgr = cv2.merge([sample_gradient, sample_gradient, sample_gradient])
        cv2.imwrite(str(input_img), sample_bgr)

        upscaler = SeedVR25Upscaler(output_dir=tmp_path)
        res = upscaler.upscale_image(
            input_image_path=input_img,
            target_width=1920,  # Scaled target for rapid test execution
            target_height=1080,
            dry_run=False,
            denoise=True,
            grain_strength=0.05,
        )
        assert res.success
        assert res.output_path.is_file()
        assert res.mode == "local_lanczos4_clahe"
        assert res.original_size == (320, 180)
        assert res.target_size == (1920, 1080)

        out_img = cv2.imread(str(res.output_path))
        assert out_img.shape == (1080, 1920, 3)

    def test_upscale_missing_file_fails_gracefully(self, tmp_path: Path):
        upscaler = SeedVR25Upscaler(output_dir=tmp_path)
        res = upscaler.upscale_image(tmp_path / "non_existent.jpg")
        assert not res.success
        assert "not found" in (res.error or "").lower()


class TestMotionAssetPipeline:
    """Tests for Step 6.5 Motion Assets Pre-Synthesis."""

    @pytest.fixture
    def mock_script(self, tmp_path: Path) -> Path:
        script_data = {
            "title": "Test Documentary",
            "scenes": [
                {
                    "scene_id": 1,
                    "visual_style_type": "HERO_AI_DUAL_SHOT",
                    "estimated_duration_sec": 4.0,
                    "timestamp_marker": "00:00 | RADAR BUNKER",
                    "overlay_recipe": {
                        "template": "tactical_hud",
                        "stamp_text": "DEFCON 2",
                        "coordinates": "54°54'N 37°24'E",
                    },
                },
                {
                    "scene_id": 2,
                    "visual_style_type": "TACTICAL_MAP_MOTION",
                    "estimated_duration_sec": 3.0,
                    "timestamp_marker": "00:15 | FLIGHT PATH",
                    "overlay_recipe": {
                        "template": "tactical_hud",
                        "stamp_text": "AIR CORRIDOR",
                    },
                },
                {
                    "scene_id": 3,
                    "visual_style_type": "DECLASSIFIED_DOSSIER",
                    "estimated_duration_sec": 3.0,
                    "timestamp_marker": "00:30 | DOSSIER",
                    "overlay_recipe": {
                        "template": "declassified_dossier",
                        "stamp_text": "TOP SECRET",
                    },
                },
                {
                    "scene_id": 4,
                    "visual_style_type": "ARCHIVAL_KEN_BURNS",
                    "estimated_duration_sec": 4.0,
                    "timestamp_marker": "00:45 | ARCHIVE",
                },
            ],
        }
        script_file = tmp_path / "mock_script.json"
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(script_data, f)
        return script_file

    def test_pipeline_dry_run_processing(self, mock_script: Path, tmp_path: Path):
        out_dir = tmp_path / "motion_overlays"
        broll_dir = tmp_path / "broll"

        pipeline = MotionAssetPipeline(
            output_dir=out_dir,
            broll_dir=broll_dir,
            dry_run=True,
            force=True,
        )

        results = pipeline.process_all_scenes(mock_script, limit=4)
        assert results["scenes_processed"] == 4
        assert results["maps_rendered"] >= 1
        assert results["photos_4k_upscaled"] >= 1
        assert results["overlays_rendered"] >= 2


class TestCinematicColorGraderIntegration:
    """Tests for Cinematic Color Science & Film Profile Integration."""

    def test_kodak_profile_filter_generation(self):
        grader = CinematicColorGrader()
        filt = grader.build_filter_graph(FilmLookProfile.KODAK_2383, film_grain=True)
        assert "eq=contrast=" in filt
        assert "colorbalance=" in filt
        assert "noise=c0s=" in filt

    def test_bleach_bypass_profile(self):
        grader = CinematicColorGrader()
        filt = grader.build_filter_graph("bleach_bypass", film_grain=False)
        assert "eq=contrast=" in filt
        assert "noise=c0s=" not in filt

    def test_unknown_profile_fallback(self):
        grader = CinematicColorGrader()
        spec = grader.get_profile("unknown_vintage_look")
        assert spec.id == "kodak_2383"


class TestUniversalTimelineExporter:
    """Tests for OpenTimelineIO multi-track timeline construction."""

    def test_multitrack_otio_export(self, tmp_path: Path):
        exporter = UniversalTimelineExporter(fps=30)

        v1_clips = [
            TimelineClipRef("V1_001", "data/broll/scene_1.mp4", 5.0, 0.0, "Video", 1),
            TimelineClipRef("V1_002", "data/broll/scene_2.mp4", 5.0, 5.0, "Video", 1),
        ]
        a1_clips = [
            TimelineClipRef("A1_Voice", "data/audio/voice.mp3", 10.0, 0.0, "Audio", 1),
        ]
        a2_clips = [
            TimelineClipRef("A2_OST", "data/audio/ost.mp3", 10.0, 0.0, "Audio", 2),
        ]
        markers = [
            TimelineMarker("ACT_I", 0.0, "RED", "The Hook"),
            TimelineMarker("ACT_II", 5.0, "GREEN", "The Escalation"),
        ]

        otio_path = tmp_path / "test_timeline.otio"
        out_file = exporter.export_to_file(
            output_path=otio_path,
            timeline_name="Test Documentary Master Timeline",
            video_clips=v1_clips,
            audio_narration_clips=a1_clips,
            audio_music_clips=a2_clips,
            markers=markers,
        )

        assert out_file.is_file()
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("OTIO_SCHEMA") == "Timeline.1"
        assert len(data.get("tracks", {}).get("children", [])) >= 3
        assert len(data.get("markers", [])) == 2
