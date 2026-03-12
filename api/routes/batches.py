"""Batch API routes - Postgres-backed batches and blob storage."""
import asyncio
import json
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Config
from src.utils import ensure_directory

from api.database import get_db
from api.models import Batch, Blob
from api.processor import run_batch_processing
from api.routes.auth import require_auth

router = APIRouter(prefix="/api/batches", tags=["batches"])

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path(Config.DEFAULT_OUTPUT_DIR)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB total per batch

BLOB_KIND_COMPILED_PDF = "compiled_pdf"
BLOB_KIND_SOURCE_PDF = "source_pdf"


def _batch_to_meta(b: Batch) -> dict:
    """Convert Batch ORM to API response shape."""
    return {
        "id": str(b.id),
        "name": b.name,
        "status": b.status,
        "pdf_count": b.pdf_count,
        "pdf_names": b.pdf_names or [],
        "failed_count": b.failed_count,
        "error": b.error,
        "compiled_pdf": b.compiled_pdf,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }


async def _processing_task(
    batch_id: uuid.UUID,
    upload_dir: Path,
    batch_name: Optional[str],
    db_factory,
) -> None:
    """Run sync processor in thread, then save blob and update batch in DB."""
    loop = asyncio.get_event_loop()
    # Run CPU/IO-heavy processing in thread pool
    await loop.run_in_executor(
        None,
        _run_processor_sync,
        batch_id,
        upload_dir,
        batch_name,
    )
    # DB updates in async context
    async with db_factory() as session:
        output_dir = OUTPUT_DIR / str(batch_id)
        meta_path = output_dir / "batch_meta.json"
        if not meta_path.exists():
            return
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        compiled_path = output_dir / f"{batch_id}-compiled.pdf"

        batch = await session.get(Batch, batch_id)
        if not batch:
            return
        batch.status = meta.get("status", "failed")
        batch.pdf_count = meta.get("pdf_count", 0)
        batch.pdf_names = meta.get("pdf_names")
        batch.failed_count = meta.get("failed_count", 0)
        batch.error = meta.get("error")

        if compiled_path.exists():
            pdf_bytes = compiled_path.read_bytes()
            blob = Blob(
                batch_id=batch_id,
                kind=BLOB_KIND_COMPILED_PDF,
                filename=f"{batch_id}-compiled.pdf",
                content_type="application/pdf",
                data=pdf_bytes,
            )
            session.add(blob)
            batch.compiled_pdf = True
            try:
                compiled_path.unlink()
            except Exception:
                pass

        await session.commit()

    try:
        shutil.rmtree(upload_dir, ignore_errors=True)
    except Exception:
        pass


def _run_processor_sync(
    batch_id: uuid.UUID,
    upload_dir: Path,
    batch_name: Optional[str],
) -> None:
    """Synchronous processor call (run in executor)."""
    pdf_paths = sorted(upload_dir.glob("*.pdf"))
    pdf_paths_str = [str(p) for p in pdf_paths]
    run_batch_processing(
        batch_id=str(batch_id),
        pdf_paths=pdf_paths_str,
        batch_name=batch_name,
        output_root=str(OUTPUT_DIR),
    )


@router.post("")
async def create_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_auth),
):
    """
    Upload PDFs and start batch processing.
    Returns batch_id immediately; processing runs in background.
    Batch metadata and compiled PDF are stored in Postgres.
    """
    batch_id = uuid.uuid4()
    upload_dir = UPLOAD_DIR / str(batch_id)
    ensure_directory(str(upload_dir))

    total_size = 0
    pdf_paths = []

    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            continue
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

    display_name = name or f"Batch {batch_id.hex[:8]}"
    batch = Batch(
        id=batch_id,
        name=display_name,
        status="processing",
        pdf_count=len(pdf_paths),
        pdf_names=[Path(p).name for p in pdf_paths],
        failed_count=0,
        compiled_pdf=False,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    # Persist source PDFs as blobs so they can be viewed later
    for file_path in sorted(Path(p) for p in pdf_paths):
        try:
            data = file_path.read_bytes()
            blob = Blob(
                batch_id=batch_id,
                kind=BLOB_KIND_SOURCE_PDF,
                filename=file_path.name,
                content_type="application/pdf",
                data=data,
            )
            db.add(blob)
        except Exception:
            pass
    await db.commit()

    # Run processing in background; task will get its own session
    from api.database import async_session_factory
    background_tasks.add_task(
        _processing_task,
        batch_id,
        upload_dir,
        name,
        async_session_factory,
    )

    return _batch_to_meta(batch)


@router.get("")
async def list_batches(db: AsyncSession = Depends(get_db), _auth: dict = Depends(require_auth)):
    """List all batches (newest first)."""
    result = await db.execute(
        select(Batch).order_by(Batch.created_at.desc())
    )
    batches = result.scalars().all()
    return [_batch_to_meta(b) for b in batches]


@router.get("/{batch_id}")
async def get_batch(batch_id: str, db: AsyncSession = Depends(get_db), _auth: dict = Depends(require_auth)):
    """Get batch metadata by ID."""
    try:
        bid = uuid.UUID(batch_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch not found")
    batch = await db.get(Batch, bid)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return _batch_to_meta(batch)


@router.delete("/{batch_id}")
async def delete_batch(batch_id: str, db: AsyncSession = Depends(get_db), _auth: dict = Depends(require_auth)):
    """Delete a batch and its blobs. Removes leftover upload/output dirs if present."""
    try:
        bid = uuid.UUID(batch_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch not found")
    batch = await db.get(Batch, bid)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    await db.delete(batch)
    await db.commit()
    upload_dir = UPLOAD_DIR / str(bid)
    output_dir = OUTPUT_DIR / str(bid)
    for path in (upload_dir, output_dir):
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass
    return Response(status_code=204)


@router.get("/{batch_id}/pdfs/{filename:path}")
async def get_source_pdf(
    batch_id: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_auth),
):
    """Serve a source PDF from the batch (for viewing in browser or download)."""
    try:
        bid = uuid.UUID(batch_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch not found")
    batch = await db.get(Batch, bid)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    result = await db.execute(
        select(Blob).where(
            Blob.batch_id == bid,
            Blob.kind == BLOB_KIND_SOURCE_PDF,
            Blob.filename == filename,
        ).limit(1)
    )
    blob = result.scalar_one_or_none()
    if not blob:
        raise HTTPException(status_code=404, detail="PDF not found")
    return Response(
        content=blob.data,
        media_type=blob.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{blob.filename}"',
        },
    )


@router.get("/{batch_id}/compiled")
async def get_compiled_pdf(batch_id: str, db: AsyncSession = Depends(get_db), _auth: dict = Depends(require_auth)):
    """Download the compiled PDF for a batch (served from DB blob)."""
    try:
        bid = uuid.UUID(batch_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch not found")
    batch = await db.get(Batch, bid)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if batch.status not in ("completed", "completed_with_errors"):
        raise HTTPException(
            status_code=400,
            detail="Batch is still processing or failed",
        )
    if not batch.compiled_pdf:
        raise HTTPException(status_code=404, detail="Compiled PDF not found")

    result = await db.execute(
        select(Blob).where(
            Blob.batch_id == bid,
            Blob.kind == BLOB_KIND_COMPILED_PDF,
        ).limit(1)
    )
    blob = result.scalar_one_or_none()
    if not blob:
        raise HTTPException(status_code=404, detail="Compiled PDF not found")
    return Response(
        content=blob.data,
        media_type=blob.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{blob.filename}"',
        },
    )
