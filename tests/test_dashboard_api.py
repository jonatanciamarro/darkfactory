"""Automated Test Suite for the DarkFactory Cinema Dashboard API."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

DARKFACTORY_ROOT = Path(__file__).resolve().parent.parent
if str(DARKFACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(DARKFACTORY_ROOT))

from src.dashboard.app import app
from src.dashboard import readers, runner, schemas


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_index_spa_serves_html(client):
    """Verifies that the SPA root endpoint serves HTML with DarkFactory Cinema branding."""
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "DarkFactory" in res.text
    assert "Cinema" in res.text
    assert "Sound Lab" in res.text


def test_status_endpoint(client):
    """Verifies that /api/status returns valid KPIs and telemetry."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "active_tasks" in data
    k = data["kpis"]
    assert "total_productions" in k
    assert "completed_episodes" in k
    assert "pending_approvals" in k
    assert "green_dollar_rate" in k
    assert "google_flow_quota" in k


def test_screenplays_endpoint(client):
    """Verifies that /api/screenplays returns structured script dossiers."""
    res = client.get("/api/screenplays")
    assert res.status_code == 200
    scripts = res.json()
    assert isinstance(scripts, list)
    if len(scripts) > 0:
        first = scripts[0]
        assert "title" in first
        assert "logline" in first
        assert "timelines" in first


def test_visual_queues_endpoint(client):
    """Verifies that /api/visual-queues aggregates Veo 3.1 and Omni Flash prompts."""
    res = client.get("/api/visual-queues")
    assert res.status_code == 200
    data = res.json()
    assert "veo3_4k" in data
    assert "omni_flash" in data
    assert "runninghub_foley" in data


def test_audio_library_endpoint(client):
    """Verifies that /api/audio-library groups 4 audio stems."""
    res = client.get("/api/audio-library")
    assert res.status_code == 200
    data = res.json()
    assert "voice" in data
    assert "ost" in data
    assert "foley" in data
    assert "master" in data


def test_approval_queue_and_actions(client, monkeypatch, tmp_path):
    """Verifies that /api/approval-queue and /api/approval-action handle publication gates."""
    import src.dashboard.app as app_module

    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(readers, "DAEMON_STATE_FILE", tmp_path / "darkfactory_daemon_state.json")
    monkeypatch.setattr(readers, "QUARANTINE_DIR", tmp_path / "quarantine")

    res = client.get("/api/approval-queue")
    assert res.status_code == 200
    queue = res.json()
    assert isinstance(queue, list)

    # Test approval action (publish_unlisted)
    action_payload = {
        "video_id": "test_video_pilot_01",
        "action": "publish_unlisted",
        "selected_thumbnail": "variant_a"
    }
    action_res = client.post("/api/approval-action", json=action_payload)
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "success"
    assert action_res.json()["action"] == "published_unlisted"

    # Test rejection to quarantine
    reject_payload = {
        "video_id": "test_video_glitch_02",
        "action": "reject_quarantine",
        "quarantine_notes": "Audio clipped at 03:15, Veo artifacting."
    }
    reject_res = client.post("/api/approval-action", json=reject_payload)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "quarantined"


def test_download_package_endpoint(client):
    """Verifies that /api/download-package produces a valid zip archive stream."""
    res = client.get("/api/download-package/sample_pilot")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert len(res.content) > 0


def test_quarantine_endpoint(client):
    """Verifies that /api/quarantine lists quarantine diagnostics."""
    res = client.get("/api/quarantine")
    assert res.status_code == 200
    reports = res.json()
    assert isinstance(reports, list)


def test_daemon_control_validation(client):
    """Verifies that /api/daemon-control rejects invalid actions."""
    res = client.post("/api/daemon-control", json={"action": "invalid_action"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"


def test_auth_status_endpoint(client):
    """Verifies that /api/auth/status returns persistent authentication state for AI platforms."""
    res = client.get("/api/auth/status")
    assert res.status_code == 200
    data = res.json()
    assert "google_flow" in data
    assert "runninghub" in data
    assert "flowmusic" in data
    assert "all_authenticated" in data
    assert "preflight_gate_status" in data
    assert "authenticated" in data["google_flow"]
    assert "authenticated" in data["runninghub"]
    assert "authenticated" in data["flowmusic"]


def test_auth_login_endpoint(client, monkeypatch):
    """Verifies that /api/auth/login endpoint triggers interactive login task."""
    monkeypatch.setattr(runner, "launch_auth_login", lambda target="all": {"status": "started", "target": target, "message": "mocked"})
    res = client.post("/api/auth/login", json={"target": "all"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "started"
    assert data["target"] == "all"

    # Also test flowmusic target
    res_fm = client.post("/api/auth/login", json={"target": "flowmusic"})
    assert res_fm.status_code == 200
    assert res_fm.json()["status"] == "started"
    assert res_fm.json()["target"] == "flowmusic"


def test_index_spa_contains_auth_buttons(client):
    """Verifies that the SPA contains the login buttons requested by the operator."""
    res = client.get("/")
    assert res.status_code == 200
    text = res.text
    assert "btn-header-login" in text
    assert "btn-login-all-main" in text
    assert "Pré-Autenticação de Contas IA" in text
    assert "triggerAccountLogin" in text
    assert "flowmusic" in text


def test_status_endpoint_contains_golden_standards(client):
    """Verifies that /api/status returns telemetry for all 6 Canonical Standards."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "golden_standards" in data["kpis"]
    standards = data["kpis"]["golden_standards"]
    assert "standard_1_auth" in standards
    assert "standard_2_dual_shot" in standards
    assert "standard_3_cosyvoice" in standards
    assert "standard_4_flowmusic" in standards
    assert "standard_5_cc0_foley" in standards
    assert "standard_6_rh_gpu_saver" in standards


def test_index_spa_contains_golden_standards_cockpit(client):
    """Verifies that SPA HTML contains the 6 Golden Standards cockpit card and badges."""
    res = client.get("/")
    assert res.status_code == 200
    text = res.text
    assert "6 Padrões Canônicos de Produção (Golden Standards)" in text
    assert "std-1-badge" in text
    assert "std-2-badge" in text
    assert "std-3-badge" in text
    assert "std-4-badge" in text
    assert "std-5-badge" in text
    assert "std-6-badge" in text


def test_topics_suggestions_endpoint(client):
    """Verifies that /api/topics/suggestions returns compliant 15-30 min topics and categories."""
    res = client.get("/api/topics/suggestions?count=4")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert "topics" in data
    assert len(data["topics"]) == 4
    for t in data["topics"]:
        assert 15 <= t["duration_min"] <= 30
        assert t["green_dollar_score"] == 100
        assert t["edsa_compliant"] is True
        assert "viral_hook" in t


def test_topics_generate_endpoint_batch_and_seed(client):
    """Verifies that /api/topics/generate returns batch suggestions and procedural seeds."""
    res_batch = client.post("/api/topics/generate", json={"count": 3})
    assert res_batch.status_code == 200
    assert len(res_batch.json()["topics"]) == 3

    res_seed = client.post("/api/topics/generate", json={"seed_concept": "Apollo 13 Glitch"})
    assert res_seed.status_code == 200
    data_seed = res_seed.json()
    assert len(data_seed["topics"]) == 1
    assert "Apollo" in data_seed["topics"][0]["title"]


def test_topics_validate_endpoint(client):
    """Verifies that /api/topics/validate verifies compliance against YouTube guidelines."""
    res = client.post("/api/topics/validate", json={"topic": "1983 Soviet Nuclear False Alarm"})
    assert res.status_code == 200
    assert res.json()["is_green_dollar"] is True
