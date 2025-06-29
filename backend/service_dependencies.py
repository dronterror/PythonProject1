"""
Dependency injection utilities for services and repositories.
This module provides FastAPI dependencies for the service and repository layers.
"""

from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from repositories.order_repository import OrderRepository
from repositories.drug_repository import DrugRepository
from services.order_service import OrderService
from services.drug_service import DrugService


# Repository Dependencies
def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    """
    Dependency injection for OrderRepository.
    """
    return OrderRepository(db)


def get_drug_repository(db: Session = Depends(get_db)) -> DrugRepository:
    """
    Dependency injection for DrugRepository.
    """
    return DrugRepository(db)


# Service Dependencies
def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    drug_repo: DrugRepository = Depends(get_drug_repository),
    db: Session = Depends(get_db)  # CRITICAL: Provide session for transaction control
) -> OrderService:
    """
    Dependency injection for OrderService.
    CRITICAL: Provides database session for atomic transaction management.
    """
    return OrderService(order_repo, drug_repo, db)


def get_drug_service(
    drug_repo: DrugRepository = Depends(get_drug_repository)
) -> DrugService:
    """
    Dependency injection for DrugService.
    """
    return DrugService(drug_repo) 