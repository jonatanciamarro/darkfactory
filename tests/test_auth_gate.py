"""Unit tests for DarkFactory Pre-Flight Auth & Session Gate."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.auth_gate import (
    check_google_flow_session,
    check_runninghub_session,
    check_flowmusic_session,
    is_flowmusic_authenticated,
    enforce_production_auth_gate,
)


def test_auth_gate_dry_run_always_passes():
    """Dry-run mode should pass without requiring real browser sessions."""
    assert enforce_production_auth_gate(dry_run=True) is True


def test_auth_gate_non_interactive_unauthenticated_raises(tmp_path):
    """When sessions are unauthenticated and non-interactive is requested, must raise PermissionError."""
    with patch("src.auth_gate.check_google_flow_session", return_value=False), \
         patch("src.auth_gate.check_runninghub_session", return_value=False):
        with pytest.raises(PermissionError) as exc_info:
            enforce_production_auth_gate(interactive=False, dry_run=False)
        assert "Production Auth Gate Check Failed" in str(exc_info.value)


def test_auth_gate_passes_when_both_authenticated():
    """When both Google Flow and RunningHub are authenticated, gate returns True."""
    with patch("src.auth_gate.check_google_flow_session", return_value=True), \
         patch("src.auth_gate.check_runninghub_session", return_value=True):
        assert enforce_production_auth_gate(interactive=False, dry_run=False) is True


def test_check_google_flow_session_missing_profile(tmp_path):
    """Missing session files should return False immediately without launching browser."""
    missing_dir = tmp_path / "nonexistent_flow"
    assert check_google_flow_session(session_dir=missing_dir, headless=True) is False


def test_check_runninghub_session_missing_profile(tmp_path):
    """Missing RunningHub session files should return False immediately without launching browser."""
    missing_dir = tmp_path / "nonexistent_runninghub"
    assert check_runninghub_session(session_dir=missing_dir, headless=True) is False


def test_check_runninghub_session_valid_storage_state(tmp_path):
    """Valid storage_state.json with RunningHub cookies returns True."""
    session_dir = tmp_path / "runninghub_session"
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state_file = session_dir / "storage_state.json"
    valid_state = {
        "cookies": [
            {
                "name": "token",
                "value": "jwt_fake_token_value",
                "domain": "runninghub.ai",
                "path": "/",
                "expires": 9999999999,
            }
        ]
    }
    storage_state_file.write_text(json.dumps(valid_state), encoding="utf-8")
    assert check_runninghub_session(session_dir=session_dir, headless=True) is True


def test_is_google_flow_authenticated_false_on_landing_page_with_signin_button():
    """Unauthenticated landing page on flow.google.com with a sign-in button must return False."""
    from src.auth_gate import is_google_flow_authenticated

    mock_page = MagicMock()
    mock_page.url = "https://flow.google.com"
    mock_btn = MagicMock()
    mock_btn.is_visible.return_value = True
    mock_page.query_selector.return_value = mock_btn

    assert is_google_flow_authenticated(mock_page, context=None) is False


def test_is_google_flow_authenticated_true_with_sid_cookie():
    """Context with valid Google SID cookie returns True."""
    from src.auth_gate import is_google_flow_authenticated

    mock_page = MagicMock()
    mock_page.url = "https://flow.google.com"
    mock_page.query_selector.return_value = None

    mock_context = MagicMock()
    mock_context.cookies.return_value = [
        {"name": "SID", "value": "xyz123", "domain": ".google.com"}
    ]

    assert is_google_flow_authenticated(mock_page, context=mock_context) is True


def test_is_runninghub_authenticated_false_on_login_screen():
    """RunningHub login screen returns False."""
    from src.auth_gate import is_runninghub_authenticated

    mock_page = MagicMock()
    mock_page.url = "https://www.runninghub.ai/pt-br/login"
    assert is_runninghub_authenticated(mock_page, context=None) is False


def test_is_runninghub_authenticated_true_with_token_cookie():
    """Context with RunningHub token cookie returns True."""
    from src.auth_gate import is_runninghub_authenticated

    mock_page = MagicMock()
    mock_page.url = "https://www.runninghub.ai/pt-br/workbench"
    mock_page.query_selector.return_value = None

    mock_context = MagicMock()
    mock_context.cookies.return_value = [
        {"name": "token", "value": "ey123456", "domain": "runninghub.ai"}
    ]

    assert is_runninghub_authenticated(mock_page, context=mock_context) is True


def test_check_flowmusic_session_missing_profile(tmp_path):
    """Missing Flow Music session files should return False immediately without launching browser."""
    missing_dir = tmp_path / "nonexistent_flowmusic"
    assert check_flowmusic_session(session_dir=missing_dir, headless=True) is False


def test_check_flowmusic_session_valid_storage_state(tmp_path):
    """Valid storage_state.json with Flow Music cookies returns True."""
    session_dir = tmp_path / "flowmusic_session"
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state_file = session_dir / "storage_state.json"
    valid_state = {
        "cookies": [
            {
                "name": "session_token",
                "value": "fake_fm_token",
                "domain": "flowmusic.app",
                "path": "/",
                "expires": 9999999999,
            }
        ]
    }
    storage_state_file.write_text(json.dumps(valid_state), encoding="utf-8")
    assert check_flowmusic_session(session_dir=session_dir, headless=True) is True


def test_is_flowmusic_authenticated_false_on_signin_button():
    """Flow Music landing page with visible Sign In button returns False, even with Google cookies in context."""
    mock_page = MagicMock()
    mock_page.url = "https://www.flowmusic.app"
    mock_btn = MagicMock()
    mock_btn.is_visible.return_value = True
    mock_page.query_selector.return_value = mock_btn

    mock_context = MagicMock()
    mock_context.cookies.return_value = [
        {"name": "SID", "value": "xyz_google_sid", "domain": ".google.com"}
    ]

    assert is_flowmusic_authenticated(mock_page, context=mock_context) is False


def test_is_flowmusic_authenticated_true_with_compose_button():
    """Flow Music page with visible Compose button and no signin button returns True."""
    mock_page = MagicMock()
    mock_page.url = "https://www.flowmusic.app"

    def mock_query(selector):
        if "sign" in selector.lower() or "entrar" in selector.lower():
            return None
        btn = MagicMock()
        btn.is_visible.return_value = True
        return btn

    mock_page.query_selector.side_effect = mock_query
    assert is_flowmusic_authenticated(mock_page, context=None) is True

