#!/usr/bin/env python3
"""Shift-Left TDD tests for RunningHub Workflow Resilience & Google Flow Selectors."""
from unittest.mock import MagicMock, patch
import pytest

from src.factory.runninghub_bot import (
    RunningHubWorkflowNotFoundError,
    detect_runninghub_workflow_error,
)
from src.google_flow_bot import GoogleFlowBot


class TestRunningHubWorkflowResilience:
    """Test fast-failure when RunningHub workflow is deleted or not found."""

    def test_detect_deleted_workflow_returns_error_message(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "O recurso foi excluído pelo autor original! O fluxo de trabalho não existe"
        
        err = detect_runninghub_workflow_error(mock_page)
        assert err is not None
        assert "excluído pelo autor original" in err

    def test_detect_deleted_workflow_returns_none_when_normal(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "RunningHub ComfyUI Cloud Workspace Queue: 0"
        
        err = detect_runninghub_workflow_error(mock_page)
        assert err is None

    def test_runninghub_workflow_not_found_exception(self):
        exc = RunningHubWorkflowNotFoundError("2118560390471745537", "Recurso excluído")
        assert "2118560390471745537" in str(exc)
        assert "Recurso excluído" in str(exc)


class TestGoogleFlowEntranceSelectors:
    """Test updated Google Flow landing page entrance selectors."""

    def test_entrance_selectors_include_create_with_google_flow(self):
        bot = GoogleFlowBot()
        selectors = bot.get_studio_entrance_selectors()
        assert any("Create with Google Flow" in sel for sel in selectors)
        assert any("Try in Google Flow" in sel for sel in selectors)
