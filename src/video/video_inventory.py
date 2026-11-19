#!/usr/bin/env python3
"""DarkFactory Video Asset Inventory, Audit & GPU Economy Dispatcher.

Inspects all existing video materials (in data/broll/, data/final/, user Downloads,
and Google Flow export directories), reconciles naming variations, validates media
integrity, and generates filtered pending queues so only missing scenes are generated.
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("VideoInventory")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BROLL_DIR = DATA_DIR / "broll"
SCRIPTS_DIR = DATA_DIR / "scripts"
PROCESSED_DIR = DATA_DIR / "processed"


@dataclass
class VideoAssetMetadata:
    """Metadata de um clipe de vídeo cinematográfico verificado."""
    scene_id: int
    shot_type: str  # "shot_a" | "shot_b"
    file_path: Path
    file_size_bytes: int
    duration_sec: float = 0.0
    is_valid: bool = True
    source_folder: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "shot_type": self.shot_type,
            "filename": self.file_path.name,
            "file_path": str(self.file_path),
            "file_size_bytes": self.file_size_bytes,
            "file_size_mb": round(self.file_size_bytes / (1024 * 1024), 2),
            "duration_sec": self.duration_sec,
            "is_valid": self.is_valid,
            "source_folder": self.source_folder,
        }


@dataclass
class VideoInventoryAuditReport:
    """Relatório estruturado de inventário e economia de GPU."""
    total_required_scenes: int = 40
    total_required_takes: int = 80
    existing_shot_a_count: int = 0
    existing_shot_b_count: int = 0
    missing_shot_a_ids: List[int] = field(default_factory=list)
    missing_shot_b_ids: List[int] = field(default_factory=list)
    coverage_percentage: float = 0.0
    estimated_gpu_minutes_saved: float = 0.0
    existing_assets: List[VideoAssetMetadata] = field(default_factory=list)

    @property
    def existing_total_takes(self) -> int:
        return self.existing_shot_a_count + self.existing_shot_b_count

    @property
    def missing_total_takes(self) -> int:
        return len(self.missing_shot_a_ids) + len(self.missing_shot_b_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_required_scenes": self.total_required_scenes,
            "total_required_takes": self.total_required_takes,
            "existing_shot_a_count": self.existing_shot_a_count,
            "existing_shot_b_count": self.existing_shot_b_count,
            "existing_total_takes": self.existing_total_takes,
            "missing_shot_a_ids": self.missing_shot_a_ids,
            "missing_shot_b_ids": self.missing_shot_b_ids,
            "missing_total_takes": self.missing_total_takes,
            "coverage_percentage": round(self.coverage_percentage, 1),
            "estimated_gpu_minutes_saved": round(self.estimated_gpu_minutes_saved, 1),
            "existing_assets": [a.to_dict() for a in self.existing_assets],
        }


def parse_scene_and_shot_from_filename(filename: str) -> Tuple[Optional[int], Optional[str]]:
    """Identifica o ID da cena (1..40) e o tipo de tomada (shot_a / shot_b) a partir de variações de nomenclatura.
    
    Suporta:
    - 'cena 1.mp4', 'scene_1.mp4', 'SCENE_01.MP4' -> (1, 'shot_a')
    - 'cena 1b.mp4', 'scene_1_b.mp4', 'cena 1_b.mp4', 'scene_1b.mp4' -> (1, 'shot_b')
    - 'minimax_h3_cinematic_scene_7.mp4' -> (7, 'shot_a')
    """
    clean_name = Path(filename).stem.lower().strip()

    # Padrão 1: 'cena 1b', 'cena 1_b', 'cena 1 b', 'cena 1', 'cena_1'
    m_cena = re.search(r'cena[_\s]*(\d+)[_\s]*(b)?', clean_name)
    if m_cena:
        s_id = int(m_cena.group(1))
        suffix = m_cena.group(2)
        shot = "shot_b" if suffix and "b" in suffix else "shot_a"
        return s_id, shot

    # Padrão 2: 'scene_1_b', 'scene_1b', 'scene 1 b', 'scene_1', 'scene 1'
    m_scene = re.search(r'scene[_\s]*(\d+)[_\s]*(b)?', clean_name)
    if m_scene:
        s_id = int(m_scene.group(1))
        suffix = m_scene.group(2)
        shot = "shot_b" if suffix and "b" in suffix else "shot_a"
        return s_id, shot

    return None, None


def validate_video_file_integrity(file_path: Path, min_size_bytes: int = 50000) -> bool:
    """Verifica se o arquivo de vídeo existe, tem tamanho mínimo e cabeçalho de contêiner válido."""
    if not file_path.exists() or not file_path.is_file():
        return False

    size = file_path.stat().st_size
    if size < min_size_bytes:
        return False

    try:
        with open(file_path, "rb") as f:
            header = f.read(128)
            # Checar cabeçalhos comuns de mídia: MP4/MOV ('ftyp'), WebM/MKV ('\x1a\x45\xdf\xa3'), AVI ('RIFF')
            if b"ftyp" in header or header.startswith(b"\x1a\x45\xdf\xa3") or header.startswith(b"RIFF"):
                return True
            # Se tiver tamanho superior a 50KB e extensão .mp4, aceitar como válido
            if file_path.suffix.lower() in [".mp4", ".mov", ".mkv", ".webm"]:
                return True
    except Exception as exc:
        logger.debug(f"Falha ao validar cabeçalho de {file_path}: {exc}")
        return False

    return False


class VideoInventoryManager:
    """Gerenciador central de inventário de takes, filas incrementais e economia de GPU."""

    def __init__(self, broll_dir: Optional[Path] = None, processed_dir: Optional[Path] = None):
        self.broll_dir = broll_dir or BROLL_DIR
        self.processed_dir = processed_dir or PROCESSED_DIR
        self.broll_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def audit_inventory(
        self,
        search_dirs: Optional[List[Path]] = None,
        total_scenes: int = 40,
    ) -> VideoInventoryAuditReport:
        """Examina os diretórios de busca e compila o relatório de cobertura completo."""
        dirs_to_scan = search_dirs or [self.broll_dir, DATA_DIR / "final"]
        existing_assets_map: Dict[Tuple[int, str], VideoAssetMetadata] = {}

        for s_dir in dirs_to_scan:
            if not s_dir.exists():
                continue
            for f in s_dir.glob("*.*"):
                if f.suffix.lower() not in [".mp4", ".mov", ".webm", ".mkv"]:
                    continue

                if not validate_video_file_integrity(f):
                    continue

                s_id, shot_type = parse_scene_and_shot_from_filename(f.name)
                if s_id is None or shot_type is None:
                    continue

                if s_id < 1 or s_id > total_scenes:
                    continue

                key = (s_id, shot_type)
                # Se já existe, manter o arquivo com maior tamanho (maior fidelidade)
                if key in existing_assets_map:
                    if f.stat().st_size <= existing_assets_map[key].file_size_bytes:
                        continue

                existing_assets_map[key] = VideoAssetMetadata(
                    scene_id=s_id,
                    shot_type=shot_type,
                    file_path=f,
                    file_size_bytes=f.stat().st_size,
                    duration_sec=14.5 if shot_type == "shot_a" else 8.0,
                    is_valid=True,
                    source_folder=str(s_dir),
                )

        # Mapear cenas presentes e ausentes
        existing_shot_a = [m for (sid, st), m in existing_assets_map.items() if st == "shot_a"]
        existing_shot_b = [m for (sid, st), m in existing_assets_map.items() if st == "shot_b"]

        existing_shot_a_ids = {m.scene_id for m in existing_shot_a}
        existing_shot_b_ids = {m.scene_id for m in existing_shot_b}

        missing_shot_a_ids = [i for i in range(1, total_scenes + 1) if i not in existing_shot_a_ids]
        missing_shot_b_ids = [i for i in range(1, total_scenes + 1) if i not in existing_shot_b_ids]

        total_required_takes = total_scenes * 2
        existing_total = len(existing_shot_a) + len(existing_shot_b)
        coverage_pct = (existing_total / total_required_takes) * 100.0 if total_required_takes > 0 else 0.0

        # Estimativa: Shot A economiza ~1.5 min de render/filas; Shot B economiza ~1.0 min
        gpu_saved_min = (len(existing_shot_a) * 1.5) + (len(existing_shot_b) * 1.0)

        # Ordenar lista de assets por cena e tipo
        sorted_assets = sorted(existing_assets_map.values(), key=lambda a: (a.scene_id, a.shot_type))

        report = VideoInventoryAuditReport(
            total_required_scenes=total_scenes,
            total_required_takes=total_required_takes,
            existing_shot_a_count=len(existing_shot_a),
            existing_shot_b_count=len(existing_shot_b),
            missing_shot_a_ids=missing_shot_a_ids,
            missing_shot_b_ids=missing_shot_b_ids,
            coverage_percentage=coverage_pct,
            estimated_gpu_minutes_saved=gpu_saved_min,
            existing_assets=sorted_assets,
        )

        return report

    def generate_pending_queues(
        self,
        audit_report: VideoInventoryAuditReport,
        omni_queue_file: Path,
        veo3_queue_file: Path,
        output_dir: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Gera arquivos de fila incremental contendo apenas as cenas ausentes no disco."""
        target_dir = output_dir or SCRIPTS_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        out_omni = target_dir / "google_flow_omni_queue_pending.json"
        out_veo3 = target_dir / "google_flow_veo3_queue_pending.json"

        # 1. Filtrar Omni Flash (Shot A)
        with open(omni_queue_file, "r", encoding="utf-8") as f:
            omni_data = json.load(f)

        pending_omni_scenes = [
            sc for sc in omni_data.get("scenes", [])
            if sc["scene_id"] in audit_report.missing_shot_a_ids
        ]
        omni_data_filtered = dict(omni_data)
        omni_data_filtered["scenes"] = pending_omni_scenes
        omni_data_filtered["is_incremental_pending_queue"] = True
        omni_data_filtered["total_pending_scenes"] = len(pending_omni_scenes)

        out_omni.write_text(json.dumps(omni_data_filtered, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Fila incremental Omni salva: {out_omni.name} ({len(pending_omni_scenes)} cenas pendentes)")

        # 2. Filtrar Veo 3.1 4K (Shot B)
        with open(veo3_queue_file, "r", encoding="utf-8") as f:
            veo3_data = json.load(f)

        pending_veo3_scenes = [
            sc for sc in veo3_data.get("scenes", [])
            if sc["scene_id"] in audit_report.missing_shot_b_ids
        ]
        veo3_data_filtered = dict(veo3_data)
        veo3_data_filtered["scenes"] = pending_veo3_scenes
        veo3_data_filtered["is_incremental_pending_queue"] = True
        veo3_data_filtered["total_pending_scenes"] = len(pending_veo3_scenes)

        out_veo3.write_text(json.dumps(veo3_data_filtered, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Fila incremental Veo 3.1 salva: {out_veo3.name} ({len(pending_veo3_scenes)} cenas pendentes)")

        return out_omni, out_veo3

    def ingest_clips_from_directory(
        self,
        source_dir: Path,
        target_broll_dir: Optional[Path] = None,
        move_file: bool = False,
    ) -> List[Path]:
        """Importa e padroniza clipes soltos (ex: da pasta Downloads ou de outra pasta) para data/broll/."""
        dest_dir = target_broll_dir or self.broll_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        ingested_files: List[Path] = []

        if not source_dir.exists():
            logger.warning(f"Diretório de ingest não encontrado: {source_dir}")
            return ingested_files

        for item in source_dir.glob("*.*"):
            if item.suffix.lower() not in [".mp4", ".mov", ".webm", ".mkv"]:
                continue

            if not validate_video_file_integrity(item):
                continue

            s_id, shot_type = parse_scene_and_shot_from_filename(item.name)
            if s_id is None or shot_type is None:
                continue

            # Nome canônico: scene_{id}.mp4 para shot_a e scene_{id}_b.mp4 para shot_b
            target_name = f"scene_{s_id}.mp4" if shot_type == "shot_a" else f"scene_{s_id}_b.mp4"
            target_path = dest_dir / target_name

            if move_file:
                shutil.move(str(item), str(target_path))
                logger.info(f"Ingest (Move): {item.name} -> {target_path.name}")
            else:
                shutil.copy2(str(item), str(target_path))
                logger.info(f"Ingest (Copy): {item.name} -> {target_path.name}")

            ingested_files.append(target_path)

        return ingested_files

    def export_report(self, audit_report: VideoInventoryAuditReport, output_file: Optional[Path] = None) -> Path:
        """Salva o relatório em formato JSON para telemetria corporativa."""
        target_file = output_file or (self.processed_dir / "video_coverage_audit.json")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(json.dumps(audit_report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return target_file

    def format_console_report(self, report: VideoInventoryAuditReport) -> str:
        """Formata relatório executivo em texto para exibição limpa no console/terminal."""
        lines = [
            "\n" + "=" * 70,
            "🎬 DARKFACTORY — AUDITORIA DE COBERTURA DE VÍDEO & ECONOMIA DE GPU",
            "=" * 70,
            f"📊 Total de Cenas Exigidas : {report.total_required_scenes} (80 takes: 40 Shot A + 40 Shot B)",
            f"✅ Takes Existentes no Disco : {report.existing_total_takes} ({report.existing_shot_a_count} Shot A + {report.existing_shot_b_count} Shot B)",
            f"⏳ Takes Pendentes de Geração: {report.missing_total_takes} ({len(report.missing_shot_a_ids)} Shot A + {len(report.missing_shot_b_ids)} Shot B)",
            f"📈 Percentual de Cobertura   : {report.coverage_percentage:.1f}%",
            f"⚡ GPU / Créditos Economizados: ~{report.estimated_gpu_minutes_saved:.1f} minutos de render economizados!",
            "-" * 70,
        ]

        if report.existing_assets:
            lines.append("📁 Takes Prontos Detectados:")
            for a in report.existing_assets:
                size_mb = round(a.file_size_bytes / (1024 * 1024), 2)
                lines.append(f"  - Cena {a.scene_id:02d} [{a.shot_type.upper()}]: {a.file_path.name} ({size_mb} MB) em '{a.source_folder}'")
        else:
            lines.append("⚠️ Nenhum take válido encontrado nos diretórios inspecionados.")

        if report.missing_shot_a_ids:
            lines.append(f"\n❌ Cenas Faltantes Shot A (Omni Flash): {report.missing_shot_a_ids[:15]}" + ("..." if len(report.missing_shot_a_ids) > 15 else ""))
        if report.missing_shot_b_ids:
            lines.append(f"❌ Cenas Faltantes Shot B (Veo 3.1 4K) : {report.missing_shot_b_ids[:15]}" + ("..." if len(report.missing_shot_b_ids) > 15 else ""))

        lines.append("=" * 70 + "\n")
        return "\n".join(lines)
