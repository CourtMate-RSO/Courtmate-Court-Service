#!/bin/bash

# ============================================
# Court Service Integration Test Script
# ============================================
# Tests all endpoints of the Court Service
# Run after: docker-compose up
# Usage: ./test_service.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1/facilities"

# Test counters
PASSED=0
FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ PASSED:${NC} $1"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}✗ FAILED:${NC} $1"
    ((FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ INFO:${NC} $1"
}

# Wait for service to be ready
wait_for_service() {
    print_header "Checking if service is ready"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
            print_success "Service is ready!"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    print_error "Service did not start within $max_attempts seconds"
    exit 1
}

# Test 1: Health Check (Root)
test_health_root() {
    print_test "Health check at root /health"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "healthy"; then
            print_success "Root health check returned 200 and contains 'healthy'"
            print_info "Response: $body"
        else
            print_error "Root health check returned 200 but response doesn't contain 'healthy'"
            print_info "Response: $body"
        fi
    else
        print_error "Root health check failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 2: Health Check (API)
test_health_api() {
    print_test "Health check at $API_PREFIX/health"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "API health check returned 200"
        print_info "Response: $body"
    else
        print_error "API health check failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 3: Root endpoint
test_root() {
    print_test "Root endpoint /"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "Court Service"; then
            print_success "Root endpoint returned 200 and contains service info"
            print_info "Response: $body"
        else
            print_error "Root endpoint returned 200 but unexpected content"
            print_info "Response: $body"
        fi
    else
        print_error "Root endpoint failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 4: API Documentation
test_docs() {
    print_test "API documentation endpoint"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX/docs")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "API docs accessible at $BASE_URL$API_PREFIX/docs"
    else
        print_error "API docs failed with status $http_code (might be disabled in prod)"
    fi
}

# Test 5: Create a facility
test_create_facility() {
    print_test "Create a new facility"
    
    local facility_data='{
        "name": "Test Basketball Court",
        "location": {
            "latitude": 46.0569,
            "longitude": 14.5058
        },
        "address_line": "Kongresni trg 12",
        "city": "Ljubljana",
        "country": "Slovenia",
        "image": "https://example.com/court.jpg"
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/facilities" \
        -H "Content-Type: application/json" \
        -d "$facility_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 201 ]; then
        print_success "Facility created successfully"
        print_info "Response: $body"
        
        # Extract facility ID for later tests
        FACILITY_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"\(.*\)"/\1/')
        if [ -n "$FACILITY_ID" ]; then
            print_info "Created facility ID: $FACILITY_ID"
        fi
    else
        print_error "Failed to create facility with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 6: List all facilities
test_list_facilities() {
    print_test "List all facilities"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX/facilities")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q '\['; then
            facility_count=$(echo "$body" | grep -o '"id"' | wc -l)
            print_success "List facilities returned 200 with $facility_count facilities"
            print_info "Response preview: $(echo "$body" | head -c 200)..."
        else
            print_error "List facilities returned 200 but invalid format"
            print_info "Response: $body"
        fi
    else
        print_error "List facilities failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 7: Get facility by ID
test_get_facility() {
    if [ -z "$FACILITY_ID" ]; then
        print_test "Get facility by ID (SKIPPED - no facility ID available)"
        print_info "Create a facility first to test this endpoint"
        return
    fi
    
    print_test "Get facility by ID: $FACILITY_ID"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX/facilities/$FACILITY_ID")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "$FACILITY_ID"; then
            print_success "Get facility by ID returned correct facility"
            print_info "Response: $body"
        else
            print_error "Get facility by ID returned 200 but wrong data"
            print_info "Response: $body"
        fi
    else
        print_error "Get facility by ID failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 8: Get facility by invalid ID
test_get_facility_invalid() {
    print_test "Get facility by invalid ID (should return 400 or 404)"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX/facilities/invalid-id-123")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 400 ] || [ "$http_code" -eq 404 ]; then
        print_success "Invalid ID correctly rejected with status $http_code"
        print_info "Response: $body"
    else
        print_error "Invalid ID should return 400 or 404, got $http_code"
        print_info "Response: $body"
    fi
}

# Test 9: Search nearby facilities
test_nearby_facilities() {
    print_test "Search for nearby facilities"
    
    local search_data='{
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 10.0
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/nearby" \
        -H "Content-Type: application/json" \
        -d "$search_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q '"courts"'; then
            court_count=$(echo "$body" | grep -o '"id"' | wc -l)
            print_success "Nearby search returned 200 with $court_count courts"
            print_info "Response preview: $(echo "$body" | head -c 300)..."
        else
            print_error "Nearby search returned 200 but invalid format"
            print_info "Response: $body"
        fi
    else
        print_error "Nearby search failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 10: Search nearby with invalid coordinates
test_nearby_invalid() {
    print_test "Search nearby with invalid coordinates (should return 422)"
    
    local invalid_data='{
        "latitude": 999,
        "longitude": 999,
        "radius_km": 10.0
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/nearby" \
        -H "Content-Type: application/json" \
        -d "$invalid_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 422 ]; then
        print_success "Invalid coordinates correctly rejected with status 422"
        print_info "Response: $body"
    else
        print_error "Invalid coordinates should return 422, got $http_code"
        print_info "Response: $body"
    fi
}

# Test 11: Create facility with missing required fields
test_create_facility_invalid() {
    print_test "Create facility with missing location (should return 422)"
    
    local invalid_data='{
        "name": "Invalid Court",
        "city": "Ljubljana"
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/facilities" \
        -H "Content-Type: application/json" \
        -d "$invalid_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 422 ]; then
        print_success "Invalid facility data correctly rejected with status 422"
        print_info "Response: $body"
    else
        print_error "Invalid facility should return 422, got $http_code"
        print_info "Response: $body"
    fi
}

# Test 12: Large radius search
test_nearby_large_radius() {
    print_test "Search nearby with large radius (50km - max allowed)"
    
    local search_data='{
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 50.0
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/nearby" \
        -H "Content-Type: application/json" \
        -d "$search_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Large radius search (50km) succeeded"
        print_info "Response preview: $(echo "$body" | head -c 200)..."
    else
        print_error "Large radius search failed with status $http_code"
        print_info "Response: $body"
    fi
}

# Test 13: Exceeded radius limit
test_nearby_exceeded_radius() {
    print_test "Search nearby with exceeded radius (51km - should return 422)"
    
    local search_data='{
        "latitude": 46.0569,
        "longitude": 14.5058,
        "radius_km": 51.0
    }'
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX/nearby" \
        -H "Content-Type: application/json" \
        -d "$search_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 422 ]; then
        print_success "Exceeded radius correctly rejected with status 422"
        print_info "Response: $body"
    else
        print_error "Exceeded radius should return 422, got $http_code"
        print_info "Response: $body"
    fi
}

# Print summary
print_summary() {
    print_header "Test Summary"
    
    local total=$((PASSED + FAILED))
    echo -e "Total Tests: $total"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All tests passed!${NC}\n"
        exit 0
    else
        echo -e "\n${RED}✗ Some tests failed${NC}\n"
        exit 1
    fi
}

# Main execution
main() {
    print_header "Court Service Integration Tests"
    print_info "Testing service at: $BASE_URL"
    print_info "API prefix: $API_PREFIX"
    
    wait_for_service
    
    # Run all tests
    test_health_root
    test_health_api
    test_root
    test_docs
    test_create_facility
    test_list_facilities
    test_get_facility
    test_get_facility_invalid
    test_nearby_facilities
    test_nearby_invalid
    test_create_facility_invalid
    test_nearby_large_radius
    test_nearby_exceeded_radius
    
    print_summary
}

# Run main function
main
