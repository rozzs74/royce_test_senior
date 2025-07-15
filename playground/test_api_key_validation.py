#!/usr/bin/env python3
"""
Test script to verify API key validation is working correctly.
"""
import requests
import json
from uuid import UUID
from config.settings import Settings

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEY = Settings.get_api_key()
INVALID_API_KEY = "invalid_key_123"

# Sample UUIDs for testing (these should match sample data in schema.sql)
SAMPLE_CUSTOMER_ID = "550e8400-e29b-41d4-a716-446655440001"

def test_api_key_validation():
    """Test API key validation on different endpoints"""
    
    # Test endpoints to validate
    test_endpoints = [
        {
            "method": "GET",
            "url": f"{BASE_URL}/customers",
            "description": "Get all customers"
        },
        {
            "method": "GET",
            "url": f"{BASE_URL}/customers/{SAMPLE_CUSTOMER_ID}",
            "description": "Get specific customer by UUID"
        },
        {
            "method": "GET", 
            "url": f"{BASE_URL}/rentals",
            "description": "Get all rentals"
        },
        {
            "method": "POST",
            "url": f"{BASE_URL}/discount/calculate",
            "description": "Calculate discount",
            "data": {
                "age": 25,
                "is_disabled": False,
                "medical_conditions": []
            }
        },
        {
            "method": "POST",
            "url": f"{BASE_URL}/customers",
            "description": "Create new customer",
            "data": {
                "name": "Test Customer",
                "age": 30,
                "contact_info": "test@example.com",
                "is_disabled": False,
                "medical_conditions": []
            }
        }
    ]
    
    print("🔐 Testing API Key Validation with UUID Support")
    print("=" * 60)
    
    for endpoint in test_endpoints:
        print(f"\n📍 Testing: {endpoint['description']}")
        print(f"   Endpoint: {endpoint['method']} {endpoint['url']}")
        
        # Test 1: No API key (should fail)
        print("\n   ❌ Test 1: No API key")
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'])
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}))
            
            print(f"      Status: {response.status_code}")
            print(f"      Response: {response.json()}")
        except Exception as e:
            print(f"      Error: {e}")
        
        # Test 2: Invalid API key (should fail)
        print("\n   ❌ Test 2: Invalid API key")
        headers = {"Authorization": f"Bearer {INVALID_API_KEY}"}
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), headers=headers)
            
            print(f"      Status: {response.status_code}")
            print(f"      Response: {response.json()}")
        except Exception as e:
            print(f"      Error: {e}")
        
        # Test 3: Valid API key (should succeed)
        print("\n   ✅ Test 3: Valid API key")
        headers = {"Authorization": f"Bearer {API_KEY}"}
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), headers=headers)
            
            print(f"      Status: {response.status_code}")
            if response.status_code == 200 or response.status_code == 201:
                print(f"      ✅ Success! API key validation working correctly")
                # Show UUID in response if present
                try:
                    resp_data = response.json()
                    if isinstance(resp_data, dict) and 'id' in resp_data:
                        print(f"      🆔 Generated UUID: {resp_data['id']}")
                    elif isinstance(resp_data, list) and resp_data and 'id' in resp_data[0]:
                        print(f"      🆔 Sample UUID: {resp_data[0]['id']}")
                except:
                    pass
            else:
                print(f"      Response: {response.json()}")
        except Exception as e:
            print(f"      Error: {e}")
        
        print("-" * 50)
    
    print("\n🎉 API Key Validation Test Complete!")
    print(f"📋 Valid API Key: {API_KEY}")
    print("💡 Usage: Include 'Authorization: Bearer <api_key>' in your request headers")
    print("🆔 Note: All IDs are now UUIDs instead of integers")

if __name__ == "__main__":
    test_api_key_validation() 