#!/usr/bin/env python3
"""DarkFactory RunningHub MMAudio & Tactical Foley Engine.

Automates Foley and sound design generation for DarkFactory historical documentaries:
1. Platform RPA Mode (RunningHub MMAudio):
   - Opens persistent Playwright session connecting to RunningHub.
   - If not authenticated, opens a visible browser window for one-time login.
   - Navigates to MMAudio workflow (ID: 2119239526823604226).
   - Injects tactical foley prompt from data/scripts/runninghub_mmaudio_prompts.json.
   - Triggers execution using the mandatory Lite/Plus tier (ADR-08).
   - Downloads generated audio and saves directly to expected audio folder.
2. Free Instant Alternative (Tactical Cold War Military Foley Suite):
   - 100% free, offline, instant generation without login or GPU costs.
   - Synthesizes stochastic Geiger counter clicks, CRT flyback hum, Bakelite telephone clack,
     heavy industrial toggle switches, and distant bunker emergency klaxons.
   - Broadcast-standard 44.1kHz 16-bit stereo WAV.
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import math
import os
import struct
import sys
import time
import wave
from pathlib import Path
from typing import Optional

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RunningHubFoleyBot")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
AUDIO_DIR = DATA_DIR / "audio"
SESSION_DIR = PROJECT_ROOT / "chrome_session" / "runninghub"

DEFAULT_FOLEY_PROMPT = (
    "Emergency red alarm klaxon sounding inside reinforced concrete military bunker, "
    "muffled repeating siren, 50Hz electrical transformer hum, vintage Bakelite telephone handling, "
    "stochastic Geiger counter clicks, tactile industrial toggle switches, high tension Cold War atmosphere"
)


def generate_free_tactical_foley(
    output_path: Path,
    duration: float = 45.0,
    sample_rate: int = 44100
) -> Path:
    """
    Synthesizes authentic Cold War military bunker sound design:
    - 50Hz USSR power grid / CRT flyback monitor electromagnetic hum with odd harmonics.
    - Stochastic Poisson Geiger counter clicks (simulating radiation sensor anomaly).
    - Heavy Bakelite telephone pick-up and cradle contact clack.
    - Tactile industrial spring-loaded toggle switch clank.
    - Pulsating emergency alarm siren wail (low volume, distant chamber reverb).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(sample_rate * duration)

    import numpy as np

    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 1. 50Hz CRT / Power Grid Electromagnetic Hum (50Hz, 100Hz, 150Hz)
    hum_50 = 0.08 * np.sin(2.0 * np.pi * 50.0 * t)
    hum_100 = 0.04 * np.sin(2.0 * np.pi * 100.0 * t)
    hum_150 = 0.02 * np.sin(2.0 * np.pi * 150.0 * t)
    # Subtle CRT high-frequency flyback line hum (15.625 kHz)
    crt_flyback = 0.015 * np.sin(2.0 * np.pi * 15625.0 * t)
    hum = hum_50 + hum_100 + hum_150 + crt_flyback

    # 2. Stochastic Poisson Geiger Counter Clicks (avg 18 clicks per second)
    clicks = np.zeros(num_samples)
    click_prob = 18.0 / sample_rate
    click_indices = np.where(np.random.rand(num_samples) < click_prob)[0]
    click_len = int(sample_rate * 0.0015)  # 1.5ms pulse
    for idx in click_indices:
        if idx + click_len < num_samples:
            pulse = np.random.uniform(0.15, 0.45) * np.exp(-np.linspace(0, 12, click_len))
            clicks[idx:idx + click_len] += pulse

    # 3. Tactile Industrial Toggle Switch Throw at 1.5s, 14.0s, 28.0s
    switch_track = np.zeros(num_samples)
    switch_times = [1.5, 14.0, 28.0]
    switch_dur = int(sample_rate * 0.08)
    for st in switch_times:
        s_idx = int(st * sample_rate)
        if s_idx + switch_dur < num_samples:
            s_t = np.linspace(0, 0.08, switch_dur)
            click_thud = 0.6 * np.exp(-s_t * 60.0) * np.sin(2.0 * np.pi * 220.0 * s_t)
            metallic_ping = 0.3 * np.exp(-s_t * 30.0) * np.sin(2.0 * np.pi * 1850.0 * s_t)
            switch_track[s_idx:s_idx + switch_dur] += (click_thud + metallic_ping)

    # 4. Distant Muffled Emergency Bunker Siren (wavering 320Hz to 480Hz)
    siren_mod = 0.5 * (1.0 + np.sin(2.0 * np.pi * 0.25 * t))
    siren_freq = 340.0 + 120.0 * siren_mod
    siren_phase = 2.0 * np.pi * np.cumsum(siren_freq) / sample_rate
    # Muffled low-pass filter simulation
    siren = 0.09 * siren_mod * np.sin(siren_phase)

    # 5. Room Tone & Air Handler White Noise (deep concrete chamber)
    room_tone = 0.02 * np.random.normal(0, 1, num_samples)

    # Composite mix
    composite = hum + clicks + switch_track + siren + room_tone

    # Normalize to -3 dBFS
    max_val = np.max(np.abs(composite))
    if max_val > 0.001:
        composite = (composite / max_val) * 0.72

    # Stereo widening
    left_channel = composite
    right_shift = int(sample_rate * 0.008)  # 8ms offset
    right_channel = np.roll(composite, right_shift)
    right_channel[:right_shift] = 0

    left_16 = np.int16(left_channel * 32767)
    right_16 = np.int16(right_channel * 32767)
    stereo = np.empty((num_samples * 2,), dtype=np.int16)
    stereo[0::2] = left_16
    stereo[1::2] = right_16

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())

    logger.info(f"Generated Free Tactical Foley: {output_path.name} ({duration:.1f}s, Geiger + CRT + Switches)")
    return output_path


