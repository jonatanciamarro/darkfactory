#!/usr/bin/env python3
"""DarkFactory Post-Production & Global YouTube Distribution Runner.

Executes final post-production steps for the 14-minute Master Documentary:
1. Generates 3 Viral 9:16 Vertical Funnel Shorts (with blurred backdrops & burnt subtitles).
2. Executes YouTube Algorithm Booster (7-language SEO, chapter markers, pinned engagement, A/B thumbnails).
3. Executes YouTube Compliance QC (100% Green Dollar certification, EDSA protection, Legal Dispute Kit).
4. Exports synchronized distribution manifest.
"""
import json
import logging
import os
import sys
from pathlib import Path

# ADR-01: UTF-8 encoding guard
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DistributionRunner")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shorts_generator import generate_funnel_shorts_package
from src.youtube_algorithm_booster import YouTubeAlgorithmBooster
from src.youtube_compliance_qc import YouTubeComplianceQC

def main():
    logger.info("🎬 Starting DarkFactory Full Episode Post-Production & Distribution...")

    master_video = PROJECT_ROOT / "data" / "output" / "the_1983_soviet_glitch_final_1080p.mp4"
    srt_file = PROJECT_ROOT / "data" / "subtitles" / "pilot_intro_mastered.srt"
    shorts_dir = PROJECT_ROOT / "data" / "output" / "shorts"
    shorts_dir.mkdir(parents=True, exist_ok=True)

    if not master_video.exists():
        logger.error(f"Master video not found at: {master_video}")
        sys.exit(1)

    video_duration = 834.77  # 13.91 minutes

    # 1. Generate 3 Funnel Vertical Shorts
    logger.info("📱 [Step 1/3] Generating 3 High-Retention 9:16 Vertical Funnel Shorts...")
    shorts_results = generate_funnel_shorts_package(
        video_input=master_video,
        master_video_id="soviet_glitch_master_001",
        srt_input=srt_file,
        output_dir=shorts_dir,
    )
    manifest_file = shorts_dir / "shorts_manifest.json"
    manifest_file.write_text(json.dumps(shorts_results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"✅ Generated {len(shorts_results)} vertical shorts and saved manifest.")

    # 2. Execute YouTube Algorithm Booster
    logger.info("🚀 [Step 2/3] Running YouTube Algorithm & Global SEO Booster...")
    title_en = "The 1983 Soviet Glitch: The Midnight World War 3 Almost Began"
    desc_en = (
        "On September 26, 1983, inside Serpukhov-15, Soviet early-warning computers flashed: "
        "'LAUNCH'. Five American nuclear missiles were reported inbound. One man, Stanislav Petrov, "
        "had 20 minutes to decide whether to trigger World War III.\n\n"
        "🏛️ HISTORICAL ARCHIVAL RECREATION: This documentary incorporates educational "
        "historical simulations and procedural synthetic visuals strictly for historical education, "
        "academic research, and archival reenactment under Fair Use guidelines."
    )
    booster = YouTubeAlgorithmBooster()
    algo_pkg = booster.build_complete_algorithm_package(
        project_id="the_1983_soviet_glitch",
        english_title=title_en,
        english_description=desc_en,
        video_duration_sec=video_duration,
        base_srt_file=srt_file if srt_file.exists() else None,
        master_video_id="soviet_glitch_master_001",
    )
    logger.info("✅ YouTube Algorithm Package exported with 7 languages, chapters, and A/B thumbnails.")

    # 3. Execute YouTube Compliance QC
    logger.info("🛡️ [Step 3/3] Running YouTube Compliance & Green Dollar QC Audit...")
    qc = YouTubeComplianceQC()
    qc_report = qc.evaluate_full_episode(
        project_id="the_1983_soviet_glitch",
        title=title_en,
        description=desc_en,
        tags=["cold war", "stanislav petrov", "1983 nuclear incident", "military history", "declassified documentary"],
        video_path=master_video,
        thumbnail_path=None,
    )
    report_dict = qc_report.to_dict()
    qc_file = PROJECT_ROOT / "data" / "processed" / "compliance_report.json"
    qc_file.parent.mkdir(parents=True, exist_ok=True)
    qc_file.write_text(json.dumps(report_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"✅ Compliance Report: Green Dollar = {report_dict.get('green_dollar_eligible')}, Score = {report_dict.get('compliance_score')}")

    logger.info("🎉 Post-production & Distribution phase completed successfully!")

if __name__ == "__main__":
    main()
