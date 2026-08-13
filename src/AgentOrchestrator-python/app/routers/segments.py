"""Segments API router.

Mirrors ``AgentHQDemo.Api/Controllers/SegmentsController.cs``.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import CustomerSegment, SegmentPrediction
from app.services.retail_analytics import RetailAnalyticsService

router = APIRouter(prefix="/api/segments", tags=["segments"])


def get_service(db: Session = Depends(get_session)) -> RetailAnalyticsService:
    return RetailAnalyticsService(db)


@router.get("", response_model=list[CustomerSegment])
async def get_all(
    service: RetailAnalyticsService = Depends(get_service),
) -> list[CustomerSegment]:
    return await service.get_segments()


@router.get("/predict/{customer_id}", response_model=SegmentPrediction)
async def predict(
    customer_id: str,
    service: RetailAnalyticsService = Depends(get_service),
) -> SegmentPrediction:
    return await service.predict_segment(customer_id)


@router.get("/{segment_id}", response_model=CustomerSegment)
async def get(
    segment_id: int,
    service: RetailAnalyticsService = Depends(get_service),
) -> CustomerSegment:
    segment = await service.get_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return segment
