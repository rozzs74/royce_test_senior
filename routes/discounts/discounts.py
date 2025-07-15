from fastapi import APIRouter, HTTPException, status, Request, Depends

from models.discounts.discounts import DiscountRequest, DiscountResponse
from app.llm_service import llm_service
from utils.api_key_validation import api_key_dependency

router = APIRouter(prefix="/discount", tags=["discount"])


@router.post("/calculate", response_model=DiscountResponse)
async def calculate_discount(
    discount_request: DiscountRequest,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Calculate discount for given customer attributes"""
    try:
        # Pydantic automatically validates the input
        # Calculate discount using LLM
        result = await llm_service.calculate_discount(
            age=discount_request.age,
            is_disabled=discount_request.is_disabled,
            medical_conditions=discount_request.medical_conditions
        )
        
        return DiscountResponse(
            discount_percentage=result['discount_percentage'],
            reason=result['reason']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate discount: {str(e)}"
        )


@router.post("/validate")
async def validate_discount(
    discount_request: DiscountRequest,
    request: Request,
    api_key: str = Depends(api_key_dependency)
):
    """Validate discount calculation by comparing LLM and rule-based results"""
    try:
        result = await llm_service.validate_discount_logic(
            age=discount_request.age,
            is_disabled=discount_request.is_disabled,
            medical_conditions=discount_request.medical_conditions
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate discount: {str(e)}"
        ) 