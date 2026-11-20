#!/usr/bin/env python3
"""DarkFactory Google Flow Scene Inspector.

Inspects active projects, generated video cards, and status on Google Flow
using persistent Playwright session contexts, and reconciles findings against
the local data/broll/ video inventory.
"""
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("FlowInspector")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
BROLL_DIR = DATA_DIR / "broll"
SESSIONS_DIR = PROJECT_ROOT / "chrome_session" / "google_flow"
GOOGLE_FLOW_URL = os.getenv("GOOGLE_FLOW_URL", "https://flow.google.com")


class FlowShotType(str, Enum):
    SHOT_A = "shot_a"  # Omni Flash continuity take (15s)
    SHOT_B = "shot_b"  # DeepMind Veo 3.1 4K hero take (8s)
    UNKNOWN = "unknown"


class FlowSceneStatus(str, Enum):
    READY = "ready"
    GENERATING = "generating"
    FAILED = "failed"
    LOCAL_SYNCED = "local_synced"


@dataclass
class FlowSceneItemDTO:
    """Canonical representation of an inspected scene card in Google Flow."""
    scene_id: Optional[int]
    shot_type: FlowShotType
    title_or_prompt: str
    status: FlowSceneStatus
    card_id: Optional[str] = None
    video_stream_url: Optional[str] = None
    local_path: Optional[Path] = None
    file_size_bytes: int = 0


@dataclass
class FlowInspectionReportDTO:
    """Consolidated report of Google Flow online workspace and inventory sync."""
    authenticated: bool
    account_identifier: Optional[str]
    active_project_title: Optional[str]
    total_online_scenes: int
    synced_to_disk: int
    pending_download: int
    scenes: List[FlowSceneItemDTO] = field(default_factory=list)


