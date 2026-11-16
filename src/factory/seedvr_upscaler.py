#!/usr/bin/env python3
"""DarkFactory SeedVR 2.5 4K Historical Photo Upscaler & Enhancement Engine.

Performs 4K (3840x2160 UHD) upscaling, de-noising, and micro-contrast restoration
on declassified archival photographs and historical ground-truth stills:
1. High-Fidelity Local Processing: Lanczos4 4K resampling, CLAHE micro-contrast
   equalization in LAB color space, unsharp masking, and analog 35mm film grain.
2. RunningHub Cloud Automation Hook: Prepared for SeedVR 2.5 ComfyUI workflow execution.
3. Atomic disk persistence and full offline test suite support.
"""
from __future__ import annotations

import logging
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

# Reconfigure stdout/stderr to UTF-8 on Windows consoles (ADR-01)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("seedvr_upscaler")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_4K_IMAGES_DIR = DATA_DIR / "final" / "images_4k"


@dataclass
class UpscaleResult:
    """Output contract for SeedVR 2.5 upscaler results."""
    success: bool
    output_path: Path
    input_path: Path
    original_size: Tuple[int, int]
    target_size: Tuple[int, int]
    mode: str
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output_path": self.output_path.as_posix(),
            "input_path": self.input_path.as_posix(),
            "original_size": self.original_size,
            "target_size": self.target_size,
            "mode": self.mode,
            "error": self.error,
        }


