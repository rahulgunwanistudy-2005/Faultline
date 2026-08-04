from __future__ import annotations

from pathlib import PurePath

from fastapi import APIRouter, HTTPException, Request

from ..config import get_settings
from ..schemas import ProofRevealPayload, ReadingCorrection, TemplateId
from ..services.background_jobs import run_local_ai_pipeline
from ..services.demo import build_class_analysis, get_student
from ..services.held_out import ProofTokenError, create_prediction, reveal_prediction
from ..services.jobs import DEMO_DISCLOSURE, LOCAL_AI_DISCLOSURE, STORE
from ..services.model_health import model_health, runtime_summary
from ..services.rate_limit import UPLOAD_LIMITER, WRITE_LIMITER
from ..services.segmentation import InvalidWorksheetImage, crop_normalized_image, normalize_image

router = APIRouter()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
def _client_key(request: Request, suffix: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{host}:{suffix}"


def _enforce_rate_limit(request: Request, *, write: bool = False) -> None:
    limiter = WRITE_LIMITER if write else UPLOAD_LIMITER
    bucket = "write" if write else "upload"
    if not limiter.allow(_client_key(request, bucket)):
        raise HTTPException(
            status_code=429,
            detail="Too many requests; retry in one minute",
            headers={"Retry-After": "60"},
        )


async def _read_upload(request: Request) -> bytes:
    maximum = get_settings().max_upload_bytes
    declared_length = request.headers.get("content-length", "")
    if declared_length.isdigit() and int(declared_length) > maximum:
        raise HTTPException(
            status_code=413,
            detail=f"The competition demo accepts images up to {maximum // (1024 * 1024)} MB",
        )
    body = bytearray()
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > maximum:
            raise HTTPException(
                status_code=413,
                detail=f"The competition demo accepts images up to {maximum // (1024 * 1024)} MB",
            )
        body.extend(chunk)
    if total == 0:
        raise HTTPException(status_code=422, detail="The uploaded file is empty")
    return bytes(body)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "faultline-api", "mode": "competition-demo"}


@router.get("/v1/runtime")
def runtime() -> dict:
    """Report the active runtime mode and non-secret model configuration."""
    return runtime_summary()


@router.get("/v1/models/health")
async def models_health() -> dict:
    """Report local-model availability (probes Ollama only in local_ai mode)."""
    return await model_health()


@router.get("/v1/demo/classes/{class_id}")
def demo_class(class_id: str) -> dict:
    if class_id != "period-3":
        raise HTTPException(status_code=404, detail="Demo class not found")
    return build_class_analysis()


@router.post("/v1/analyses", status_code=202)
async def create_analysis(
    request: Request,
    template_id: TemplateId,
) -> dict:
    _enforce_rate_limit(request)
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Send a PNG or JPEG image body")
    content = await _read_upload(request)
    try:
        image = normalize_image(content)
        crops = crop_normalized_image(image)
    except InvalidWorksheetImage as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    filename_header = request.headers.get("x-filename", "worksheet")
    filename = PurePath(filename_header.replace("\\", "/")).name[:120] or "worksheet"
    metadata = {
        "width": image.width,
        "height": image.height,
        "regions": len(crops),
        "bytes_received": len(content),
        "stored": False,
    }

    if get_settings().is_local_ai:
        job = STORE.create_local_ai(filename, template_id, metadata)
        # Synchronous within the request for this single-worker demo: the job
        # traverses real pipeline stages (recorded in state_history), never a
        # time-based simulation, and there is no fixture fallback on failure.
        region_crops = [(crop.region_id, crop.image_bytes) for crop in crops]
        await run_local_ai_pipeline(job, region_crops)
        snapshot = job.snapshot()
        return {
            "analysis_id": job.id,
            "status": snapshot["status"],
            "progress": snapshot["progress"],
            "mode": snapshot["mode"],
            "disclosure": LOCAL_AI_DISCLOSURE,
            "upload": metadata,
        }

    job = STORE.create(filename, template_id, metadata)
    snapshot = job.snapshot()
    return {
        "analysis_id": job.id,
        "status": snapshot["status"],
        "progress": snapshot["progress"],
        "mode": snapshot["mode"],
        "disclosure": DEMO_DISCLOSURE,
        "upload": metadata,
    }


@router.get("/v1/analyses/{analysis_id}")
def get_analysis(analysis_id: str) -> dict:
    job = STORE.get(analysis_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis not found or expired")
    return job.snapshot()


@router.patch("/v1/analyses/{analysis_id}/readings/{reading_id}")
def correct_reading(
    request: Request,
    analysis_id: str,
    reading_id: str,
    correction: ReadingCorrection,
) -> dict:
    _enforce_rate_limit(request, write=True)
    try:
        job = STORE.correct(analysis_id, reading_id, correction.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Reading not found in this analysis") from exc
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis not found or expired")
    return {
        "analysis_id": analysis_id,
        "reading_id": reading_id,
        "normalized_answer": correction.normalized_answer,
        "step_features": correction.step_features,
        "status": "complete",
        "result": job.snapshot()["result"],
        "message": "The diagnosis was recomputed from the reviewed reading.",
    }


@router.get("/v1/students/{student_id}/diagnostic-items")
def diagnostic_items(student_id: str) -> dict:
    student = get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"student_id": student_id, "items": student["diagnostic_items"]}


@router.post("/v1/students/{student_id}/held-out-prediction")
def held_out_prediction(request: Request, student_id: str) -> dict:
    _enforce_rate_limit(request, write=True)
    prediction = create_prediction(student_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return prediction


@router.post("/v1/students/{student_id}/held-out-reveal")
def held_out_reveal(request: Request, student_id: str, payload: ProofRevealPayload) -> dict:
    _enforce_rate_limit(request, write=True)
    try:
        reveal = reveal_prediction(student_id, payload.proof_token)
    except ProofTokenError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if reveal is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return reveal
