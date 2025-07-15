from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class RentalBase(BaseModel):
    customer_id: UUID = Field(..., description="UUID of the customer renting shoes")
    shoe_size: float = Field(..., gt=0, le=20, description="Shoe size (US sizing)")
    rental_fee: float = Field(..., gt=0, description="Base rental fee before discount")

    @validator('shoe_size')
    def validate_shoe_size(cls, v):
        # Common shoe sizes are typically between 1 and 20
        if v < 1 or v > 20:
            raise ValueError("Shoe size must be between 1 and 20")
        # Round to nearest 0.5 for realistic shoe sizes
        return round(v * 2) / 2

    @validator('rental_fee')
    def validate_rental_fee(cls, v):
        if v <= 0:
            raise ValueError("Rental fee must be positive")
        # Round to 2 decimal places for currency
        return round(v, 2)


class RentalCreate(RentalBase):
    discount: float = Field(default=0.0, ge=0, le=1, description="Discount applied (0.0 to 1.0)")
    total_fee: float = Field(default=0.0, ge=0, description="Final fee after discount")


class RentalResponse(RentalBase):
    id: UUID = Field(..., description="Unique rental identifier (UUID)")
    rental_date: datetime
    discount: float = Field(..., ge=0, le=1, description="Discount applied (0.0 to 1.0)")
    total_fee: float = Field(..., ge=0, description="Final fee after discount")

    class Config:
        from_attributes = True
