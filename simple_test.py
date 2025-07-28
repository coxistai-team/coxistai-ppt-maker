#!/usr/bin/env python3
"""
Simple test script to verify basic functionality without AI API
"""

import requests
import json
import time

def test_basic_functionality():
    """Test basic functionality without AI generation"""
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Basic Functionality")
    print("=" * 40)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status')}")
            print(f"   S3 Available: {data.get('s3_available')}")
            print(f"   OpenRouter Configured: {data.get('openrouter_configured')}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    # Test slide operations with a mock presentation
    print("\n📊 Testing Slide Operations")
    
    # Create a mock presentation ID
    presentation_id = f"test_pres_{int(time.time())}"
    
    # Test slide copy
    try:
        copy_data = {
            "operation": "copy",
            "presentation_id": presentation_id,
            "slide_index": 0
        }
        
        response = requests.post(
            f"{base_url}/slide_operations",
            json=copy_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Slide Copy: {result.get('message')}")
                print(f"   Slide Count: {result.get('slide_count')}")
            else:
                print(f"❌ Slide Copy Failed: {result.get('error')}")
        else:
            print(f"❌ Slide Copy HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Slide Copy Error: {e}")
    
    # Test slide delete
    try:
        delete_data = {
            "operation": "delete",
            "presentation_id": presentation_id,
            "slide_index": 1
        }
        
        response = requests.post(
            f"{base_url}/slide_operations",
            json=delete_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Slide Delete: {result.get('message')}")
                print(f"   Slide Count: {result.get('slide_count')}")
            else:
                print(f"❌ Slide Delete Failed: {result.get('error')}")
        else:
            print(f"❌ Slide Delete HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Slide Delete Error: {e}")
    
    # Test error handling
    print("\n🔍 Testing Error Handling")
    
    # Test invalid operation
    try:
        invalid_data = {
            "operation": "invalid",
            "presentation_id": presentation_id,
            "slide_index": 0
        }
        
        response = requests.post(
            f"{base_url}/slide_operations",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            result = response.json()
            print(f"✅ Invalid Operation: Properly rejected")
        else:
            print(f"❌ Invalid Operation: Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid Operation Error: {e}")
    
    # Test missing fields
    try:
        incomplete_data = {
            "operation": "copy"
            # Missing presentation_id and slide_index
        }
        
        response = requests.post(
            f"{base_url}/slide_operations",
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            result = response.json()
            print(f"✅ Missing Fields: Properly rejected")
        else:
            print(f"❌ Missing Fields: Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Missing Fields Error: {e}")
    
    print("\n🎉 Basic functionality tests completed!")
    return True

if __name__ == "__main__":
    test_basic_functionality() 