from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import User
from schemas import MedicationOrderOut, MedicationOrderCreate
from dependencies import require_role, require_roles, get_current_user
from services.order_service import OrderService
from service_dependencies import get_order_service
from exceptions import (
    OrderNotFoundError, DrugNotFoundError, InsufficientStockError,
    OrderAlreadyCompletedError, InvalidOrderStatusError, ValMedBusinessException
)
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


def translate_business_exception(exc: ValMedBusinessException) -> HTTPException:
    """
    Translate business exceptions to HTTP exceptions.
    This centralizes the error handling and HTTP status code mapping.
    """
    if isinstance(exc, OrderNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    elif isinstance(exc, DrugNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    elif isinstance(exc, InsufficientStockError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    elif isinstance(exc, OrderAlreadyCompletedError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    elif isinstance(exc, InvalidOrderStatusError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    else:
        # Generic business exception
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/", response_model=MedicationOrderOut, dependencies=[Depends(require_role("doctor"))])
def create_order(
    order: MedicationOrderCreate, 
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Create a new medication order.
    Only doctors can create orders.
    """
    try:
        new_order = order_service.create_order(order, current_user.id)
        return new_order
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error creating order: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the order"
        )


@router.get("/my-orders/", response_model=List[MedicationOrderOut], dependencies=[Depends(require_role("doctor"))])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get all orders created by the current doctor.
    This endpoint allows doctors to see the status of their prescriptions.
    """
    try:
        orders = order_service.list_orders_by_doctor(current_user.id)
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders for doctor {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving your orders"
        )


@router.get("/active-mar/", response_model=List[MedicationOrderOut], dependencies=[Depends(require_roles(["nurse", "pharmacist"]))])
def get_active_mar(order_service: OrderService = Depends(get_order_service)):
    """
    Get all active orders for the Medication Administration Record (MAR).
    This endpoint allows nurses and pharmacists to view active prescriptions.
    """
    try:
        active_orders = order_service.get_active_mar_orders()
        return active_orders
    except Exception as e:
        logger.error(f"Error retrieving active MAR orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving active orders"
        )


@router.get("/mar-dashboard", response_model=Dict[str, Any], dependencies=[Depends(require_role("nurse"))])
def get_mar_dashboard(order_service: OrderService = Depends(get_order_service)):
    """
    Get optimized dashboard data for nurses, grouped by patient.
    This function uses caching and optimized queries to prevent N+1 problems.
    """
    try:
        dashboard_data = order_service.get_mar_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error retrieving MAR dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving dashboard data"
        )


@router.get("/", response_model=List[MedicationOrderOut], dependencies=[Depends(get_current_user)])
def get_orders(
    order_service: OrderService = Depends(get_order_service),
    skip: int = 0, 
    limit: int = Query(100, le=100)
):
    """
    Get all active orders with pagination.
    Uses optimized queries to prevent N+1 problems.
    
    WARNING: This endpoint uses OFFSET-based pagination which is inefficient for large datasets.
    Use /orders/cursor for production workloads with cursor-based pagination.
    """
    try:
        active_orders = order_service.list_active_orders(skip, limit)
        return active_orders
    except Exception as e:
        logger.error(f"Error retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders"
        )


@router.get("/cursor", response_model=Dict[str, Any], dependencies=[Depends(get_current_user)])
def get_orders_with_cursor(
    order_service: OrderService = Depends(get_order_service),
    cursor: Optional[str] = Query(None, description="Cursor from previous page for pagination"),
    limit: int = Query(50, le=100, description="Maximum number of orders to return"),
    cursor_type: str = Query("timestamp", regex="^(timestamp|id)$", description="Type of cursor to use")
):
    """
    Get active orders using efficient CURSOR-based pagination.
    
    This endpoint provides scalable pagination that maintains O(log n) performance
    regardless of dataset size, unlike OFFSET-based pagination which degrades linearly.
    
    Args:
        cursor: The cursor value from the previous page (timestamp or UUID string)
        limit: Maximum number of records to return (max 100)
        cursor_type: Either "timestamp" for chronological or "id" for stable pagination
        
    Returns:
        {
            "orders": [...],
            "next_cursor": "2024-01-15T10:30:00Z" or "uuid-string",
            "has_next": true,
            "cursor_type": "timestamp"
        }
    """
    try:
        # Parse cursor based on type
        parsed_cursor = None
        if cursor:
            if cursor_type == "timestamp":
                try:
                    parsed_cursor = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid timestamp cursor format. Use ISO format: 2024-01-15T10:30:00Z"
                    )
            else:  # cursor_type == "id"
                try:
                    parsed_cursor = uuid.UUID(cursor)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid UUID cursor format"
                    )
        
        result = order_service.list_active_orders_with_cursor(parsed_cursor, limit, cursor_type)
        
        # Format cursor for JSON response
        if result["next_cursor"]:
            if cursor_type == "timestamp":
                result["next_cursor"] = result["next_cursor"].isoformat() + "Z"
            else:
                result["next_cursor"] = str(result["next_cursor"])
        
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error retrieving orders with cursor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders"
        )


@router.get("/{order_id}", response_model=MedicationOrderOut, dependencies=[Depends(get_current_user)])
def get_order(
    order_id: uuid.UUID,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get a specific order by ID.
    """
    try:
        order = order_service.get_order_by_id(order_id)
        return order
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error retrieving order {order_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error retrieving order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the order"
        )


@router.post("/{order_id}/fulfill", response_model=Dict[str, Any], dependencies=[Depends(require_role("nurse"))])
def fulfill_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Fulfill a medication order (complex business logic).
    This represents giving medication to a patient and updating stock.
    Only nurses can fulfill orders.
    """
    try:
        fulfillment_result = order_service.fulfill_order(order_id, current_user.id)
        return fulfillment_result
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error fulfilling order {order_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error fulfilling order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fulfilling the order"
        )


@router.post("/{order_id}/discontinue", response_model=MedicationOrderOut, dependencies=[Depends(require_role("doctor"))])
def discontinue_order(
    order_id: uuid.UUID,
    reason: str = None,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Discontinue a medication order.
    Only doctors can discontinue orders.
    """
    try:
        discontinued_order = order_service.discontinue_order(order_id, reason)
        return discontinued_order
    except ValMedBusinessException as e:
        logger.warning(f"Business logic error discontinuing order {order_id}: {e.message}")
        raise translate_business_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error discontinuing order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while discontinuing the order"
        )


@router.get("/statistics/summary", response_model=Dict[str, Any], dependencies=[Depends(require_roles(["doctor", "nurse", "pharmacist"]))])
def get_order_statistics(order_service: OrderService = Depends(get_order_service)):
    """
    Get order statistics for reporting.
    Available to all clinical staff.
    """
    try:
        statistics = order_service.get_order_statistics()
        return statistics
    except Exception as e:
        logger.error(f"Error retrieving order statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving order statistics"
        ) 