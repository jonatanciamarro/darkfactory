#!/usr/bin/env python3
"""DarkFactory Cinematic Video Renderer & Assembly Engine.

Renders and stitches the complete pilot documentary video:
1. Orchestrates Phase 3 T2V Dual-Engine Generation (Veo 3.1 & Omni Flash 1.2):
   - Shot A (Omni Flash 1.2): 12-15s Character Continuity Take (Stanislav Petrov in 1983 Soviet Uniform).
   - Shot B (Veo 3.1 4K): 6-8s Tactical Hero Macro Climax (CRT Radar Vectors, Soviet Clock, Cloud Glitch).
2. Dual-Shot Crosscutting: stitches Shot A + Shot B seamlessly across all scenes.
3. Applies smooth micro-transitions (0.15s dip-to-black cuts between scenes, 0.35s opening fade-in, 0.40s closing fade-out).
4. Employs a Cold War / Kodak 2383 historical documentary 3D LUT for cinematic grade (removes AI glossiness).
5. Adds 2.39:1 anamorphic cinema letterboxing (140px matte top and bottom).
6. Syncs scene visual durations frame-accurately with audio timestamps.
7. Binds mastered audio + procedural sound design mix (with opening sub-bass braam impact).
8. Burns in broadcast-standard documentary subtitles inside the lower letterbox matte.
9. Outputs final master to data/output/the_1983_soviet_glitch_final_1080p.mp4.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Force UTF-8 on Windows (ADR-01)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VideoRenderer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
AUDIO_DIR = DATA_DIR / "audio"
MASTERED_DIR = AUDIO_DIR / "mastered"
BROLL_DIR = DATA_DIR / "broll"
OUTPUT_DIR = DATA_DIR / "output"
SUBS_DIR = DATA_DIR / "subtitles"
LUTS_DIR = DATA_DIR / "luts"


def get_ffmpeg_binary() -> str:
    """Find a valid ffmpeg executable on the system or in the environment."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    candidates = [
        Path(r"C:\Users\WDAGUtilityAccount\Downloads\Nova pasta\stockcont\venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"),
        Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    raise FileNotFoundError("FFmpeg binary not found.")


def ensure_cinematic_lut() -> Path:
    """Ensure the historical documentary 3D LUT exists, generating if needed."""
    lut_path = LUTS_DIR / "cold_war_documentary.cube"
    if not lut_path.exists():
        try:
            from generate_cinematic_lut import create_historical_documentary_lut
            create_historical_documentary_lut(lut_path)
            logger.info(f"Generated missing 3D LUT at {lut_path}")
        except Exception as e:
            logger.warning(f"Could not auto-generate 3D LUT: {e}")
    return lut_path


def ensure_t2v_broll_consistency(force: bool = False) -> None:
    """Guarantees T2V Dual-Engine Generation (Veo 3.1 & Omni Flash 1.2) is run for character/clothing consistency."""
    from google_flow_bot import GoogleFlowBot
    omni_q = SCRIPTS_DIR / "google_flow_omni_queue.json"
    veo3_q = SCRIPTS_DIR / "google_flow_veo3_queue.json"

    if not omni_q.exists() or not veo3_q.exists():
        logger.info("Generating Google Flow queues from Nolan Screenplay...")
        try:
            from nolan_director import NolanHistoryDirector
            director = NolanHistoryDirector()
            director.direct_episode("1983 Soviet nuclear false alarm incident")
        except Exception as e:
            logger.warning(f"Could not auto-refresh Nolan queues: {e}")

    broll_videos = list(BROLL_DIR.glob("*.mp4")) + list(BROLL_DIR.glob("*.mov"))
    if force or len(broll_videos) < 3:
        logger.info("🎬 Phase 3: Triggering T2V Dual-Engine Generation (Veo 3.1 & Omni Flash 1.2) for character & costume consistency...")
        bot = GoogleFlowBot(broll_dir=BROLL_DIR)
        if omni_q.exists() and veo3_q.exists():
            bot.dispatch_flow_queues(omni_queue_file=omni_q, veo3_queue_file=veo3_q, dry_run=False)


