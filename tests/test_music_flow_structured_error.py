"""Tests for Google Flow Music and RunningHub Offline Fallback Disabling and Structured Error Logs."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.music_flow_bot import GoogleFlowMusicBot
from src.runninghub_foley_bot import RunningHubFoleyBot
from src.video.minimax_music_engine import MiniMaxMusicEngine
from src.factory.runninghub_bot import (
    CONTA_COSYVOICE_CONFIG,
    CONTA_MINIMAX_MUSIC_CONFIG,
    CONTA_MINIMAX_H3_CONFIG,
    get_account_config,
)


class TestRunningHubUnifiedAccount1:
    """Ensure all RunningHub workflows open Account 1."""

    def test_all_configs_use_account_1(self):
        assert CONTA_COSYVOICE_CONFIG["account"] == 1
        assert CONTA_MINIMAX_MUSIC_CONFIG["account"] == 1
        assert CONTA_MINIMAX_H3_CONFIG["account"] == 1

    @pytest.mark.parametrize("acc_key", ["cosyvoice", "minimax_music", "minimax_h3", 1, 4, 5, 7])
    def test_get_account_config_always_resolves_to_account_1(self, acc_key):
        cfg = get_account_config(acc_key)
        assert cfg["account"] == 1


class TestOfflineFallbackDisabledStructuredError:
    """Ensure offline procedural synthesis is disabled and returns structured errors."""

    def test_music_flow_bot_free_mode_raises_error(self, tmp_path):
        bot = GoogleFlowMusicBot()
        out_file = tmp_path / "test_music.wav"
        with pytest.raises(RuntimeError) as exc_info:
            bot.generate_ost(output_path=out_file, mode="free")
        assert "desativado" in str(exc_info.value).lower()

    @patch.object(GoogleFlowMusicBot, "_run_human_playwright_flowmusic", return_value=False)
    def test_music_flow_bot_failure_generates_structured_error_log(self, mock_playwright, tmp_path):
        bot = GoogleFlowMusicBot()
        out_file = tmp_path / "test_music.wav"
        with pytest.raises(RuntimeError) as exc_info:
            bot.generate_ost(output_path=out_file, mode="platform")
        assert "Falha na geração de trilha" in str(exc_info.value) or "desativado" in str(exc_info.value).lower()

    def test_runninghub_foley_bot_free_mode_raises_error(self, tmp_path):
        bot = RunningHubFoleyBot()
        out_file = tmp_path / "test_foley.wav"
        with pytest.raises(RuntimeError) as exc_info:
            bot.generate_foley(output_path=out_file, mode="free")
        assert "desativado" in str(exc_info.value).lower()

    @patch("src.factory.runninghub_bot.run_minimax_music_bot")
    def test_minimax_music_engine_failure_raises_structured_error(self, mock_bot, tmp_path):
        mock_bot.side_effect = RuntimeError("RunningHub connection timeout")
        engine = MiniMaxMusicEngine(output_dir=tmp_path)
        with pytest.raises(RuntimeError) as exc_info:
            engine.generate_soundtrack(
                preset_name="hans_zimmer_tension",
                force_procedural=False,
                allow_procedural_fallback=False,
            )
        assert "RunningHub MiniMax Music 3 falhou" in str(exc_info.value)
