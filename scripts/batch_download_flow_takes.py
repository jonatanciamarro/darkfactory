#!/usr/bin/env python3
"""Batch download takes from Google Flow project filmstrip."""
import json
import logging
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BatchDownloader")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BROLL_DIR = DATA_DIR / "broll"
BROLL_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR = PROJECT_ROOT / "chrome_session" / "google_flow"
PROJECT_URL = "https://flow.google.com/project/6300d30f-ac56-46c3-8bde-356264377336"

# Coordenadas X dos 24 takes encontrados no filmstrip
THUMB_X_COORDS = [
    441, 471, 501, 531, 561, 591, 621, 651, 
    681, 711, 741, 771, 801, 831, 861, 891, 
    921, 951, 981, 1011, 1041, 1071, 1101, 1131
]

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(PROJECT_URL, wait_until="domcontentloaded", timeout=45000)
    time.sleep(4)
    page.keyboard.press("Escape")
    time.sleep(1)

    # Abrir o editor
    page.mouse.click(380, 280)
    time.sleep(3)

    downloaded = []
    
    # Baixar takes sequencialmente
    for idx, x_pos in enumerate(THUMB_X_COORDS, 1):
        target_file = BROLL_DIR / f"flow_take_{idx:02d}.mp4"
        if target_file.exists() and target_file.stat().st_size > 500000:
            logger.info(f"Take {idx:02d} já existe localmente ({target_file.stat().st_size} bytes). Pulando...")
            downloaded.append({"take": idx, "file": str(target_file), "status": "cached"})
            continue

        logger.info(f"Selecionando Take #{idx:02d} nas coordenadas ({x_pos}, 38)...")
        page.mouse.click(x_pos, 38)
        time.sleep(2)

        # Capturar título/prompt
        title = page.evaluate("() => document.querySelector('h1, h2, [class*=\"title\"]')?.innerText || ''")
        logger.info(f"Take #{idx:02d}: '{title}'")

        # Acionar download
        try:
            dl_btn = page.query_selector('button[aria-label*="Baixar mídia"], button[aria-label*="Fazer o download"]')
            if not dl_btn:
                logger.warning(f"Botão de download não encontrado no take {idx:02d}")
                continue

            dl_btn.click()
            time.sleep(1)

            opt_720p = page.query_selector('text="720p"')
            if opt_720p:
                with page.expect_download(timeout=25000) as dl_info:
                    opt_720p.click()
                dl = dl_info.value
                dl.save_as(str(target_file))
                logger.info(f"✅ Download Take #{idx:02d} concluído: {target_file.name} ({target_file.stat().st_size} bytes)")
                downloaded.append({"take": idx, "file": str(target_file), "title": title, "status": "downloaded"})
            else:
                logger.warning(f"Opção 720p não visível para take {idx:02d}")
        except Exception as exc:
            logger.warning(f"Erro ao baixar take #{idx:02d}: {exc}")

    print("\nRESUMO DO DOWNLOAD EM LOTE:")
    print(json.dumps(downloaded, indent=2, ensure_ascii=False))

    ctx.close()
