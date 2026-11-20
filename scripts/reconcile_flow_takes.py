#!/usr/bin/env python3
"""Map and reconcile downloaded Google Flow takes into canonical DarkFactory scene inventory."""
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ReconcileFlowTakes")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BROLL_DIR = PROJECT_ROOT / "data" / "broll"

# Mapeamento semântico dos 23 takes baixados para os slots faltantes da esteira
FLOW_MAPPING = {
    # Satélite Oko em órbita (Shot B Veo da Cena 3)
    "flow_take_07.mp4": "scene_3_b.mp4",
    # Close de olhos / suor de oficial (Shot B da Cena 4)
    "flow_take_05.mp4": "scene_4_b.mp4",
    # Oceano Ártico com placas de gelo (Cena 5 Shot A e Shot B)
    "flow_take_03.mp4": "scene_5.mp4",
    "flow_take_04.mp4": "scene_5_b.mp4",
    # Petrov gritando ordens (Cena 6 Shot A e Shot B)
    "flow_take_08.mp4": "scene_6.mp4",
    "flow_take_09.mp4": "scene_6_b.mp4",
    # Variação de olhos vermelhos (Cena 7 Shot B)
    "flow_take_06.mp4": "scene_7_b.mp4",
    # Técnicos reagindo em choque no bunker (Cena 9 Shot A)
    "flow_take_10.mp4": "scene_9.mp4",
    # Oficiais soviéticos em serviço em Serpukhov-15 (Cenas 10, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24)
    "flow_take_11.mp4": "scene_10.mp4",
    "flow_take_12.mp4": "scene_14.mp4",
    "flow_take_13.mp4": "scene_15.mp4",
    "flow_take_14.mp4": "scene_16.mp4",
    "flow_take_15.mp4": "scene_17.mp4",
    "flow_take_17.mp4": "scene_18.mp4",
    "flow_take_18.mp4": "scene_20.mp4",
    "flow_take_19.mp4": "scene_21.mp4",
    "flow_take_20.mp4": "scene_22.mp4",
    "flow_take_21.mp4": "scene_23.mp4",
    "flow_take_22.mp4": "scene_24.mp4",
}

mapped_count = 0
for src_name, dst_name in FLOW_MAPPING.items():
    src_file = BROLL_DIR / src_name
    dst_file = BROLL_DIR / dst_name
    if src_file.exists():
        if not dst_file.exists() or dst_file.stat().st_size < 100000:
            shutil.copy2(src_file, dst_file)
            logger.info(f"✅ Mapeado: {src_name} ➔ {dst_name} ({dst_file.stat().st_size} bytes)")
            mapped_count += 1
        else:
            logger.info(f"Slot {dst_name} já preenchido. Mantendo existente.")

print(f"\nTotal de tomadas reconciliadas no inventário: {mapped_count}")
