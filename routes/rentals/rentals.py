from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import List

from models import RentalCreate, RentalResponse
from db.pool.db import db_manager
from utils.api_key_validation import api_key_dependency

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.post("/", response_model=RentalResponse)
async def create_rental(
    rental: RentalCreate,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Create a new rental"""
    try:
        # Check if customer exists - use direct method, not db_manager.customers
        customer = await db_manager.get_customer_by_id(str(rental.customer_id))
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Calculate total fee (you might want to calculate discount here)
        total_fee = rental.rental_fee * (1 - getattr(rental, 'discount', 0))
        
        # Create rental data with calculated total
        rental_data = rental.copy()
        if not hasattr(rental_data, 'discount'):
            rental_data.discount = 0.0
        if not hasattr(rental_data, 'total_fee'):
            rental_data.total_fee = total_fee
        
        rental_id = await db_manager.create_rental(rental_data)
        created_rental = await db_manager.get_rental_by_id(rental_id)
        
        if not created_rental:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created rental"
            )
            
        return RentalResponse(**created_rental)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rental: {str(e)}"
        )


@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: str,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Get rental by ID"""
    try:
        rental = await db_manager.get_rental_by_id(rental_id)
        
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found"
            )
            
        return RentalResponse(**rental)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rental: {str(e)}"
        )


@router.get("/", response_model=List[RentalResponse])
async def list_rentals(
    request: Request,
    api_key: str = Depends(api_key_dependency),
    skip: int = 0,
    limit: int = 100
):
    """List all rentals with pagination"""
    try:
        rentals = await db_manager.list_rentals(skip=skip, limit=limit)
        return [RentalResponse(**rental) for rental in rentals]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rentals: {str(e)}"
        )


@router.put("/{rental_id}/return", response_model=RentalResponse)
async def return_rental(
    rental_id: str,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Mark rental as returned"""
    try:
        # Check if rental exists
        rental = await db_manager.rentals.get_rental_by_id(rental_id)
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found"
            )
            
        # Update rental status
        await db_manager.rentals.return_rental(rental_id)
        updated_rental = await db_manager.rentals.get_rental_by_id(rental_id)
        
        return updated_rental
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to return rental: {str(e)}"
        ) 