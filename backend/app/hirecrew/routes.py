"""
HireCrew Seller-Hosted REST API Router.
Implements the exact v1 contract for job submission and polling.
"""

import re
import asyncio
from fastapi import APIRouter, Header, HTTPException, Request, BackgroundTasks
from app.hirecrew.models import (
    HireCrewJobSubmitRequest,
    HireCrewJobSubmitResponse,
    HireCrewJobPollResponse,
    SourceItem
)
from app.db.jobs import job_db, IdempotencyConflictError
from app.hirecrew.worker import execute_hirecrew_job
from app.config import config

router = APIRouter()

# Strict jobId path validation: letters, digits, _, -
JOB_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')


def _verify_bearer_token(authorization: str = Header(None)):
    """Verifies seller integration Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header.")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format. Expected Bearer token.")
    token = parts[1]
    if token != config.hirecrew_seller_token:
        raise HTTPException(status_code=403, detail="Invalid seller integration token.")


@router.post("/jobs", response_model=HireCrewJobSubmitResponse, status_code=200)
async def submit_job(
    request: HireCrewJobSubmitRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    """
    HireCrew Seller Submit Endpoint.
    Contract:
    POST /jobs
    Headers:
      Authorization: Bearer <token>
      Idempotency-Key: <order-key>
    """
    _verify_bearer_token(authorization)

    if not idempotency_key or not idempotency_key.strip():
        raise HTTPException(status_code=400, detail="Missing required Idempotency-Key header.")

    try:
        job, is_new = job_db.create_or_get_job(
            order_id=request.orderId,
            brief=request.brief,
            idempotency_key=idempotency_key.strip()
        )
    except IdempotencyConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # If this is a new job, trigger background execution
    if is_new:
        background_tasks.add_task(execute_hirecrew_job, job["job_id"])

    return HireCrewJobSubmitResponse(
        jobId=job["job_id"],
        status=job["status"]
    )


@router.get("/jobs/{job_id}", response_model=HireCrewJobPollResponse)
async def poll_job(
    job_id: str,
    authorization: str = Header(None)
):
    """
    HireCrew Seller Polling Endpoint.
    Contract:
    GET /jobs/{jobId}
    Headers:
      Authorization: Bearer <token>
    """
    _verify_bearer_token(authorization)

    if not JOB_ID_REGEX.match(job_id):
        raise HTTPException(status_code=400, detail="Invalid jobId format. Must contain only alphanumeric, _, or - characters.")

    job = job_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    sources_models = [SourceItem(**s) for s in job.get("sources", [])] if job.get("sources") else None

    return HireCrewJobPollResponse(
        jobId=job["job_id"],
        status=job["status"],
        report=job.get("report"),
        sources=sources_models,
        error=job.get("error")
    )