class SeedVR25Upscaler:
    """Upscaler engine for archival historical photography (Local 4K + SeedVR 2.5 hook)."""

    def __init__(
        self,
        output_dir: Optional[Path | str] = None,
        prefer_cloud: bool = False,
    ) -> None:
        self.output_dir = Path(output_dir).resolve() if output_dir else DEFAULT_4K_IMAGES_DIR.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prefer_cloud = prefer_cloud

    def is_cloud_available(self) -> bool:
        """Returns True if RunningHub credentials or workflow for SeedVR 2.5 are configured."""
        api_key = os.getenv("RUNNINGHUB_API_KEY", "").strip()
        workflow_id = os.getenv("RUNNINGHUB_SEEDVR_WORKFLOW_ID", "").strip()
        return bool(api_key and workflow_id)

    def upscale_image(
        self,
        input_image_path: str | Path,
        output_image_path: Optional[str | Path] = None,
        target_width: int = 3840,
        target_height: int = 2160,
        dry_run: bool = False,
        denoise: bool = True,
        grain_strength: float = 0.08,
        preserve_aspect_ratio: bool = True,
    ) -> UpscaleResult:
        """Upscales historical photo to 4K UHD with micro-contrast and archival grain.

        Args:
            input_image_path: Path to input archival photograph.
            output_image_path: Destination path for 4K image (auto-named if None).
            target_width: Target resolution width (default 3840 for 4K 16:9).
            target_height: Target resolution height (default 2160 for 4K 16:9).
            dry_run: If True, writes lightweight sample without heavy compute.
            denoise: Whether to apply edge-preserving bilateral filtering.
            grain_strength: Standard deviation factor for subtle 35mm grain.
            preserve_aspect_ratio: Whether to center-crop non-standard aspect ratios to eliminate stretch distortion.
        """
        in_path = Path(input_image_path).resolve()
        if not in_path.exists():
            return UpscaleResult(
                success=False,
                output_path=Path(""),
                input_path=in_path,
                original_size=(0, 0),
                target_size=(target_width, target_height),
                mode="none",
                error=f"Input image not found: {in_path}",
            )

        if output_image_path:
            out_path = Path(output_image_path).resolve()
        else:
            out_stem = f"{in_path.stem}_4k_seedvr"
            out_path = self.output_dir / f"{out_stem}.jpg"

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            # Measure actual original dimensions if possible
            orig_size = (target_width, target_height)
            try:
                with Image.open(in_path) as im:
                    orig_size = im.size
            except Exception:
                pass

            # Create a 4K placeholder quickly for dry-run / rapid testing
            img_dry = np.full((target_height, target_width, 3), 24, dtype=np.uint8)
            cv2.putText(
                img_dry,
                f"DRY RUN 4K ARCHIVAL: {in_path.name}",
                (80, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.0,
                (220, 220, 220),
                4,
                cv2.LINE_AA,
            )
            cv2.imwrite(str(out_path), img_dry, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return UpscaleResult(
                success=True,
                output_path=out_path,
                input_path=in_path,
                original_size=orig_size,
                target_size=(target_width, target_height),
                mode="dry_run",
            )

        # High-Fidelity Local Upscale
        try:
            # Read image using OpenCV
            img_bgr = cv2.imread(str(in_path))
            if img_bgr is None:
                # Fallback to PIL
                pil_img = Image.open(in_path).convert("RGB")
                img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            orig_h, orig_w = img_bgr.shape[:2]

            # Aspect ratio preservation via cinematic center-crop
            if preserve_aspect_ratio and target_width > 0 and target_height > 0:
                target_aspect = target_width / target_height
                current_aspect = orig_w / orig_h
                if abs(current_aspect - target_aspect) > 0.005:
                    if current_aspect > target_aspect:
                        # Wider than target (e.g. 21:9): center crop horizontal margins
                        crop_w = int(round(orig_h * target_aspect))
                        crop_w = max(1, min(crop_w, orig_w))
                        offset_x = (orig_w - crop_w) // 2
                        img_bgr = img_bgr[:, offset_x:offset_x + crop_w]
                    else:
                        # Taller than target (e.g. 4:3, 1:1, 9:16): center crop vertical margins
                        crop_h = int(round(orig_w / target_aspect))
                        crop_h = max(1, min(crop_h, orig_h))
                        offset_y = (orig_h - crop_h) // 2
                        img_bgr = img_bgr[offset_y:offset_y + crop_h, :]

            # 1. Edge-preserving smoothing / denoising
            if denoise:
                img_bgr = cv2.bilateralFilter(img_bgr, d=5, sigmaColor=35, sigmaSpace=35)

            # 2. Lanczos4 High-Order Interpolation to 4K UHD
            upscaled = cv2.resize(
                img_bgr,
                (target_width, target_height),
                interpolation=cv2.INTER_LANCZOS4,
            )

            # 3. LAB Color Space CLAHE Micro-Contrast Enhancement
            lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l_channel)
            lab_enhanced = cv2.merge((l_enhanced, a_channel, b_channel))
            enhanced_bgr = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

            # 4. Unsharp Masking for Archival Crisp Edges
            gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), sigmaX=1.5)
            sharpened = cv2.addWeighted(enhanced_bgr, 1.25, gaussian, -0.25, 0)

            # 5. Subtle 35mm Analog Film Grain Simulation
            if grain_strength > 0:
                noise = np.random.normal(0, grain_strength * 25, sharpened.shape).astype(np.float32)
                grained = np.clip(sharpened.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            else:
                grained = sharpened

            # Atomic save via temporary file preserving extension for cv2.imwrite
            ext = out_path.suffix if out_path.suffix else ".jpg"
            tmp_out = out_path.with_name(f"{out_path.stem}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}{ext}")
            saved = cv2.imwrite(str(tmp_out), grained, [cv2.IMWRITE_JPEG_QUALITY, 96])
            if not saved:
                Image.fromarray(cv2.cvtColor(grained, cv2.COLOR_BGR2RGB)).save(str(tmp_out), quality=96)
            tmp_out.replace(out_path)

            logger.info(
                f"Successfully upscaled '{in_path.name}' ({orig_w}x{orig_h}) "
                f"-> 4K UHD ({target_width}x{target_height}) at {out_path.name}"
            )
            return UpscaleResult(
                success=True,
                output_path=out_path,
                input_path=in_path,
                original_size=(orig_w, orig_h),
                target_size=(target_width, target_height),
                mode="local_lanczos4_clahe",
            )
        except Exception as exc:
            logger.error(f"Error upscaling image {in_path}: {exc}")
            return UpscaleResult(
                success=False,
                output_path=out_path,
                input_path=in_path,
                original_size=(0, 0),
                target_size=(target_width, target_height),
                mode="failed",
                error=str(exc),
            )
