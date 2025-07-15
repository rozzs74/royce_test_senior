from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import List

from models import CustomerCreate, CustomerResponse, RentalResponse
from db.pool.db import db_manager
from utils.api_key_validation import api_key_dependency

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Create a new customer"""
    try:
        customer_id = await db_manager.create_customer(customer)
        created_customer = await db_manager.get_customer_by_id(customer_id)
        
        if not created_customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created customer"
            )
            
        return CustomerResponse(**created_customer)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Get customer by ID"""
    try:
        customer = await db_manager.get_customer_by_id(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
            
        return CustomerResponse(**customer)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer: {str(e)}"
        )


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    request: Request,
    api_key: str = Depends(api_key_dependency),
    skip: int = 0,
    limit: int = 100
):
    """List all customers with pagination"""
    try:
        customers = await db_manager.list_customers(skip=skip, limit=limit)
        return [CustomerResponse(**customer) for customer in customers]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list customers: {str(e)}"
        )


@router.get("/{customer_id}/rentals", response_model=List[RentalResponse])
async def get_customer_rentals(
    customer_id: str,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Get all rentals for a specific customer"""
    try:
        # First check if customer exists
        customer = await db_manager.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
            
        rentals = await db_manager.get_rentals_by_customer_id(customer_id)
        return [RentalResponse(**rental) for rental in rentals]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer rentals: {str(e)}"
        ) 