def get_browser_launch_kwargs() -> dict:
    """Finds best browser executable (system Google Chrome, Edge, or Playwright default)."""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in chrome_paths:
        if os.path.isfile(c):
            return {"executable_path": c}
    return {}


class RunningHubFoleyBot:
    """Automates RunningHub MMAudio Foley generation with stealth session and free fallback."""

    def __init__(self, session_dir: Optional[Path] = None):
        self.session_dir = session_dir or SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def generate_foley(
        self,
        output_path: Path,
        prompt: Optional[str] = None,
        duration: float = 45.0,
        mode: str = "auto",
        headed: bool = False
    ) -> Path:
        """
        Generates tactical documentary Foley:
        - If mode == 'platform' or ('auto' and cookies exist/headed requested):
          attempts RunningHub MMAudio Playwright automation.
        - If platform is unavailable or mode == 'free':
          generates authentic tactical Cold War foley instantly.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        foley_prompt = prompt or self._load_prompt()

        if mode == "free":
            error_report = {
                "service": "RunningHub MMAudio (Foley)",
                "status": "ERROR",
                "error_type": "OFFLINE_FALLBACK_DISABLED",
                "message": "O fallback offline (síntese matemática de Foley) foi desativado.",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "target_file": str(output_path),
            }
            logger.error("🛑 [FALHA ESTRUTURADA DE FOLEY]:\n%s", json.dumps(error_report, indent=2, ensure_ascii=False))
            raise RuntimeError(error_report["message"])

        if mode in ("platform", "auto"):
            success = self._run_playwright_runninghub(
                prompt=foley_prompt,
                output_path=output_path,
                headed=headed
            )
            if success and output_path.exists() and output_path.stat().st_size > 1000:
                logger.info(f"✅ Successfully captured RunningHub MMAudio track: {output_path.name}")
                return output_path

        # Hard Gate: Erro estruturado ao invés de fallback offline de síntese local
        quarantine_dir = DATA_DIR / "quarantine" / f"foley_fail_{int(time.time())}"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        error_report = {
            "service": "RunningHub MMAudio (Foley)",
            "status": "ERROR",
            "error_type": "PLATFORM_GENERATION_FAILED",
            "message": "Falha na geração de Foley tático via RunningHub MMAudio. O fallback offline foi permanentemente desativado.",
            "prompt": foley_prompt,
            "target_duration_sec": duration,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "output_target": str(output_path),
        }
        report_file = quarantine_dir / "quarantine_report.json"
        report_file.write_text(json.dumps(error_report, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.error("🛑 [FALHA ESTRUTURADA DE FOLEY]:\n%s", json.dumps(error_report, indent=2, ensure_ascii=False))
        raise RuntimeError(
            f"FALHA NA GERAÇÃO DE FOLEY: RunningHub MMAudio indisponível ou falhou ao capturar áudio. "
            f"Fallback offline procedimental foi permanentemente desativado. "
            f"Log estruturado registrado em: {report_file}"
        )

    def _load_prompt(self) -> str:
        prompt_file = SCRIPTS_DIR / "runninghub_mmaudio_prompts.json"
        if prompt_file.exists():
            try:
                data = json.loads(prompt_file.read_text(encoding="utf-8"))
                scenes = data.get("scenes", [])
                if scenes:
                    return scenes[0].get("mmaudio_prompt", DEFAULT_FOLEY_PROMPT)
            except Exception:
                pass
        return DEFAULT_FOLEY_PROMPT

    def _run_playwright_runninghub(
        self,
        prompt: str,
        output_path: Path,
        headed: bool = False
    ) -> bool:
        """
        Launches Playwright session against RunningHub MMAudio workflow:
        - Reuses persistent context or cookies.
        - Enforces ADR-08: Execution tier MUST be Lite/Plus (middle button).
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed in environment. Falling back to free foley engine.")
            return False

        logger.info(f"Initiating RunningHub MMAudio automation (headed={headed})...")
        user_data_dir = self.session_dir / "user_data"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        try:
            with sync_playwright() as p:
                launch_opts = {
                    "user_data_dir": str(user_data_dir),
                    "headless": not headed,
                    "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                }
                launch_opts.update(get_browser_launch_kwargs())
                context = p.chromium.launch_persistent_context(**launch_opts)
                page = context.new_page()
                page.set_default_timeout(30000)

                url = "https://www.runninghub.ai/pt-br/workflow/2119239526823604226"
                logger.info(f"Navigating to {url}...")
                page.goto(url, wait_until="domcontentloaded")

                if headed:
                    print("\n" + "=" * 65)
                    print("🔐 MODO DE LOGIN INTERATIVO ATIVADO (RUNNINGHUB)")
                    print("   1. Faça login na sua conta RunningHub na janela do Chrome.")
                    print("   2. Navegue até o workflow MMAudio se necessário.")
                    print("   3. Quando estiver pronto, pressione [ENTER] aqui no terminal.")
                    print("   (A janela NÃO fechará até você pressionar ENTER!)")
                    print("=" * 65 + "\n")
                    try:
                        input("👉 Pressione [ENTER] aqui no terminal assim que concluir o login...")
                    except (EOFError, KeyboardInterrupt):
                        pass
                    print("\n🔄 Login confirmado! Prosseguindo...\n")
                else:
                    login_btn = page.query_selector("button:has-text('Sign In'), button:has-text('Entrar'), button:has-text('Login')")
                    if login_btn:
                        logger.info("RunningHub requires login. Relaunch with --headed to log in and save cookies.")
                        context.close()
                        return False

                # Intercept audio responses
                captured_audio = {"bytes": None, "url": None}

                def on_foley_response(res):
                    try:
                        u = res.url.lower()
                        ct = (res.headers.get("content-type") or "").lower()
                        if any(ext in u for ext in [".wav", ".mp3", ".flac", ".ogg"]) or "audio/" in ct:
                            body = res.body()
                            if len(body) > 20000:
                                captured_audio["bytes"] = body
                                captured_audio["url"] = res.url
                                logger.info(f"🎧 [Rede] Foley capturado: {len(body)} bytes ({res.url[:70]})")
                    except Exception:
                        pass

                page.on("response", on_foley_response)

                # Locate prompt input and inject
                text_input = page.query_selector("textarea, input[placeholder*='prompt' i]")
                if text_input:
                    text_input.click()
                    time.sleep(0.3)
                    text_input.fill("")
                    text_input.type(prompt, delay=10)
                    time.sleep(1.0)

                    # Trigger Lite/Plus execution (ADR-08: Standard button is prohibited)
                    lite_plus_btn = page.query_selector("button:has-text('Lite'), button:has-text('Plus'), button:has-text('Run (Lite)')")
                    if lite_plus_btn:
                        lite_plus_btn.click()
                        logger.info("Triggered execution on RunningHub via Lite/Plus tier (ADR-08)...")

                        start_wait = time.time()
                        while time.time() - start_wait < 90.0:
                            time.sleep(3.0)
                            if captured_audio["bytes"]:
                                output_path.write_bytes(captured_audio["bytes"])
                                logger.info(f"✅ Foley saved from network stream: {output_path.name}")
                                try:
                                    from src.factory.runninghub_bot import cancel_runninghub_task
                                    logger.info("🛑 Cancelando workflow MMAudio no RunningHub para economizar créditos GPU...")
                                    cancel_runninghub_task(page)
                                except Exception as exc:
                                    logger.debug(f"Aviso ao cancelar MMAudio: {exc}")
                                context.close()
                                return True

                            audio_el = page.query_selector("audio")
                            if audio_el:
                                src = audio_el.get_attribute("src")
                                if src and src.startswith("http"):
                                    import urllib.request
                                    urllib.request.urlretrieve(src, str(output_path))
                                    logger.info(f"✅ Foley salvo via URL: {output_path.name}")
                                    try:
                                        from src.factory.runninghub_bot import cancel_runninghub_task
                                        logger.info("🛑 Cancelando workflow MMAudio no RunningHub para economizar créditos GPU...")
                                        cancel_runninghub_task(page)
                                    except Exception as exc:
                                        logger.debug(f"Aviso ao cancelar MMAudio: {exc}")
                                    context.close()
                                    return True

                context.close()
                return False

        except Exception as e:
            logger.warning(f"RunningHub MMAudio automation error: {e}. Falling back to free foley engine.")
            return False


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory RunningHub MMAudio & Free Tactical Foley Engine")
    parser.add_argument("--output", type=str, default=str(AUDIO_DIR / "procedural_foley_stem.wav"), help="Target audio file path")
    parser.add_argument("--prompt", type=str, default=None, help="Custom foley prompt")
    parser.add_argument("--duration", type=float, default=45.0, help="Duration in seconds")
    parser.add_argument("--mode", choices=["auto", "platform", "free"], default="auto", help="Execution mode")
    parser.add_argument("--headed", action="store_true", help="Launch visible browser window for interactive login")
    args = parser.parse_args()

    bot = RunningHubFoleyBot()
    out = bot.generate_foley(
        output_path=Path(args.output),
        prompt=args.prompt,
        duration=args.duration,
        mode=args.mode,
        headed=args.headed,
    )
    print(f"\n🎉 Foley Ready at: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
