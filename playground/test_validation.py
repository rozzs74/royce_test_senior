#!/usr/bin/env python3
"""
Test script to verify Pydantic validation works correctly
"""

from app.models import CustomerCreate, RentalCreate, DiscountRequest
from pydantic import ValidationError
import json


def test_customer_validation():
    """Test customer validation"""
    print("Testing Customer Validation...")
    
    # Valid customer
    try:
        customer = CustomerCreate(
            name="John Doe",
            age=25,
            contact_info="john@example.com",
            is_disabled=False,
            medical_conditions=["diabetes"]
        )
        print("✅ Valid customer created successfully")
    except ValidationError as e:
        print(f"❌ Unexpected validation error: {e}")
        return False
    
    # Test invalid medical condition
    try:
        customer = CustomerCreate(
            name="John Doe",
            age=25,
            contact_info="john@example.com",
            is_disabled=False,
            medical_conditions=["invalid_condition"]
        )
        print("❌ Should have failed with invalid medical condition")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid medical condition")
    
    # Test invalid age
    try:
        customer = CustomerCreate(
            name="John Doe",
            age=150,  # Invalid age
            contact_info="john@example.com",
            is_disabled=False
        )
        print("❌ Should have failed with invalid age")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid age")
    
    # Test empty name
    try:
        customer = CustomerCreate(
            name="   ",  # Empty name
            age=25,
            contact_info="john@example.com",
            is_disabled=False
        )
        print("❌ Should have failed with empty name")
        return False
    except ValidationError as e:
        print("✅ Correctly caught empty name")
    
    return True


def test_rental_validation():
    """Test rental validation"""
    print("\nTesting Rental Validation...")
    
    # Valid rental
    try:
        rental = RentalCreate(
            customer_id=1,
            shoe_size=10.5,
            rental_fee=25.00
        )
        print("✅ Valid rental created successfully")
        print(f"   Shoe size normalized to: {rental.shoe_size}")
        print(f"   Rental fee normalized to: {rental.rental_fee}")
    except ValidationError as e:
        print(f"❌ Unexpected validation error: {e}")
        return False
    
    # Test invalid shoe size
    try:
        rental = RentalCreate(
            customer_id=1,
            shoe_size=25.0,  # Invalid shoe size
            rental_fee=25.00
        )
        print("❌ Should have failed with invalid shoe size")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid shoe size")
    
    # Test invalid customer ID
    try:
        rental = RentalCreate(
            customer_id=0,  # Invalid customer ID
            shoe_size=10.5,
            rental_fee=25.00
        )
        print("❌ Should have failed with invalid customer ID")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid customer ID")
    
    # Test negative rental fee
    try:
        rental = RentalCreate(
            customer_id=1,
            shoe_size=10.5,
            rental_fee=-5.00  # Negative fee
        )
        print("❌ Should have failed with negative rental fee")
        return False
    except ValidationError as e:
        print("✅ Correctly caught negative rental fee")
    
    return True


def test_discount_validation():
    """Test discount request validation"""
    print("\nTesting Discount Request Validation...")
    
    # Valid discount request
    try:
        discount_req = DiscountRequest(
            age=70,
            is_disabled=True,
            medical_conditions=["diabetes", "hypertension"]
        )
        print("✅ Valid discount request created successfully")
    except ValidationError as e:
        print(f"❌ Unexpected validation error: {e}")
        return False
    
    # Test invalid medical condition
    try:
        discount_req = DiscountRequest(
            age=70,
            is_disabled=True,
            medical_conditions=["invalid_condition"]
        )
        print("❌ Should have failed with invalid medical condition")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid medical condition")
    
    # Test invalid age
    try:
        discount_req = DiscountRequest(
            age=200,  # Invalid age
            is_disabled=True
        )
        print("❌ Should have failed with invalid age")
        return False
    except ValidationError as e:
        print("✅ Correctly caught invalid age")
    
    return True


def test_shoe_size_normalization():
    """Test shoe size normalization to nearest 0.5"""
    print("\nTesting Shoe Size Normalization...")
    
    test_cases = [
        (10.1, 10.0),
        (10.3, 10.5),
        (10.7, 10.5),
        (10.9, 11.0),
        (8.25, 8.5),
        (8.75, 9.0)
    ]
    
    for input_size, expected_size in test_cases:
        try:
            rental = RentalCreate(
                customer_id=1,
                shoe_size=input_size,
                rental_fee=25.00
            )
            if rental.shoe_size == expected_size:
                print(f"✅ {input_size} -> {rental.shoe_size} (expected {expected_size})")
            else:
                print(f"❌ {input_size} -> {rental.shoe_size} (expected {expected_size})")
                return False
        except ValidationError as e:
            print(f"❌ Validation error for size {input_size}: {e}")
            return False
    
    return True


def main():
    """Run all validation tests"""
    print("🎳 Pydantic Validation Tests")
    print("=" * 50)
    
    tests = [
        test_customer_validation,
        test_rental_validation,
        test_discount_validation,
        test_shoe_size_normalization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("❌ Some validation tests failed!")
        return 1


if __name__ == "__main__":
    exit(main()) 