def parse_scene_id_from_text(text: str) -> Optional[int]:
    """Extract scene number from card text, prompt, or title."""
    # Matches: "cena 1", "scene 01", "cena: 2", "scene_3", "#4", "scene 10"
    m = re.search(r"(?:cena|scene|take)\s*[:_#\-]?\s*(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m2 = re.search(r"#\s*(\d+)", text)
    if m2:
        return int(m2.group(1))
    return None


def detect_shot_type_from_text(text: str) -> FlowShotType:
    """Determine whether a card belongs to Shot A or Shot B."""
    t = text.lower()
    if "shot b" in t or "veo" in t or "hero" in t or "macro" in t or "cena 1b" in t or "1b" in t:
        return FlowShotType.SHOT_B
    if "shot a" in t or "omni" in t or "continuity" in t:
        return FlowShotType.SHOT_A
    return FlowShotType.SHOT_A  # Default to Shot A for standard prompts


class GoogleFlowInspector:
    """Inspects Google Flow live session and reconciles against local inventory."""

    def __init__(
        self,
        session_dir: Optional[Path] = None,
        broll_dir: Optional[Path] = None,
        timeout_sec: float = 20.0,
    ):
        self.session_dir = session_dir or SESSIONS_DIR
        self.broll_dir = broll_dir or BROLL_DIR
        self.timeout_sec = timeout_sec

    def reconcile_scenes(
        self,
        raw_items: List[Dict[str, Any]],
        authenticated: bool,
        account: Optional[str] = None,
        project: Optional[str] = None,
    ) -> FlowInspectionReportDTO:
        """Transforms raw DOM elements into canonical DTOs and checks local disk sync."""
        scenes: List[FlowSceneItemDTO] = []
        synced_count = 0
        pending_count = 0

        # Scan local files
        local_files = list(self.broll_dir.glob("*.mp4")) if self.broll_dir.exists() else []

        for item in raw_items:
            title = item.get("title", "")
            card_id = item.get("card_id")
            stream_url = item.get("video_src")
            status_raw = item.get("status", "ready").lower()

            scene_id = item.get("scene_id") or parse_scene_id_from_text(title)
            shot_type = item.get("shot_type") or detect_shot_type_from_text(title)

            # Check if synced locally
            matched_path: Optional[Path] = None
            if scene_id is not None:
                for lf in local_files:
                    lf_name = lf.name.lower()
                    # Match patterns like "cena 1.mp4", "scene_1.mp4", "cena 1b.mp4"
                    scene_pattern = rf"(?:cena|scene)\s*_{0,1}{scene_id}(?:b|\.mp4)"
                    if re.search(rf"(?:cena|scene)[_\s]?{scene_id}(?:[b_]|\.mp4)", lf_name):
                        if shot_type == FlowShotType.SHOT_B and "b" in lf_name:
                            matched_path = lf
                            break
                        elif shot_type == FlowShotType.SHOT_A and "b" not in lf_name:
                            matched_path = lf
                            break

            if matched_path:
                status = FlowSceneStatus.LOCAL_SYNCED
                synced_count += 1
                size = matched_path.stat().st_size
            else:
                if "generating" in status_raw or "progress" in status_raw:
                    status = FlowSceneStatus.GENERATING
                elif "failed" in status_raw or "error" in status_raw:
                    status = FlowSceneStatus.FAILED
                else:
                    status = FlowSceneStatus.READY
                pending_count += 1
                size = 0

            scenes.append(
                FlowSceneItemDTO(
                    scene_id=scene_id,
                    shot_type=shot_type,
                    title_or_prompt=title,
                    status=status,
                    card_id=card_id,
                    video_stream_url=stream_url,
                    local_path=matched_path,
                    file_size_bytes=size,
                )
            )

        return FlowInspectionReportDTO(
            authenticated=authenticated,
            account_identifier=account,
            active_project_title=project,
            total_online_scenes=len(scenes),
            synced_to_disk=synced_count,
            pending_download=pending_count,
            scenes=scenes,
        )

    def inspect_online_session(
        self,
        headless: bool = True,
        save_screenshot_path: Optional[Path] = None,
    ) -> FlowInspectionReportDTO:
        """Launches Playwright with persistent context to inspect Google Flow workspace."""
        from playwright.sync_api import sync_playwright
        from src.auth_gate import is_google_flow_authenticated

        if not self.session_dir.exists():
            return FlowInspectionReportDTO(
                authenticated=False,
                account_identifier=None,
                active_project_title=None,
                total_online_scenes=0,
                synced_to_disk=0,
                pending_download=0,
                scenes=[],
            )

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            page = context.new_page() if not context.pages else context.pages[0]

            logger.info("Acessando Google Flow para inspeção...")
            try:
                page.goto(GOOGLE_FLOW_URL, wait_until="domcontentloaded", timeout=int(self.timeout_sec * 1000))
                time.sleep(3)
            except Exception as exc:
                logger.warning(f"Timeout ao carregar {GOOGLE_FLOW_URL}: {exc}")

            auth = is_google_flow_authenticated(page, context=context)
            if not auth:
                context.close()
                return FlowInspectionReportDTO(
                    authenticated=False,
                    account_identifier=None,
                    active_project_title=None,
                    total_online_scenes=0,
                    synced_to_disk=0,
                    pending_download=0,
                    scenes=[],
                )

            # Extrair identificador de conta
            account_ident = None
            try:
                avatar = page.query_selector(
                    'a[aria-label*="Google Account"], img[alt*="Google Account"], [aria-label*="Conta do Google"], button[aria-label*="Google Account"]'
                )
                if avatar:
                    account_ident = avatar.get_attribute("aria-label") or avatar.get_attribute("alt")
            except Exception:
                pass

            # Extrair título do projeto ou workspace ativo
            project_title = None
            try:
                title_elem = page.query_selector('h1, [data-testid*="project-title"], [class*="project-title"]')
                if title_elem:
                    project_title = title_elem.inner_text().strip()
                if not project_title:
                    project_title = page.title()
            except Exception:
                project_title = page.title()

            # Capturar screenshot se solicitado
            if save_screenshot_path:
                save_screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(save_screenshot_path))
                logger.info(f"Screenshot salvo em: {save_screenshot_path}")

            # Extrair cards de vídeo / tomadas criadas no DOM
            raw_items = []
            try:
                cards = page.query_selector_all(
                    'div[data-card-id], div[data-testid*="card"], div[data-testid*="video"], '
                    'div[data-node-id], div[class*="flow-node"], div[class*="generation-card"], '
                    'div[class*="video-card"], div[role="article"]:has(video), video'
                )
                for idx, card in enumerate(cards):
                    card_text = card.inner_text() if hasattr(card, "inner_text") else ""
                    video_elem = card if card.evaluate("el => el.tagName.toLowerCase() === 'video'") else card.query_selector("video")
                    src = ""
                    if video_elem:
                        src = video_elem.get_attribute("src") or video_elem.evaluate("el => el.currentSrc || ''")

                    raw_items.append({
                        "card_id": f"card_{idx + 1}",
                        "title": card_text or f"Scene Card {idx + 1}",
                        "video_src": src,
                        "status": "ready" if src else "generating",
                    })
            except Exception as exc:
                logger.warning(f"Erro ao extrair elementos visuais do DOM: {exc}")

            context.close()
            return self.reconcile_scenes(
                raw_items=raw_items,
                authenticated=True,
                account=account_ident,
                project=project_title,
            )


if __name__ == "__main__":
    inspector = GoogleFlowInspector()
    print("Iniciando inspeção...")
    rep = inspector.inspect_online_session(
        headless=True,
        save_screenshot_path=DATA_DIR / "flow_inspection_current.png",
    )
    print(f"Autenticado: {rep.authenticated}")
    print(f"Conta: {rep.account_identifier}")
    print(f"Projeto: {rep.active_project_title}")
    print(f"Total Cenas Online: {rep.total_online_scenes}")
    print(f"Sincronizados em Disco: {rep.synced_to_disk}")
    print(f"Pendentes de Download: {rep.pending_download}")
