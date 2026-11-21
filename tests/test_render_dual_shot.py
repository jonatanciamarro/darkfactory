"""Unit tests for Dual-Shot (Shot A Drama + Shot B Macro) rendering & stitching."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.render_pilot_video import render_scene_video, get_shot_candidates


def test_get_shot_candidates(tmp_path):
    """get_shot_candidates should return prioritized list of Shot A and Shot B paths."""
    with patch("src.render_pilot_video.BROLL_DIR", tmp_path):
        a_cands, b_cands = get_shot_candidates(scene_id=3)
        assert tmp_path / "scene_3.mp4" in a_cands
        assert tmp_path / "scene_3_b.mp4" in b_cands
        assert tmp_path / "scene_3b.mp4" in b_cands


def test_render_scene_dual_shot_composition(tmp_path):
    """When both Shot A and Shot B exist, scene is stitched from both takes."""
    shot_a = tmp_path / "scene_3.mp4"
    shot_b = tmp_path / "scene_3_b.mp4"
    shot_a.touch()
    shot_b.touch()
    output_mp4 = tmp_path / "output_scene_3.mp4"

    with patch("src.render_pilot_video.BROLL_DIR", tmp_path), \
         patch("src.render_pilot_video.OUTPUT_DIR", tmp_path), \
         patch("src.render_pilot_video.render_single_clip", return_value=True) as mock_single, \
         patch("src.render_pilot_video.subprocess.run") as mock_subproc:
        mock_subproc.return_value.returncode = 0

        ok = render_scene_video(
            ffmpeg_bin="ffmpeg",
            scene_id=3,
            duration=10.0,
            output_mp4=output_mp4,
        )

        assert ok is True
        # Both Shot A and Shot B must have been rendered
        assert mock_single.call_count == 2
        calls = mock_single.call_args_list
        # Call 1: Shot A with ~5.0s
        assert calls[0].kwargs["duration"] == 5.0
        # Call 2: Shot B with ~5.0s
        assert calls[1].kwargs["duration"] == 5.0


def test_render_scene_fallback_to_shot_b_when_shot_a_missing(tmp_path):
    """When Shot A is missing but Shot B exists (e.g. Scene 7), Shot B is used as video candidate."""
    shot_b = tmp_path / "scene_7_b.mp4"
    shot_b.touch()
    output_mp4 = tmp_path / "output_scene_7.mp4"

    with patch("src.render_pilot_video.BROLL_DIR", tmp_path), \
         patch("src.render_pilot_video.OUTPUT_DIR", tmp_path), \
         patch("src.render_pilot_video.render_single_clip", return_value=True) as mock_single:

        ok = render_scene_video(
            ffmpeg_bin="ffmpeg",
            scene_id=7,
            duration=8.0,
            output_mp4=output_mp4,
        )

        assert ok is True
        assert mock_single.call_count == 1
        clip_candidates = mock_single.call_args.kwargs["clip_candidates"]
        assert shot_b in clip_candidates
