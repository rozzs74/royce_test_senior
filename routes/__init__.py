from .customers import router as customers_router
from .rentals import router as rentals_router
from .discounts import router as discount_router

__all__ = ["customers_router", "rentals_router", "discount_router"] 