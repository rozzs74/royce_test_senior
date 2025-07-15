from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Customer's full name")
    age: int = Field(..., ge=0, le=120, description="Customer's age")
    contact_info: str = Field(..., min_length=1, max_length=200, description="Customer's contact information")
    is_disabled: bool = Field(default=False, description="Whether the customer is disabled")
    medical_conditions: Optional[List[str]] = Field(default=None, description="List of medical conditions")

    @validator('medical_conditions')
    def validate_medical_conditions(cls, v):
        if v is not None:
            valid_conditions = ['diabetes', 'hypertension', 'chronic condition']
            for condition in v:
                if condition.lower() not in valid_conditions:
                    raise ValueError(f"Invalid medical condition: {condition}. Valid conditions are: {', '.join(valid_conditions)}")
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    @validator('contact_info')
    def validate_contact_info(cls, v):
        if not v or v.isspace():
            raise ValueError("Contact info cannot be empty or just whitespace")
        return v.strip()


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: UUID = Field(..., description="Unique customer identifier (UUID)")
    created_at: datetime

    class Config:
        from_attributes = True
