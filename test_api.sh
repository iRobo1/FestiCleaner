#!/bin/bash

# Test script for Festival Robot Backend API

API="http://localhost:8000"
echo "🤖 Testing Festival Robot Backend API"
echo "======================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function test_endpoint() {
    echo -e "\n${YELLOW}→ Testing: $1${NC}"
    echo "Endpoint: $2"
    response=$(curl -s -o /dev/null -w "%{http_code}" "$2")
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        echo -e "${GREEN}✓ Success (HTTP $response)${NC}"
    else
        echo -e "${RED}✗ Failed (HTTP $response)${NC}"
    fi
}

function test_post() {
    echo -e "\n${YELLOW}→ Testing: $1${NC}"
    echo "Endpoint: $2"
    response=$(curl -s -X POST "$2" \
      -H "Content-Type: application/json" \
      -d "$3" \
      -w "\n%{http_code}")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ Success (HTTP $http_code)${NC}"
        echo "Response: $body"
    else
        echo -e "${RED}✗ Failed (HTTP $http_code)${NC}"
        echo "Response: $body"
    fi
}

# Health check
test_endpoint "Health Check" "$API/health"

# Robot Status
test_endpoint "Get Robot Status" "$API/api/robot/status"

# Map
test_endpoint "Get Map" "$API/api/map"

# Stats
test_endpoint "Get Statistics" "$API/api/stats"

# History
test_endpoint "Get Telemetry History" "$API/api/history/telemetry?limit=5"

# Post telemetry
test_post "Post Telemetry" "$API/api/robot/telemetry" \
  '{
    "battery": 85.5,
    "temperature": 22.3,
    "position": {"x": 1.5, "y": 2.3}
  }'

# Update map
test_post "Update Map" "$API/api/map/update" \
  '{
    "x": 2.0,
    "y": 2.5
  }'

# Camera frame
test_endpoint "Get Camera Frame" "$API/api/camera/frame"

echo -e "\n${YELLOW}=======================================${NC}"
echo -e "${GREEN}Testing complete!${NC}"
echo ""
echo "Additional endpoints to test manually:"
echo "  • Camera stream: $API/api/camera/stream"
echo "  • WebSocket camera: ws://localhost:8000/ws/camera"
echo "  • WebSocket telemetry: ws://localhost:8000/ws/telemetry"
echo "  • Swagger docs: $API/docs"
