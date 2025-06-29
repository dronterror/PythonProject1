from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any
import uuid
from models import User
from schemas import DrugOut, DrugCreate, DrugUpdate, DrugTransferCreate, DrugTransferOut
from dependencies import require_role, get_current_user
from services.drug_service import DrugService
from service_dependencies import get_drug_service
from exceptions import (
    DrugNotFoundError, DrugAlreadyExistsError, InsufficientStockError,
    InvalidStockQuantityError, InvalidTransferError, ValMedBusinessException
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/drugs", tags=["drugs"])


def translate_business_exception(exc: ValMedBusinessException) -> HTTPException:
    """
    Translate business exceptions to HTTP exceptions.
    This centralizes the error handling and HTTP status code mapping.
    """
    if isinstance(exc, DrugNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    elif isinstance(exc, DrugAlreadyExistsError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    elif isinstance(exc, InsufficientStockError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    elif isinstance(exc, InvalidStockQuantityError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    elif isinstance(exc, InvalidTransferError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    else:
        # Generic business exception
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def create_drug_endpoint(
    drug: DrugCreate, 
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Create a new drug.
    Only pharmacists can create drugs.
    Cache invalidation is handled automatically by the service layer.
    """
    try:
        new_drug = drug_service.create_drug(drug)
        return new_drug
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error creating drug: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error creating drug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the drug"
        )


@router.put("/{drug_id}", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def update_drug_endpoint(
    drug_id: uuid.UUID, 
    drug: DrugUpdate, 
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Update a drug's information.
    Only pharmacists can update drugs.
    Cache invalidation is handled automatically by the service layer.
    """
    try:
        updated_drug = drug_service.update_drug(drug_id, drug)
        return updated_drug
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error updating drug {drug_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error updating drug {drug_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the drug"
        )


@router.post("/transfer", response_model=DrugTransferOut, dependencies=[Depends(require_role("pharmacist"))])
def transfer_drug_stock_endpoint(
    transfer: DrugTransferCreate, 
    current_user: User = Depends(get_current_user),
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Transfer drug stock between wards.
    Only pharmacists can perform drug stock transfers.
    Cache invalidation is handled automatically by the service layer.
    """
    try:
        transfer_record = drug_service.transfer_drug_stock(transfer, current_user.id)
        return transfer_record
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error transferring drug stock: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error transferring drug stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while transferring drug stock"
        )


@router.get("/low-stock", response_model=List[DrugOut], dependencies=[Depends(require_role("pharmacist"))])
def get_low_stock_drugs_endpoint(
    drug_service: DrugService = Depends(get_drug_service),
    skip: int = 0, 
    limit: int = Query(100, le=100)
):
    """
    Get drugs with low stock levels.
    Only pharmacists can view low stock alerts.
    """
    try:
        low_stock_drugs = drug_service.get_low_stock_drugs()
        return low_stock_drugs[skip:skip + limit]
    except Exception as e:
        logger.error(f"Error retrieving low stock drugs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving low stock drugs"
        )


@router.get("/", response_model=List[DrugOut], dependencies=[Depends(get_current_user)])
def get_drugs_endpoint(
    drug_service: DrugService = Depends(get_drug_service),
    skip: int = 0, 
    limit: int = Query(100, le=100)
):
    """
    Get all drugs with pagination.
    Available to all authenticated users.
    """
    try:
        drugs = drug_service.list_drugs(skip, limit)
        return drugs
    except Exception as e:
        logger.error(f"Error retrieving drugs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving drugs"
        )


@router.get("/formulary", response_model=List[Dict[str, Any]], dependencies=[Depends(require_role("doctor"))])
def get_formulary_endpoint(drug_service: DrugService = Depends(get_drug_service)):
    """
    Get the static formulary list for doctors to use when prescribing.
    Returns lightweight drug information (id, name, form, strength).
    
    ⚡ CACHED: This endpoint uses Redis caching with a 5-minute expiration.
    Cache is automatically invalidated when drugs are created, updated, or deleted.
    """
    try:
        formulary_data = drug_service.get_formulary()
        return formulary_data
    except Exception as e:
        logger.error(f"Error retrieving formulary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the formulary"
        )


@router.get("/inventory/status", response_model=Dict[str, Dict[str, Any]], dependencies=[Depends(require_role("doctor"))])
def get_inventory_status_endpoint(drug_service: DrugService = Depends(get_drug_service)):
    """
    Get real-time inventory status for all drugs.
    Returns a lightweight mapping of drug_id to stock count and status.
    
    ⚡ CACHED: This endpoint uses Redis caching with a 1-minute expiration.
    Cache is automatically invalidated when drug stock levels are updated.
    """
    try:
        inventory_status = drug_service.get_inventory_status()
        return inventory_status
    except Exception as e:
        logger.error(f"Error retrieving inventory status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving inventory status"
        )


@router.get("/{drug_id}", response_model=DrugOut, dependencies=[Depends(get_current_user)])
def get_drug_endpoint(
    drug_id: uuid.UUID,
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Get a specific drug by ID.
    Available to all authenticated users.
    """
    try:
        drug = drug_service.get_drug_by_id(drug_id)
        return drug
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error retrieving drug {drug_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error retrieving drug {drug_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the drug"
        )


@router.put("/{drug_id}/stock", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def update_drug_stock_endpoint(
    drug_id: uuid.UUID,
    new_stock: int = Query(..., ge=0, description="New stock level (must be non-negative)"),
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Update drug stock level.
    Only pharmacists can update stock levels.
    Cache invalidation is handled automatically by the service layer.
    """
    try:
        updated_drug = drug_service.update_stock(drug_id, new_stock)
        return updated_drug
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error updating stock for drug {drug_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error updating stock for drug {drug_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating drug stock"
        )


@router.get("/{drug_id}/analytics", response_model=Dict[str, Any], dependencies=[Depends(require_role("pharmacist"))])
def get_drug_analytics_endpoint(
    drug_id: uuid.UUID,
    drug_service: DrugService = Depends(get_drug_service)
):
    """
    Get analytics for a specific drug.
    Only pharmacists can view drug analytics.
    """
    try:
        analytics = drug_service.get_drug_usage_analytics(drug_id)
        return analytics
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error retrieving analytics for drug {drug_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error retrieving analytics for drug {drug_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving drug analytics"
        )


@router.get("/transfers/history", response_model=List[DrugTransferOut], dependencies=[Depends(require_role("pharmacist"))])
def get_drug_transfers_endpoint(
    drug_service: DrugService = Depends(get_drug_service),
    skip: int = 0,
    limit: int = Query(100, le=100)
):
    """
    Get drug transfer history with pagination.
    Only pharmacists can view transfer history.
    """
    try:
        transfers = drug_service.get_drug_transfers(skip, limit)
        return transfers
    except Exception as e:
        logger.error(f"Error retrieving drug transfers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving drug transfers"
        ) 