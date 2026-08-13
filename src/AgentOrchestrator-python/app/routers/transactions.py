"""Transactions API router.

Mirrors ``AgentHQDemo.Api/Controllers/TransactionsController.cs``.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.database import get_session
from app.models import Transaction, TransactionCreate
from app.services.retail_analytics import RetailAnalyticsService

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def get_service(db: Session = Depends(get_session)) -> RetailAnalyticsService:
    return RetailAnalyticsService(db)


@router.get("", response_model=list[Transaction])
async def get_all(service: RetailAnalyticsService = Depends(get_service)) -> list[Transaction]:
    return await service.get_transactions()


@router.get("/{transaction_id}", response_model=Transaction)
async def get(
    transaction_id: int,
    service: RetailAnalyticsService = Depends(get_service),
) -> Transaction:
    txn = await service.get_transaction(transaction_id)
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return txn


@router.post("", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create(
    payload: TransactionCreate,
    response: Response,
    service: RetailAnalyticsService = Depends(get_service),
) -> Transaction:
    # FastAPI has already validated `payload` and returned 422 if it was
    # invalid, which is what ModelState.IsValid does in the .NET controller.
    created = await service.add_transaction(Transaction(**payload.model_dump()))
    response.headers["Location"] = f"/api/transactions/{created.id}"
    return created


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    transaction_id: int,
    service: RetailAnalyticsService = Depends(get_service),
) -> Response:
    deleted = await service.delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