def get_audio_duration(ffmpeg_bin: str, file_path: Path) -> float:
    """Probe audio duration in seconds."""
    cmd = [ffmpeg_bin, "-i", str(file_path), "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
            except Exception:
                break
    return 0.0


def create_procedural_broll_image(image_path: Path, scene_id: int, scene_title: str) -> None:
    """Fallback: Generates a high-tension character-consistent plate adhering to CharacterConsistencySpec."""
    from google_flow_bot import create_consistent_character_plate
    shot_type = "shot_b" if "b" in image_path.stem.lower() else "shot_a"
    create_consistent_character_plate(image_path, scene_id=scene_id, shot_type=shot_type, prompt=scene_title)


def render_scene_video(
    ffmpeg_bin: str,
    scene_id: int,
    duration: float,
    output_mp4: Path,
    is_first: bool = False,
    is_last: bool = False,
    transition_sec: float = 0.15,
) -> bool:
    """Renders a scene clip with adaptive speed-matching and micro-transitions.

    Supports dual-shot composition (Shot A: Omni Flash 1.2 Character + Shot B: Veo 3.1 Tactical Macro)
    for any scene where Beat B video (e.g. cena 1b.mp4, scene_2_b.mp4, scene_3_b.mp4) is present.
    If only one clip exists, dynamically stretches/compresses playback via setpts without ugly loops.
    """
    shot_b_candidates = [
        BROLL_DIR / f"cena {scene_id}b.mp4",
        BROLL_DIR / f"cena_{scene_id}b.mp4",
        BROLL_DIR / f"scene_{scene_id}_b.mp4",
        BROLL_DIR / f"scene_{scene_id}b.mp4",
        BROLL_DIR / f"cena {scene_id}b.mov",
        BROLL_DIR / f"scene_{scene_id}b.mov",
    ]
    shot_b_src = next((c for c in shot_b_candidates if c.is_file()), None)

    shot_a_candidates = [
        BROLL_DIR / f"cena {scene_id}.mp4",
        BROLL_DIR / f"cena_{scene_id}.mp4",
        BROLL_DIR / f"scene_{scene_id}.mp4",
        BROLL_DIR / f"scene {scene_id}.mp4",
        BROLL_DIR / f"cena {scene_id}.mov",
        BROLL_DIR / f"scene_{scene_id}.mov",
    ]
    fallback_a_imgs = [
        BROLL_DIR / f"scene_{scene_id}.jpg",
        BROLL_DIR / f"scene_{scene_id}.png",
        BROLL_DIR / f"cena_{scene_id}.jpg",
        BROLL_DIR / f"cena {scene_id}.jpg",
    ]

    if shot_b_src:
        t_split = round(duration * 0.55, 2)
        dur_a = t_split
        dur_b = max(1.0, duration - t_split)
        logger.info(f"🎬 Dual-Shot T2V detected for Scene {scene_id}! Shot {scene_id}A (Omni Flash 1.2 Character: {dur_a:.2f}s) + Shot {scene_id}B (Veo 3.1 Macro: {dur_b:.2f}s)")
        temp_a = OUTPUT_DIR / f"temp_scene_{scene_id}a.mp4"
        temp_b = OUTPUT_DIR / f"temp_scene_{scene_id}b.mp4"

        # Render Shot A (Omni Flash 1.2 Character continuity take)
        ok_a = render_single_clip(
            ffmpeg_bin=ffmpeg_bin,
            clip_candidates=shot_a_candidates,
            fallback_img_candidates=fallback_a_imgs,
            scene_id=scene_id,
            duration=dur_a,
            output_mp4=temp_a,
            is_first=is_first,
            is_last=False,
            transition_sec=transition_sec
        )
        # Render Shot B (Veo 3.1 4K Tactical Macro Climax)
        ok_b = render_single_clip(
            ffmpeg_bin=ffmpeg_bin,
            clip_candidates=[shot_b_src],
            fallback_img_candidates=[
                BROLL_DIR / f"scene_{scene_id}b.jpg",
                BROLL_DIR / f"scene_{scene_id}b.png",
                BROLL_DIR / f"scene_{scene_id}_b.jpg",
            ],
            scene_id=scene_id,
            duration=dur_b,
            output_mp4=temp_b,
            is_first=False,
            is_last=is_last,
            transition_sec=transition_sec
        )
        if ok_a and ok_b:
            concat_txt = OUTPUT_DIR / f"scene_{scene_id}_concat.txt"
            with open(concat_txt, "w", encoding="utf-8") as f:
                f.write(f"file '{temp_a.resolve().as_posix()}'\n")
                f.write(f"file '{temp_b.resolve().as_posix()}'\n")
            cmd_cat = [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(output_mp4)]
            res = subprocess.run(cmd_cat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
            if temp_a.exists(): temp_a.unlink()
            if temp_b.exists(): temp_b.unlink()
            if concat_txt.exists(): concat_txt.unlink()
            if res.returncode == 0:
                logger.info(f"✅ Successfully stitched Scene {scene_id} Dual-Shot (Shot {scene_id}A + Shot {scene_id}B)!")
                return True

    # Standard single clip render with speed matching
    return render_single_clip(
        ffmpeg_bin=ffmpeg_bin,
        clip_candidates=shot_a_candidates,
        fallback_img_candidates=fallback_a_imgs,
        scene_id=scene_id,
        duration=duration,
        output_mp4=output_mp4,
        is_first=is_first,
        is_last=is_last,
        transition_sec=transition_sec
    )


def render_single_clip(
    ffmpeg_bin: str,
    clip_candidates: List[Path],
    fallback_img_candidates: List[Path],
    scene_id: int,
    duration: float,
    output_mp4: Path,
    is_first: bool = False,
    is_last: bool = False,
    transition_sec: float = 0.15,
) -> bool:
    """Renders a single video clip or image with adaptive speed-matching and micro-transitions."""
    video_src = next((c for c in clip_candidates if c.is_file()), None)
    actual_img = next((c for c in fallback_img_candidates if c.is_file()), None)

    if not video_src and not actual_img:
        fallback_img = BROLL_DIR / f"scene_{scene_id}.jpg"
        create_procedural_broll_image(fallback_img, scene_id, f"Scene {scene_id}")
        actual_img = fallback_img

    fps = 30
    total_frames = int(max(2.0, duration) * fps)

    fade_in = 0.35 if is_first else transition_sec
    fade_out = 0.40 if is_last else transition_sec
    fade_filter = f"fade=t=in:st=0:d={fade_in:.2f},fade=t=out:st={duration - fade_out:.3f}:d={fade_out:.2f}"

    if video_src:
        src_dur = get_audio_duration(ffmpeg_bin, video_src)
        if src_dur > 0.5:
            pts_factor = duration / src_dur
            logger.info(
                f"Adaptive Speed-Matching for Scene {scene_id}: source {src_dur:.2f}s -> target {duration:.2f}s "
                f"(playback speed: {1.0/pts_factor:.2f}x, pts_factor={pts_factor:.4f})"
            )
            speed_filter = f"setpts={pts_factor:.4f}*PTS,"
        else:
            speed_filter = ""

        logger.info(f"Using live b-roll video for Scene {scene_id}: {video_src.name} (dur: {duration:.2f}s)")
        vf_pipeline = (
            f"{speed_filter}"
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"fps={fps},"
            f"{fade_filter},"
            f"format=yuv420p"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(video_src),
            "-t", f"{duration:.3f}",
            "-vf", vf_pipeline,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-an",
            str(output_mp4)
        ]
    else:
        logger.info(f"Applying Anamorphic Ken-Burns zoom on image: {actual_img.name} (dur: {duration:.2f}s)")
        zoom_expr = "min(zoom+0.0004,1.15)"
        vf_pipeline = (
            f"scale=8000:-1,"
            f"zoompan=z='{zoom_expr}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps},"
            f"{fade_filter},"
            f"format=yuv420p"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1",
            "-i", str(actual_img),
            "-t", f"{duration:.3f}",
            "-vf", vf_pipeline,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-r", str(fps),
            "-an",
            str(output_mp4)
        ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        logger.error(f"Scene {scene_id} render failed: {res.stderr}")
        return False
    return True


def assemble_final_video(
    ffmpeg_bin: str,
    scene_videos: List[Path],
    audio_file: Path,
    srt_file: Optional[Path],
    output_video: Path,
    apply_lut: bool = True,
    apply_letterbox: bool = True,
) -> bool:
    """Concatenates scene clips, applies 3D LUT grade & 2.39:1 letterbox, burns subtitles, muxes audio."""
    concat_list = OUTPUT_DIR / "video_concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for v in scene_videos:
            f.write(f"file '{v.resolve().as_posix()}'\n")

    temp_stitched = OUTPUT_DIR / "temp_stitched.mp4"
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(temp_stitched)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.info("Applying Historical Documentary Color Grade, 2.39:1 Cinema Letterbox & Subtitles...")
    vf_filters = []

    # 1. Historical Documentary Color Grade (3D LUT or fallback)
    if apply_lut:
        lut_path = ensure_cinematic_lut()
        if lut_path.is_file():
            lut_clean = lut_path.resolve().as_posix().replace(":", "\\:")
            vf_filters.append(f"lut3d=file='{lut_clean}'")
            logger.info("Using 3D LUT: Kodak 2383 / Cold War Bleach-Bypass profile.")
        else:
            fallback_grade = (
                "eq=contrast=1.10:brightness=-0.01:saturation=0.88,"
                "colorbalance=rs=-0.03:gs=0.03:bs=0.01:rh=0.03:gh=0.01:bh=-0.03"
            )
            vf_filters.append(fallback_grade)
            logger.info("Using native FFmpeg Colorbalance / Bleach-Bypass filter.")

    # 2. Cinema Letterbox (2.39:1 Anamorphic Scope = 140px black bars on 1080p canvas)
    if apply_letterbox:
        letterbox_cmd = "drawbox=x=0:y=0:w=iw:h=140:color=black:t=fill,drawbox=x=0:y=ih-140:w=iw:h=140:color=black:t=fill"
        vf_filters.append(letterbox_cmd)
        logger.info("Applied 2.39:1 Anamorphic Cinema Letterbox (140px top/bottom).")

    # 3. Subtitles burned cleanly inside the lower cinema letterbox bar
    if srt_file and srt_file.exists():
        srt_clean_path = srt_file.resolve().as_posix().replace(":", "\\:")
        subtitle_filter = (
            f"subtitles='{srt_clean_path}':"
            "force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,BorderStyle=1,Outline=2,"
            "Shadow=1,Alignment=2,MarginV=30'"
        )
        vf_filters.append(subtitle_filter)
        logger.info("Burning subtitles cleanly inside lower cinema letterbox matte.")

    vf_filters.append("format=yuv420p")
    vf_chain = ",".join(vf_filters)

    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", str(temp_stitched),
        "-i", str(audio_file),
        "-vf", vf_chain,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-shortest",
        str(output_video)
    ]

    res = subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        logger.error(f"Final assembly failed: {res.stderr}")
        return False

    if temp_stitched.exists():
        temp_stitched.unlink()

    logger.info(f"✅ Final video master rendered: {output_video.name}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Phase 3: T2V Dual-Engine & Master Video Assembly")
    parser.add_argument("--force-t2v", action="store_true", help="Force regenerate T2V B-roll clips")
    args = parser.parse_args()

    BROLL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LUTS_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_binary()
    logger.info(f"Using FFmpeg: {ffmpeg_bin}")

    # Ensure LUT is ready
    ensure_cinematic_lut()

    # 1. Phase 3 Step 1: Ensure T2V Dual-Engine Generation (Veo 3.1 & Omni Flash 1.2) for Character & Clothing Consistency
    ensure_t2v_broll_consistency(force=args.force_t2v)

    script_path = SCRIPTS_DIR / "pilot_soviet_glitch.json"
    if not script_path.exists():
        script_path = SCRIPTS_DIR / "nolan_soviet_glitch.json"
    if not script_path.exists():
        candidates = list(SCRIPTS_DIR.glob("*soviet_glitch.json"))
        if candidates:
            script_path = candidates[0]
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    logger.info(f"Rendering pilot documentary: {script_data.get('title')}")

    # Discover durations from mastered audio files
    durations = []
    for s in scenes:
        s_id = s["scene_id"]
        mastered_audio = MASTERED_DIR / f"scene_{s_id}_mastered.mp3"
        if not mastered_audio.exists():
            mastered_audio = AUDIO_DIR / f"scene_{s_id}.mp3"

        if mastered_audio.exists():
            d = get_audio_duration(ffmpeg_bin, mastered_audio)
            durations.append(d)
        else:
            durations.append(s.get("estimated_duration_sec", 12.0))

    rendered_scenes = []
    num_scenes = len(scenes)
    for idx, (s, dur) in enumerate(zip(scenes, durations)):
        s_id = s["scene_id"]
        scene_mp4 = OUTPUT_DIR / f"temp_scene_{s_id}.mp4"
        is_first = (idx == 0)
        is_last = (idx == num_scenes - 1)
        logger.info(f"Rendering Scene {s_id} video track ({dur:.2f}s) [first={is_first}, last={is_last}]...")
        success = render_scene_video(
            ffmpeg_bin=ffmpeg_bin,
            scene_id=s_id,
            duration=dur,
            output_mp4=scene_mp4,
            is_first=is_first,
            is_last=is_last,
            transition_sec=0.15
        )
        if success:
            rendered_scenes.append(scene_mp4)

    # Select final audio mix (with sound design & opening braam)
    final_audio = AUDIO_DIR / "pilot_final_audio_mix.mp3"
    if not final_audio.exists():
        final_audio = MASTERED_DIR / "pilot_intro_full_mastered.mp3"
    if not final_audio.exists():
        final_audio = AUDIO_DIR / "pilot_intro_full.mp3"

    # Select subtitles
    subtitles_file = SUBS_DIR / "pilot_intro_mastered.srt"
    if not subtitles_file.exists():
        subtitles_file = SUBS_DIR / "pilot_intro_full.srt"

    final_output = OUTPUT_DIR / "the_1983_soviet_glitch_final_1080p.mp4"

    logger.info("Assembling final video with LUT, Cinema Letterbox, Audio & Subtitles...")
    success = assemble_final_video(
        ffmpeg_bin=ffmpeg_bin,
        scene_videos=rendered_scenes,
        audio_file=final_audio,
        srt_file=subtitles_file,
        output_video=final_output,
        apply_lut=True,
        apply_letterbox=True
    )

    if success:
        # Clean up temporary scene mp4s and concat list
        for r in rendered_scenes:
            if r.exists():
                r.unlink()
        concat_list = OUTPUT_DIR / "video_concat_list.txt"
        if concat_list.exists():
            concat_list.unlink()

        size_mb = final_output.stat().st_size / (1024 * 1024)
        print(f"\n=======================================================")
        print(f"🎉 PILOT MASTER VIDEO COMPLETE!")
        print(f"   Output File: {final_output}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Resolution: 1920x1080 (2.39:1 Anamorphic Scope Letterbox)")
        print(f"   Color Grade: Cold War Kodak 2383 Bleach-Bypass 3D LUT")
        print(f"   Transitions: Micro Dip-to-Black (0.15s) Between Scenes")
        print(f"   Sound Design: Procedural Sub-Bass Braam Impact + Heartbeat + Sirens")
        print(f"   Subtitles: Matte Burned-in Broadcast Typography")
        print(f"=======================================================\n")


if __name__ == "__main__":
    main()
