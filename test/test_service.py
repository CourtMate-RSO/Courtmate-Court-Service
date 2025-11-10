#!/usr/bin/env python3
"""
Court Service Integration Test Suite
Run after: docker-compose up
Usage: python test_service.py
"""

import requests
import json
import time
import sys
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/facilities"

# Test counters
passed = 0
failed = 0
facility_id: Optional[str] = None


def print_header(text: str):
    """Print a header"""
    print(f"\n{Fore.BLUE}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Style.RESET_ALL}\n")


def print_test(text: str):
    """Print test description"""
    print(f"{Fore.YELLOW}TEST: {Style.RESET_ALL}{text}")


def print_success(text: str):
    """Print success message"""
    global passed
    passed += 1
    print(f"{Fore.GREEN}✓ PASSED: {Style.RESET_ALL}{text}")


def print_error(text: str):
    """Print error message"""
    global failed
    failed += 1
    print(f"{Fore.RED}✗ FAILED: {Style.RESET_ALL}{text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ INFO: {Style.RESET_ALL}{text}")


def wait_for_service(max_attempts: int = 30) -> bool:
    """Wait for service to be ready"""
    print_header("Checking if service is ready")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print_success("Service is ready!")
                return True
        except requests.exceptions.RequestException:
            print(".", end="", flush=True)
            time.sleep(1)
    
    print_error(f"Service did not start within {max_attempts} seconds")
    return False


