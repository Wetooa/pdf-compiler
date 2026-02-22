"""Batch API routes."""
import json
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.config import Config
from src.utils import ensure_directory

from ..processor import run_batch_processing

router = APIRouter(prefix="/api/batches", tags=["batches"])

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path(Config.DEFAULT_OUTPUT_DIR)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB total per batch


def _get_batch_meta(batch_id: str) -> Optional[dict]:
    """Load batch metadata from output directory."""
    meta_path = OUTPUT_DIR / batch_id / "batch_meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _processing_task(batch_id: str, upload_dir: Path, batch_name: Optional[str]):
    """Synchronous processing task run in thread pool."""
    pdf_paths = sorted(upload_dir.glob("*.pdf"))
    pdf_paths_str = [str(p) for p in pdf_paths]
    run_batch_processing(
        batch_id=batch_id,
        pdf_paths=pdf_paths_str,
        batch_name=batch_name,
        output_root=str(OUTPUT_DIR),
    )
    # Clean up uploads after processing
    try:
        shutil.rmtree(upload_dir, ignore_errors=True)
    except Exception:
        pass


@router.post("")
async def create_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
):
    """
    Upload PDFs and start batch processing.
    Returns batch_id immediately; processing runs in background.
    """
    batch_id = str(uuid.uuid4())
    upload_dir = UPLOAD_DIR / batch_id
    ensure_directory(str(upload_dir))

    total_size = 0
    pdf_paths = []

    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            continue
        total_size += 0  # We'll accumulate as we read
        file_path = upload_dir / f.filename
        try:
            content = await f.read()
            total_size += len(content)
            if total_size > MAX_UPLOAD_SIZE:
                shutil.rmtree(upload_dir, ignore_errors=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"Total upload size exceeds {MAX_UPLOAD_SIZE // (1024*1024)}MB limit",
                )
            file_path.write_bytes(content)
            pdf_paths.append(str(file_path))
        except Exception as e:
            shutil.rmtree(upload_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=str(e))

    if not pdf_paths:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="No valid PDF files uploaded")

    # Write initial meta so GET returns "processing"
    output_dir = OUTPUT_DIR / batch_id
    ensure_directory(str(output_dir))
    initial_meta = {
        "id": batch_id,
        "name": name or f"Batch {batch_id[:8]}",
        "status": "processing",
        "pdf_count": len(pdf_paths),
        "pdf_names": [Path(p).name for p in pdf_paths],
        "compiled_pdf": None,
    }
    (output_dir / "batch_meta.json").write_text(
        json.dumps(initial_meta, indent=2), encoding="utf-8"
    )

    background_tasks.add_task(_processing_task, batch_id, upload_dir, name)

    return initial_meta


@router.get("/{batch_id}")
async def get_batch(batch_id: str):
    """Get batch metadata by ID."""
    meta = _get_batch_meta(batch_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Batch not found")
    return meta


@router.get("/{batch_id}/compiled")
async def get_compiled_pdf(batch_id: str):
    """Download the compiled PDF for a batch."""
    meta = _get_batch_meta(batch_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Batch not found")
    if meta.get("status") not in ("completed", "completed_with_errors"):
        raise HTTPException(
            status_code=400,
            detail="Batch is still processing or failed",
        )
    pdf_path = Path(meta.get("compiled_pdf") or "")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Compiled PDF not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="compiled.pdf",
    )
</think>
Simplifying background task execution:
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace