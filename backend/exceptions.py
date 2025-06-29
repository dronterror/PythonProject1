"""
Custom business exceptions for the ValMed application.
These exceptions are raised by the service layer and translated to HTTP responses by the router layer.
"""


class ValMedBusinessException(Exception):
    """Base exception for all business logic errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# Order-related exceptions
class OrderNotFoundError(ValMedBusinessException):
    """Raised when a medication order is not found."""
    
    def __init__(self, order_id: str):
        super().__init__(f"Order with ID {order_id} not found", "ORDER_NOT_FOUND")


class OrderAlreadyCompletedError(ValMedBusinessException):
    """Raised when attempting to modify a completed order."""
    
    def __init__(self, order_id: str):
        super().__init__(f"Order {order_id} is already completed", "ORDER_ALREADY_COMPLETED")


class InvalidOrderStatusError(ValMedBusinessException):
    """Raised when attempting an invalid status transition."""
    
    def __init__(self, current_status: str, requested_status: str):
        super().__init__(
            f"Cannot change order status from {current_status} to {requested_status}",
            "INVALID_STATUS_TRANSITION"
        )


# Drug-related exceptions
class DrugNotFoundError(ValMedBusinessException):
    """Raised when a drug is not found."""
    
    def __init__(self, drug_id: str):
        super().__init__(f"Drug with ID {drug_id} not found", "DRUG_NOT_FOUND")


class DrugAlreadyExistsError(ValMedBusinessException):
    """Raised when attempting to create a drug that already exists."""
    
    def __init__(self, name: str, form: str, strength: str):
        super().__init__(
            f"Drug '{name}' with form '{form}' and strength '{strength}' already exists",
            "DRUG_ALREADY_EXISTS"
        )


class InsufficientStockError(ValMedBusinessException):
    """Raised when there's insufficient stock for an operation."""
    
    def __init__(self, drug_name: str, requested: int, available: int):
        super().__init__(
            f"Insufficient stock for {drug_name}. Requested: {requested}, Available: {available}",
            "INSUFFICIENT_STOCK"
        )


class InvalidStockQuantityError(ValMedBusinessException):
    """Raised when stock quantity is invalid."""
    
    def __init__(self, quantity: int):
        super().__init__(f"Stock quantity must be non-negative, got: {quantity}", "INVALID_STOCK_QUANTITY")


# Transfer-related exceptions
class InvalidTransferError(ValMedBusinessException):
    """Raised when a drug transfer is invalid."""
    
    def __init__(self, reason: str):
        super().__init__(f"Invalid drug transfer: {reason}", "INVALID_TRANSFER")


class TransferNotFoundError(ValMedBusinessException):
    """Raised when a drug transfer is not found."""
    
    def __init__(self, transfer_id: str):
        super().__init__(f"Transfer with ID {transfer_id} not found", "TRANSFER_NOT_FOUND")


# Authorization exceptions
class InsufficientPermissionsError(ValMedBusinessException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, required_role: str, user_role: str):
        super().__init__(
            f"Operation requires '{required_role}' role, user has '{user_role}' role",
            "INSUFFICIENT_PERMISSIONS"
        )


# Cache exceptions
class CacheError(ValMedBusinessException):
    """Raised when cache operations fail."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(f"Cache {operation} failed: {reason}", "CACHE_ERROR")


# Data validation exceptions
class InvalidDataError(ValMedBusinessException):
    """Raised when input data is invalid."""
    
    def __init__(self, field: str, reason: str):
        super().__init__(f"Invalid data for field '{field}': {reason}", "INVALID_DATA") 