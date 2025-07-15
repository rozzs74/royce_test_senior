from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class DiscountRequest(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Customer's age")
    is_disabled: bool = Field(..., description="Whether the customer is disabled")
    medical_conditions: Optional[List[str]] = Field(default=None, description="List of medical conditions")

    @validator('medical_conditions')
    def validate_medical_conditions(cls, v):
        if v is not None:
            valid_conditions = ['diabetes', 'hypertension', 'chronic condition']
            for condition in v:
                if condition.lower() not in valid_conditions:
                    raise ValueError(f"Invalid medical condition: {condition}. Valid conditions are: {', '.join(valid_conditions)}")
        return v


class DiscountResponse(BaseModel):
    discount_percentage: float = Field(..., ge=0, le=1, description="Discount percentage (0.0 to 1.0)")
    reason: str = Field(..., description="Explanation for the discount applied")
