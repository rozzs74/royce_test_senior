#!/usr/bin/env python3
"""
Simple test script for the Bowling Shoes Rental Service API
Run this after starting the application to verify endpoints work correctly
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_customer():
    """Test customer creation"""
    print("\nTesting customer creation...")
    customer_data = {
        "name": "Test Customer",
        "age": 70,
        "contact_info": "test@example.com",
        "is_disabled": True,
        "medical_conditions": ["diabetes", "hypertension"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if response.status_code == 201:
            customer = response.json()
            print(f"✅ Customer created: ID {customer['id']}")
            return customer['id']
        else:
            print(f"❌ Customer creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Customer creation failed: {e}")
        return None

def test_get_customers():
    """Test getting all customers"""
    print("\nTesting get all customers...")
    try:
        response = requests.get(f"{BASE_URL}/customers")
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Retrieved {len(customers)} customers")
            return True
        else:
            print(f"❌ Get customers failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get customers failed: {e}")
        return False

def test_discount_calculation():
    """Test discount calculation"""
    print("\nTesting discount calculation...")
    discount_data = {
        "age": 70,
        "is_disabled": True,
        "medical_conditions": ["diabetes", "hypertension"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/calculate-discount", json=discount_data)
        if response.status_code == 200:
            discount = response.json()
            print(f"✅ Discount calculated: {discount['discount_percentage']*100}%")
            print(f"   Reason: {discount['reason']}")
            return True
        else:
            print(f"❌ Discount calculation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Discount calculation failed: {e}")
        return False

def test_create_rental(customer_id):
    """Test rental creation"""
    if not customer_id:
        print("❌ Cannot test rental creation without customer ID")
        return False
        
    print(f"\nTesting rental creation for customer {customer_id}...")
    rental_data = {
        "customer_id": customer_id,
        "shoe_size": 10.5,
        "rental_fee": 25.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rentals", json=rental_data)
        if response.status_code == 201:
            rental = response.json()
            print(f"✅ Rental created: ID {rental['id']}")
            print(f"   Original fee: ${rental['rental_fee']}")
            print(f"   Discount: {rental['discount']*100}%")
            print(f"   Total fee: ${rental['total_fee']}")
            return rental['id']
        else:
            print(f"❌ Rental creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Rental creation failed: {e}")
        return None

def test_get_rentals():
    """Test getting all rentals"""
    print("\nTesting get all rentals...")
    try:
        response = requests.get(f"{BASE_URL}/rentals")
        if response.status_code == 200:
            rentals = response.json()
            print(f"✅ Retrieved {len(rentals)} rentals")
            return True
        else:
            print(f"❌ Get rentals failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get rentals failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎳 Bowling Shoes Rental Service API Tests")
    print("=" * 50)
    
    # Wait for service to be ready
    print("Waiting for service to be ready...")
    for i in range(30):
        if test_health_check():
            break
        time.sleep(1)
    else:
        print("❌ Service not ready after 30 seconds")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 0
    
    # Test discount calculation (doesn't require database)
    total_tests += 1
    if test_discount_calculation():
        tests_passed += 1
    
    # Test customer operations
    total_tests += 1
    customer_id = test_create_customer()
    if customer_id:
        tests_passed += 1
    
    total_tests += 1
    if test_get_customers():
        tests_passed += 1
    
    # Test rental operations
    total_tests += 1
    rental_id = test_create_rental(customer_id)
    if rental_id:
        tests_passed += 1
    
    total_tests += 1
    if test_get_rentals():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 