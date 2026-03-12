"""Processor module - wraps the CLI processing logic for web API use."""
import json
import logging
from pathlib import Path
from typing import List, Optional

from src.config import Config
from src.main import process_pdf_list
from src.pdf_processor import PDFProcessor
from src.summarizer import Summarizer
from src.output_generator import OutputGenerator
from src.utils import ensure_directory

logger = logging.getLogger(__name__)

BATCH_META_FILENAME = "batch_meta.json"


def run_batch_processing(
    batch_id: str,
    pdf_paths: List[str],
    batch_name: Optional[str] = None,
    output_root: Optional[str] = None,
) -> dict:
    """
    Process a list of PDFs and compile to a single output.

    Args:
        batch_id: Unique batch identifier
        pdf_paths: List of absolute paths to PDF files
        batch_name: Optional display name for the batch
        output_root: Root output directory (default: ./output)

    Returns:
        Dict with status, pdf_names, compiled_pdf path, etc.
    """
    output_dir = Path(output_root or Config.DEFAULT_OUTPUT_DIR) / batch_id
    ocr_output_dir = output_dir / Config.OCR_TEXT_SUBDIR
    raw_summaries_dir = output_dir / Config.RAW_SUMMARIES_SUBDIR

    ensure_directory(str(output_dir))
    ensure_directory(str(ocr_output_dir))
    ensure_directory(str(raw_summaries_dir))

    title = batch_name or f"Learning Guides: {batch_id}"

    try:
        pdf_processor = PDFProcessor(
            dpi=Config.OCR_DPI, ocr_output_dir=str(ocr_output_dir)
        )
        summarizer = Summarizer(raw_summaries_dir=str(raw_summaries_dir))
        output_gen = OutputGenerator(str(output_dir))

        _, successful_pdfs, failed_pdfs = process_pdf_list(
            pdf_paths,
            pdf_processor,
            summarizer,
            output_gen,
            Config.PAGES_PER_GROUP,
            Config.DEFAULT_OVERLAP,
            skip_compiled=False,
            compiled_title=title,
        )

        pdf_names = [Path(p).name for p in successful_pdfs]
        compiled_pdf = output_dir / f"{batch_id}-compiled.pdf"
        compiled_exists = compiled_pdf.exists()

        meta = {
            "id": batch_id,
            "name": batch_name or f"Batch {batch_id[:8]}",
            "status": "completed" if not failed_pdfs else "completed_with_errors",
            "pdf_count": len(successful_pdfs),
            "pdf_names": pdf_names,
            "failed_count": len(failed_pdfs),
            "compiled_pdf": str(compiled_pdf) if compiled_exists else None,
        }
    except Exception as e:
        logger.exception(f"Batch {batch_id} failed: {e}")
        meta = {
            "id": batch_id,
            "name": batch_name or f"Batch {batch_id[:8]}",
            "status": "failed",
            "pdf_count": 0,
            "pdf_names": [],
            "failed_count": len(pdf_paths),
            "compiled_pdf": None,
            "error": str(e),
        }

    meta_path = output_dir / BATCH_META_FILENAME
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