def test_health_root():
    """Test health check at root"""
    print_test("Health check at root /health")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            if "healthy" in str(data).lower():
                print_success("Root health check returned 200 and contains 'healthy'")
                print_info(f"Response: {data}")
            else:
                print_error("Root health check returned 200 but doesn't contain 'healthy'")
                print_info(f"Response: {data}")
        else:
            print_error(f"Root health check failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_health_api():
    """Test health check at API endpoint"""
    print_test(f"Health check at {API_PREFIX}/health")
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/health")
        
        if response.status_code == 200:
            print_success("API health check returned 200")
            print_info(f"Response: {response.json()}")
        else:
            print_error(f"API health check failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_root():
    """Test root endpoint"""
    print_test("Root endpoint /")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            if "Court Service" in str(data):
                print_success("Root endpoint returned 200 and contains service info")
                print_info(f"Response: {data}")
            else:
                print_error("Root endpoint returned 200 but unexpected content")
                print_info(f"Response: {data}")
        else:
            print_error(f"Root endpoint failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_docs():
    """Test API documentation endpoint"""
    print_test("API documentation endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/docs")
        
        if response.status_code == 200:
            print_success(f"API docs accessible at {BASE_URL}{API_PREFIX}/docs")
        else:
            print_error(f"API docs failed with status {response.status_code} (might be disabled in prod)")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_create_facility():
    """Test creating a new facility"""
    global facility_id
    print_test("Create a new facility")
    
    facility_data = {
        "name": "Test Basketball Court",
        "location": {
            "latitude": 46.0569,
            "longitude": 14.5058
        },
        "address_line": "Kongresni trg 12",
        "city": "Ljubljana",
        "country": "Slovenia",
        "image": "https://example.com/court.jpg"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/facilities",
            json=facility_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            facility_id = data.get("id")
            print_success("Facility created successfully")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            if facility_id:
                print_info(f"Created facility ID: {facility_id}")
        else:
            print_error(f"Failed to create facility with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_list_facilities():
    """Test listing all facilities"""
    print_test("List all facilities")
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/facilities")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                facility_count = len(data)
                print_success(f"List facilities returned 200 with {facility_count} facilities")
                preview = json.dumps(data[:2] if len(data) > 2 else data, indent=2)
                print_info(f"Response preview: {preview}...")
            else:
                print_error("List facilities returned 200 but invalid format")
                print_info(f"Response: {data}")
        else:
            print_error(f"List facilities failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_get_facility():
    """Test getting facility by ID"""
    if not facility_id:
        print_test("Get facility by ID (SKIPPED - no facility ID available)")
        print_info("Create a facility first to test this endpoint")
        return
    
    print_test(f"Get facility by ID: {facility_id}")
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/facilities/{facility_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("id") == facility_id:
                print_success("Get facility by ID returned correct facility")
                print_info(f"Response: {json.dumps(data, indent=2)}")
            else:
                print_error("Get facility by ID returned 200 but wrong data")
                print_info(f"Response: {data}")
        else:
            print_error(f"Get facility by ID failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_get_facility_invalid():
    """Test getting facility by invalid ID"""
    print_test("Get facility by invalid ID (should return 400 or 404)")
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/facilities/invalid-id-123")
        
        if response.status_code in [400, 404]:
            print_success(f"Invalid ID correctly rejected with status {response.status_code}")
            print_info(f"Response: {response.text}")
        else:
            print_error(f"Invalid ID should return 400 or 404, got {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_nearby_facilities():
    """Test searching for nearby facilities"""
    print_test("Search for nearby facilities")
    
    search_data = {
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 10.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/nearby",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "courts" in data:
                court_count = len(data["courts"])
                print_success(f"Nearby search returned 200 with {court_count} courts")
                preview = json.dumps(data, indent=2)[:500]
                print_info(f"Response preview: {preview}...")
            else:
                print_error("Nearby search returned 200 but invalid format")
                print_info(f"Response: {data}")
        else:
            print_error(f"Nearby search failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_nearby_invalid():
    """Test searching nearby with invalid coordinates"""
    print_test("Search nearby with invalid coordinates (should return 422)")
    
    invalid_data = {
        "latitude": 999,
        "longitude": 999,
        "radius_km": 10.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/nearby",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print_success("Invalid coordinates correctly rejected with status 422")
            print_info(f"Response: {response.text}")
        else:
            print_error(f"Invalid coordinates should return 422, got {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_create_facility_invalid():
    """Test creating facility with missing required fields"""
    print_test("Create facility with missing location (should return 422)")
    
    invalid_data = {
        "name": "Invalid Court",
        "city": "Ljubljana"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/facilities",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print_success("Invalid facility data correctly rejected with status 422")
            print_info(f"Response: {response.text}")
        else:
            print_error(f"Invalid facility should return 422, got {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_nearby_large_radius():
    """Test searching with large radius"""
    print_test("Search nearby with large radius (50km - max allowed)")
    
    search_data = {
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 50.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/nearby",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("Large radius search (50km) succeeded")
            preview = str(response.json())[:200]
            print_info(f"Response preview: {preview}...")
        else:
            print_error(f"Large radius search failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def test_nearby_exceeded_radius():
    """Test searching with exceeded radius limit"""
    print_test("Search nearby with exceeded radius (51km - should return 422)")
    
    search_data = {
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 51.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/nearby",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print_success("Exceeded radius correctly rejected with status 422")
            print_info(f"Response: {response.text}")
        else:
            print_error(f"Exceeded radius should return 422, got {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Request failed: {str(e)}")


def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = passed + failed
    print(f"Total Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}✓ All tests passed!{Style.RESET_ALL}\n")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}✗ Some tests failed{Style.RESET_ALL}\n")
        sys.exit(1)


def main():
    """Main execution"""
    print_header("Court Service Integration Tests")
    print_info(f"Testing service at: {BASE_URL}")
    print_info(f"API prefix: {API_PREFIX}")
    
    if not wait_for_service():
        sys.exit(1)
    
    # Run all tests
    test_health_root()
    test_health_api()
    test_root()
    test_docs()
    test_create_facility()
    test_list_facilities()
    test_get_facility()
    test_get_facility_invalid()
    test_nearby_facilities()
    test_nearby_invalid()
    test_create_facility_invalid()
    test_nearby_large_radius()
    test_nearby_exceeded_radius()
    
    print_summary()


if __name__ == "__main__":
    main()
