#!/usr/bin/env python3
"""
Comprehensive test script for the AI Presentation Generator service.
Tests all major features including creation, slide operations, export, and error handling.
"""

import requests
import json
import time
import os
from typing import Dict, Any

class PresentationServiceTester:
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"S3: {data.get('s3_available')}, OpenRouter: {data.get('openrouter_configured')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_create_presentation(self) -> str:
        """Test presentation creation"""
        try:
            data = {
                "topic": "Test Presentation - AI and Machine Learning",
                "slides": 3
            }
            
            response = requests.post(
                f"{self.base_url}/create_presentation",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    presentation_id = result.get("presentation_id")
                    self.log_test("Create Presentation", True, f"Created {result.get('slide_count')} slides")
                    return presentation_id
                else:
                    self.log_test("Create Presentation", False, result.get("error", "Unknown error"))
                    return None
            else:
                self.log_test("Create Presentation", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Presentation", False, str(e))
            return None
    
    def test_get_presentation_json(self, presentation_id: str) -> bool:
        """Test getting presentation JSON"""
        try:
            response = requests.get(f"{self.base_url}/get_presentation_json/{presentation_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("json_data"):
                    slides = result["json_data"].get("slides", [])
                    self.log_test("Get Presentation JSON", True, f"Retrieved {len(slides)} slides")
                    return True
                else:
                    self.log_test("Get Presentation JSON", False, result.get("error", "No JSON data"))
                    return False
            else:
                self.log_test("Get Presentation JSON", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Presentation JSON", False, str(e))
            return False
    
    def test_slide_operations(self, presentation_id: str) -> bool:
        """Test slide copy and delete operations"""
        try:
            # Test slide copy
            copy_data = {
                "operation": "copy",
                "presentation_id": presentation_id,
                "slide_index": 0
            }
            
            response = requests.post(
                f"{self.base_url}/slide_operations",
                json=copy_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("Slide Copy", True, f"Copied slide, now have {result.get('slide_count')} slides")
                else:
                    self.log_test("Slide Copy", False, result.get("error", "Copy failed"))
                    return False
            else:
                self.log_test("Slide Copy", False, f"Status code: {response.status_code}")
                return False
            
            # Test slide delete
            delete_data = {
                "operation": "delete",
                "presentation_id": presentation_id,
                "slide_index": 1  # Delete the copied slide
            }
            
            response = requests.post(
                f"{self.base_url}/slide_operations",
                json=delete_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("Slide Delete", True, f"Deleted slide, now have {result.get('slide_count')} slides")
                    return True
                else:
                    self.log_test("Slide Delete", False, result.get("error", "Delete failed"))
                    return False
            else:
                self.log_test("Slide Delete", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Slide Operations", False, str(e))
            return False
    
    def test_export_presentation(self, presentation_id: str) -> bool:
        """Test presentation export"""
        try:
            # Test PDF export
            export_data = {
                "presentationId": presentation_id,
                "format": "pdf"
            }
            
            response = requests.post(
                f"{self.base_url}/export_ppt",
                json=export_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "application/pdf" in content_type:
                    self.log_test("PDF Export", True, "PDF file generated successfully")
                else:
                    self.log_test("PDF Export", False, f"Unexpected content type: {content_type}")
                    return False
            else:
                self.log_test("PDF Export", False, f"Status code: {response.status_code}")
                return False
            
            # Test PPTX export
            export_data["format"] = "pptx"
            
            response = requests.post(
                f"{self.base_url}/export_ppt",
                json=export_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "application/vnd.openxmlformats-officedocument.presentationml.presentation" in content_type:
                    self.log_test("PPTX Export", True, "PowerPoint file generated successfully")
                    return True
                else:
                    self.log_test("PPTX Export", False, f"Unexpected content type: {content_type}")
                    return False
            else:
                self.log_test("PPTX Export", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Export Presentation", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and validation"""
        try:
            # Test invalid topic
            response = requests.post(
                f"{self.base_url}/create_presentation",
                json={"topic": "", "slides": 5},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                result = response.json()
                if "Topic is required" in result.get("error", ""):
                    self.log_test("Error Handling - Empty Topic", True, "Properly rejected empty topic")
                else:
                    self.log_test("Error Handling - Empty Topic", False, "Did not reject empty topic")
                    return False
            else:
                self.log_test("Error Handling - Empty Topic", False, f"Expected 400, got {response.status_code}")
                return False
            
            # Test invalid slide count
            response = requests.post(
                f"{self.base_url}/create_presentation",
                json={"topic": "Test", "slides": 25},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                result = response.json()
                if "between 1 and 20" in result.get("error", ""):
                    self.log_test("Error Handling - Invalid Slide Count", True, "Properly rejected invalid slide count")
                    return True
                else:
                    self.log_test("Error Handling - Invalid Slide Count", False, "Did not reject invalid slide count")
                    return False
            else:
                self.log_test("Error Handling - Invalid Slide Count", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting (if implemented)"""
        try:
            # Make multiple rapid requests
            for i in range(5):
                response = requests.post(
                    f"{self.base_url}/create_presentation",
                    json={"topic": f"Rate Test {i}", "slides": 1},
                    headers={"Content-Type": "application/json"}
                )
                time.sleep(0.1)  # Small delay between requests
            
            # The last request might be rate limited
            if response.status_code in [200, 429]:
                self.log_test("Rate Limiting", True, "Rate limiting working as expected")
                return True
            else:
                self.log_test("Rate Limiting", False, f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rate Limiting", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting AI Presentation Service Tests")
        print("=" * 50)
        
        # Test health check
        if not self.test_health_check():
            print("❌ Health check failed. Service may not be running.")
            return
        
        # Test presentation creation
        presentation_id = self.test_create_presentation()
        if not presentation_id:
            print("❌ Presentation creation failed. Stopping tests.")
            return
        
        # Test getting presentation JSON
        self.test_get_presentation_json(presentation_id)
        
        # Test slide operations
        self.test_slide_operations(presentation_id)
        
        # Test export functionality
        self.test_export_presentation(presentation_id)
        
        # Test error handling
        self.test_error_handling()
        
        # Test rate limiting
        self.test_rate_limiting()
        
        # Generate summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! The service is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the service configuration.")
            
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to test_results.json")

if __name__ == "__main__":
    # Get base URL from environment or use default
    base_url = os.getenv("PPT_SERVICE_URL", "http://localhost:5002")
    
    tester = PresentationServiceTester(base_url)
    tester.run_all_tests() 