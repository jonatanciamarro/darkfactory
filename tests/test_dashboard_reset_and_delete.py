"""Automated Test Suite for Cinema Dashboard Reset, Episode Delete, and Asset Management.

Validates:
1. Path safety and traversal prevention (is_safe_asset_path).
2. Deletion of entire episode assets and daemon state synchronization.
3. Single asset deletion across allowed categories and rejection of forbidden targets (models, luts, templates, traversal).
4. Pipeline reset behavior: purging test artifacts, preserving critical models and LUTs, and resetting daemon state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import pytest
from fastapi.testclient import TestClient

import sys
DARKFACTORY_ROOT = Path(__file__).resolve().parent.parent
if str(DARKFACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(DARKFACTORY_ROOT))

from src.dashboard.app import app
import src.dashboard.app as app_module
from src.dashboard import readers


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_dashboard_env(tmp_path, monkeypatch):
    """Sets up an isolated, disposable data directory hierarchy for testing."""
    mock_data = tmp_path / "data"
    mock_data.mkdir(parents=True, exist_ok=True)

    mock_scripts = mock_data / "scripts"
    mock_audio = mock_data / "audio"
    mock_audio_mastered = mock_audio / "mastered"
    mock_final = mock_data / "final"
    mock_final_audio = mock_final / "audio"
    mock_final_videos = mock_final / "videos"
    mock_output = mock_data / "output"
    mock_processed = mock_data / "processed"
    mock_algo = mock_processed / "algorithm_packages"
    mock_dispute = mock_processed / "dispute_kits"
    mock_quarantine = mock_data / "quarantine"
    mock_subtitles = mock_data / "subtitles"
    mock_broll = mock_data / "broll"
    mock_models = mock_data / "models"
    mock_luts = mock_data / "luts"
    mock_templates = mock_data / "templates"
    mock_daemon_state = mock_processed / "darkfactory_daemon_state.json"

    for d in [
        mock_scripts,
        mock_audio,
        mock_audio_mastered,
        mock_final,
        mock_final_audio,
        mock_final_videos,
        mock_output,
        mock_processed,
        mock_algo,
        mock_dispute,
        mock_quarantine,
        mock_subtitles,
        mock_broll,
        mock_models,
        mock_luts,
        mock_templates,
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Initialize a dummy daemon state
    initial_state = {
        "status": "idle",
        "last_heartbeat": None,
        "current_topic": "Operation Barba",
        "current_topic_index": 2,
        "completed_episodes": ["video_alpha", "video_beta"],
        "pending_approval_queue": [
            {"video_id": "video_alpha", "filename": "video_alpha_master.mp4"},
            {"video_id": "video_gamma", "filename": "video_gamma_master.mp4"},
        ],
        "total_productions": 5,
    }
    with open(mock_daemon_state, "w", encoding="utf-8") as f:
        json.dump(initial_state, f)

    # Monkeypatch readers constants
    monkeypatch.setattr(readers, "DATA_DIR", mock_data)
    monkeypatch.setattr(readers, "SCRIPTS_DIR", mock_scripts)
    monkeypatch.setattr(readers, "AUDIO_DIR", mock_audio)
    monkeypatch.setattr(readers, "AUDIO_MASTERED_DIR", mock_audio_mastered)
    monkeypatch.setattr(readers, "FINAL_AUDIO_DIR", mock_final_audio)
    monkeypatch.setattr(readers, "OUTPUT_DIR", mock_output)
    monkeypatch.setattr(readers, "FINAL_VIDEOS_DIR", mock_final_videos)
    monkeypatch.setattr(readers, "PROCESSED_DIR", mock_processed)
    monkeypatch.setattr(readers, "ALGORITHM_PACKAGES_DIR", mock_algo)
    monkeypatch.setattr(readers, "DISPUTE_KITS_DIR", mock_dispute)
    monkeypatch.setattr(readers, "QUARANTINE_DIR", mock_quarantine)
    monkeypatch.setattr(readers, "SUBTITLES_DIR", mock_subtitles)
    monkeypatch.setattr(readers, "BROLL_DIR", mock_broll)
    monkeypatch.setattr(readers, "DAEMON_STATE_FILE", mock_daemon_state)

    monkeypatch.setattr(app_module, "DATA_DIR", mock_data)

    return {
        "data": mock_data,
        "scripts": mock_scripts,
        "audio": mock_audio,
        "final_audio": mock_final_audio,
        "final_videos": mock_final_videos,
        "output": mock_output,
        "processed": mock_processed,
        "algo": mock_algo,
        "dispute": mock_dispute,
        "quarantine": mock_quarantine,
        "subtitles": mock_subtitles,
        "broll": mock_broll,
        "models": mock_models,
        "luts": mock_luts,
        "templates": mock_templates,
        "daemon_state_file": mock_daemon_state,
    }


# ==============================================================================
# 1. Tests for Path Safety and Traversal Prevention (is_safe_asset_path)
# ==============================================================================

def test_is_safe_asset_path_allows_valid_data_paths(mock_dashboard_env):
    """Verifies that is_safe_asset_path allows paths inside mutable data directories."""
    env = mock_dashboard_env
    valid_paths = [
        env["output"] / "episode_01.mp4",
        env["final_videos"] / "master_cut.mp4",
        env["subtitles"] / "episode_01.srt",
        env["audio"] / "narration_stem.wav",
        env["final_audio"] / "mix_minus_14lufs.mp3",
        env["scripts"] / "nolan_dossier.json",
        env["quarantine"] / "glitch_take" / "report.json",
        env["broll"] / "frame_001.jpg",
        env["algo"] / "seo_meta.json",
        env["dispute"] / "dmca_kit.txt",
    ]

    for p in valid_paths:
        assert readers.is_safe_asset_path(p) is True, f"Expected {p} to be marked safe"


def test_is_safe_asset_path_rejects_protected_directories(mock_dashboard_env):
    """Verifies that is_safe_asset_path strictly rejects models, luts, and templates."""
    env = mock_dashboard_env
    forbidden_paths = [
        env["models"] / "kokoro-v0_19.onnx",
        env["models"] / "subfolder" / "checkpoint.pth",
        env["models"],
        env["luts"] / "kodak_vision3_5207.cube",
        env["luts"] / "fuji_eterna.cube",
        env["luts"],
        env["templates"] / "documentary_preset.json",
        env["templates"] / "sub_dir" / "config.yaml",
        env["templates"],
    ]

    for p in forbidden_paths:
        assert readers.is_safe_asset_path(p) is False, f"Expected protected path {p} to be rejected"


def test_is_safe_asset_path_rejects_external_and_traversal_paths(mock_dashboard_env):
    """Verifies that is_safe_asset_path rejects paths outside DATA_DIR or with path traversal."""
    env = mock_dashboard_env
    traversal_or_external_paths = [
        env["data"].parent / "src" / "dashboard" / "app.py",
        env["data"].parent / ".env",
        env["output"] / ".." / ".." / "src" / "main.py",
        env["output"] / ".." / "models" / "kokoro.onnx",
        env["output"] / ".." / "luts" / "kodak.cube",
        env["output"] / ".." / "templates" / "base.json",
        Path("C:/Windows/System32/cmd.exe") if sys.platform.startswith("win") else Path("/bin/sh"),
        Path("C:/Users/Administrator/.ssh/id_rsa") if sys.platform.startswith("win") else Path("/etc/passwd"),
    ]

    for p in traversal_or_external_paths:
        assert readers.is_safe_asset_path(p) is False, f"Expected {p} to be rejected"


# ==============================================================================
# 2. Tests for DELETE /api/episodes/{video_id}
# ==============================================================================

def test_delete_episode_endpoint_removes_files_and_updates_daemon_state(client, mock_dashboard_env):
    """Verifies DELETE /api/episodes/{video_id} removes all related episode files and updates state."""
    env = mock_dashboard_env
    vid = "ep_coldwar_001"

    # Seed files related to ep_coldwar_001
    f_out = env["output"] / f"{vid}_raw.mp4"
    f_final = env["final_videos"] / f"{vid}_master.mp4"
    f_sub = env["subtitles"] / f"{vid}_ptbr.srt"
    f_algo = env["algo"] / f"algorithm_pkg_{vid}.json"
    f_dispute = env["dispute"] / f"dispute_kit_{vid}.txt"
    f_broll = env["broll"] / f"{vid}_broll_01.jpg"

    for f in [f_out, f_final, f_sub, f_algo, f_dispute, f_broll]:
        f.write_text("dummy episode content", encoding="utf-8")

    # Seed unrelated file that must NOT be deleted
    f_unrelated = env["output"] / "ep_unrelated_999.mp4"
    f_unrelated.write_text("unrelated content", encoding="utf-8")

    # Put vid into daemon state
    state_file = env["daemon_state_file"]
    state_data = {
        "status": "waiting_approval",
        "completed_episodes": [vid, "other_ep"],
        "pending_approval_queue": [
            {"video_id": vid, "filename": f"{vid}_master.mp4"},
            {"video_id": "other_ep", "filename": "other_master.mp4"},
        ],
        "total_productions": 10,
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_data, f)

    res = client.delete(f"/api/episodes/{vid}")
    assert res.status_code == 200, f"Delete episode returned {res.status_code}: {res.text}"
    body = res.json()
    assert body.get("status") in {"success", "ok"}
    assert body.get("video_id") == vid

    # Assert related files are removed
    assert not f_out.exists(), "Output video was not deleted"
    assert not f_final.exists(), "Final video was not deleted"
    assert not f_sub.exists(), "Subtitle was not deleted"
    assert not f_algo.exists(), "Algorithm package was not deleted"
    assert not f_dispute.exists(), "Dispute kit was not deleted"

    # Assert unrelated file is untouched
    assert f_unrelated.exists(), "Unrelated file was incorrectly deleted"

    # Verify daemon state update
    with open(state_file, "r", encoding="utf-8") as f:
        updated_state = json.load(f)

    completed = updated_state.get("completed_episodes", [])
    assert vid not in completed, f"Episode {vid} still present in completed_episodes"
    assert "other_ep" in completed

    pending = [item.get("video_id") for item in updated_state.get("pending_approval_queue", [])]
    assert vid not in pending, f"Episode {vid} still present in pending_approval_queue"
    assert "other_ep" in pending


def test_delete_episode_nonexistent_returns_gracefully(client, mock_dashboard_env):
    """Verifies DELETE /api/episodes/{video_id} handles non-existent IDs gracefully."""
    res = client.delete("/api/episodes/nonexistent_video_id_xyz")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") in {"success", "ok"}


# ==============================================================================
# 3. Tests for DELETE /api/asset
# ==============================================================================

@pytest.mark.parametrize("category,folder_key,filename", [
    ("output", "output", "test_pilot_output.mp4"),
    ("video", "final_videos", "test_master.mp4"),
    ("subtitles", "subtitles", "test_sub.srt"),
    ("seo", "algo", "test_seo_pkg.json"),
    ("dispute_kit", "dispute", "test_dispute_kit.txt"),
    ("audio", "audio", "test_voice.mp3"),
    ("broll", "broll", "test_broll_frame.png"),
    ("scripts", "scripts", "test_screenplay.json"),
])
def test_delete_asset_allowed_categories(client, mock_dashboard_env, category, folder_key, filename):
    """Verifies DELETE /api/asset deletes individual files across all allowed categories."""
    env = mock_dashboard_env
    target_file = env[folder_key] / filename
    target_file.write_text("asset test content", encoding="utf-8")
    assert target_file.exists()

    res = client.delete(f"/api/asset?category={category}&filename={filename}")
    assert res.status_code == 200, f"Failed deleting {category}/{filename}: {res.text}"
    body = res.json()
    assert body.get("status") in {"success", "ok"}
    assert not target_file.exists(), f"File {target_file} was not deleted"


def test_delete_asset_quarantine_directory(client, mock_dashboard_env):
    """Verifies DELETE /api/asset handles quarantine directory or report removal."""
    env = mock_dashboard_env
    q_dir = env["quarantine"] / "glitch_dir_001"
    q_dir.mkdir(parents=True, exist_ok=True)
    report_file = q_dir / "quarantine_report.json"
    report_file.write_text('{"error": "artifacting"}', encoding="utf-8")

    res = client.delete("/api/asset?category=quarantine&filename=glitch_dir_001")
    assert res.status_code == 200
    assert not q_dir.exists()


def test_delete_asset_rejects_forbidden_and_traversal_paths(client, mock_dashboard_env):
    """Verifies DELETE /api/asset rejects forbidden categories, traversal, or protected assets."""
    env = mock_dashboard_env

    # 1. Traversal attempt
    res_trav = client.delete("/api/asset?category=output&filename=../../app.py")
    assert res_trav.status_code in {400, 403, 404, 422}

    # 2. Attempting to delete protected models
    kokoro = env["models"] / "kokoro-test.onnx"
    kokoro.write_text("model weights", encoding="utf-8")
    res_model = client.delete("/api/asset?category=models&filename=kokoro-test.onnx")
    assert res_model.status_code in {400, 403, 404, 422}
    assert kokoro.exists(), "Protected model was deleted!"

    # 3. Attempting to delete protected LUTs
    lut = env["luts"] / "cinematic.cube"
    lut.write_text("lut content", encoding="utf-8")
    res_lut = client.delete("/api/asset?category=luts&filename=cinematic.cube")
    assert res_lut.status_code in {400, 403, 404, 422}
    assert lut.exists(), "Protected LUT was deleted!"

    # 4. Attempting to delete protected templates
    tpl = env["templates"] / "template.json"
    tpl.write_text("{}", encoding="utf-8")
    res_tpl = client.delete("/api/asset?category=templates&filename=template.json")
    assert res_tpl.status_code in {400, 403, 404, 422}
    assert tpl.exists(), "Protected template was deleted!"


# ==============================================================================
# 4. Tests for POST /api/pipeline/reset
# ==============================================================================

def test_pipeline_reset_purges_outputs_and_preserves_models_luts(client, mock_dashboard_env):
    """Verifies POST /api/pipeline/reset purges artifacts, preserves models/luts, and resets state."""
    env = mock_dashboard_env

    # Seed ephemeral test outputs
    ephemeral_files = [
        env["output"] / "temp_video.mp4",
        env["final_videos"] / "final_render.mp4",
        env["final_audio"] / "final_soundtrack.wav",
        env["audio"] / "stem_voice.mp3",
        env["broll"] / "frame_1.jpg",
        env["subtitles"] / "temp_sub.srt",
        env["algo"] / "temp_pkg.json",
        env["dispute"] / "temp_dispute.txt",
        env["scripts"] / "temp_nolan_script.json",
    ]
    for ef in ephemeral_files:
        ef.write_text("ephemeral test data", encoding="utf-8")

    # Seed quarantine directory
    q_dir = env["quarantine"] / "take_glitch"
    q_dir.mkdir(parents=True, exist_ok=True)
    (q_dir / "quarantine_report.json").write_text("{}", encoding="utf-8")

    # Seed PROTECTED assets that must be preserved
    model_file = env["models"] / "kokoro-v0_19.onnx"
    model_file.write_text("BINARY_MODEL_DATA", encoding="utf-8")

    lut_file = env["luts"] / "kodak_vision3.cube"
    lut_file.write_text("LUT_DATA_TABLE", encoding="utf-8")

    template_file = env["templates"] / "nolan_structure.json"
    template_file.write_text('{"preset": "nolan_5_acts"}', encoding="utf-8")

    # Set modified daemon state
    state_file = env["daemon_state_file"]
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "status": "processing",
                "completed_episodes": ["ep1", "ep2"],
                "pending_approval_queue": [{"video_id": "ep3"}],
                "total_productions": 12,
            },
            f,
        )

    # Perform pipeline reset with include_scripts=True
    res = client.post("/api/pipeline/reset", json={"include_scripts": True})
    assert res.status_code == 200, f"Reset endpoint failed: {res.text}"
    body = res.json()
    assert body.get("status") in {"success", "ok"}

    # 1. Verify ephemeral files are purged
    for ef in ephemeral_files:
        assert not ef.exists(), f"Ephemeral file {ef} was not deleted during reset!"
    assert not (q_dir / "quarantine_report.json").exists(), "Quarantine item was not purged"

    # 2. Verify protected assets are strictly preserved
    assert model_file.exists(), "PROTECTED MODEL FILE WAS DELETED!"
    assert model_file.read_text(encoding="utf-8") == "BINARY_MODEL_DATA"

    assert lut_file.exists(), "PROTECTED LUT FILE WAS DELETED!"
    assert lut_file.read_text(encoding="utf-8") == "LUT_DATA_TABLE"

    assert template_file.exists(), "PROTECTED TEMPLATE FILE WAS DELETED!"
    assert template_file.read_text(encoding="utf-8") == '{"preset": "nolan_5_acts"}'

    # 3. Verify daemon state reset to factory defaults
    with open(state_file, "r", encoding="utf-8") as f:
        reset_state = json.load(f)

    assert reset_state.get("status") == "idle"
    assert reset_state.get("completed_episodes") == []
    assert reset_state.get("pending_approval_queue") == []
    assert reset_state.get("total_productions") == 0


def test_pipeline_reset_preserves_scripts_when_include_scripts_false(client, mock_dashboard_env):
    """Verifies POST /api/pipeline/reset preserves scripts when include_scripts is False."""
    env = mock_dashboard_env

    # Ephemeral output
    out_video = env["output"] / "temp_render.mp4"
    out_video.write_text("video", encoding="utf-8")

    # Script that should be kept
    script_file = env["scripts"] / "keep_this_script.json"
    script_file.write_text('{"title": "Preserved History"}', encoding="utf-8")

    res = client.post("/api/pipeline/reset", json={"include_scripts": False})
    assert res.status_code == 200
    assert not out_video.exists(), "Output video was not purged"
    assert script_file.exists(), "Script was purged despite include_scripts=False"
