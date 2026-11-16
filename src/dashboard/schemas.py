"""Pydantic Schemas for the DarkFactory Cinema Dashboard."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TopicTriggerRequest(BaseModel):
    """Payload to trigger an autonomous production cycle on a given historical topic."""
    topic: str = Field(..., min_length=3, description="Historical topic or mystery")
    dry_run: bool = Field(default=False, description="Simulate without real GPU/API costs")
    narrative_style: str = Field(default="nolan_crosscut", description="Narrative pacing archetype")


class ApprovalActionRequest(BaseModel):
    """Payload to approve or quarantine a documentary in the 1-Click queue."""
    video_id: str = Field(..., description="Episode/Video identifier")
    action: str = Field(..., description="'publish_unlisted' | 'publish_public' | 'reject_quarantine'")
    quarantine_notes: Optional[str] = Field(default=None, description="Reason if quarantined")
    selected_thumbnail: Optional[str] = Field(default="variant_a", description="Selected A/B/C thumbnail variant")


class PhaseRunRequest(BaseModel):
    """Payload to trigger a single modular pipeline phase."""
    phase: int = Field(..., ge=1, le=5, description="Phase number (1: Research, 2: Script, 3: Video, 4: Audio, 5: SEO/Pub)")
    topic: Optional[str] = Field(default=None, description="Topic override")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional phase flags")


class DaemonControlRequest(BaseModel):
    """Payload to control the 24/7 autonomous supervisor daemon."""
    action: str = Field(..., description="'start' | 'stop' | 'restart' | 'run_once'")


class ScreenplaySaveRequest(BaseModel):
    """Payload to manually edit or update a screenplay script."""
    topic: str
    screenplay_data: Dict[str, Any]


class AuthLoginRequest(BaseModel):
    """Payload to trigger interactive headful login for AI platforms."""
    target: str = Field(default="all", description="'all' | 'flow' | 'runninghub' | 'flowmusic'")


class TopicGenerateRequest(BaseModel):
    """Payload to request automatically generated compliant topics."""
    category: Optional[str] = Field(default=None, description="Optional category filter")
    count: int = Field(default=4, ge=1, le=12, description="Number of suggestions to return")
    seed_concept: Optional[str] = Field(default=None, description="Optional custom keyword to generate from")
