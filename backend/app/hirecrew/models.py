"""
Data models for the HireCrew Seller-Hosted API Contract (v1).
Matches the exact schema specified in HireCrew seller documentation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    title: str = Field(..., max_length=500, description="Title of the cited source.")
    url: str = Field(..., max_length=2048, description="Reachable primary source URL.")


class HireCrewJobSubmitRequest(BaseModel):
    orderId: str = Field(..., description="HireCrew order UUID.")
    brief: str = Field(..., min_length=1, max_length=50000, description="Buyer task brief or text to inspect.")


class HireCrewJobSubmitResponse(BaseModel):
    jobId: str
    status: str = "queued"


class HireCrewJobPollResponse(BaseModel):
    jobId: str
    status: str  # "queued", "running", "delivered", "failed"
    report: Optional[str] = None
    sources: Optional[List[SourceItem]] = None
    error: Optional[str] = None
