#!/bin/bash
# Test Wallet Balance Script
# This script tests the wallet balance endpoint

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if we're in the project directory
if [ ! -f "$PROJECT_ROOT/backend/main.py" ]; then
    echo '{"success": false, "error": "Not in project directory"}' >&2
    exit 1
fi

# Check if the backend is running
if ! curl -s http://localhost:8000/api/v1/wallet/health > /dev/null 2>&1; then
    echo '{"success": false, "error": "Backend server not running on port 8000"}' >&2
    exit 1
fi

# Test wallet balance endpoint
echo "Testing wallet balance endpoint..." >&2
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wallet/balance" \
    -H "Content-Type: application/json")

# Check if response is valid JSON
if ! echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo "{\"success\": false, \"error\": \"Invalid JSON response\", \"response\": \"$RESPONSE\"}" >&2
    exit 1
fi

# Check if balance field exists
BALANCE=$(echo "$RESPONSE" | jq -r '.balance_sol // empty')
if [ -z "$BALANCE" ]; then
    echo "{\"success\": false, \"error\": \"Missing balance_sol field\", \"response\": $RESPONSE}" >&2
    exit 1
fi

# Check if balance is a valid number
if ! [[ "$BALANCE" =~ ^[0-9]*\.?[0-9]+$ ]]; then
    echo "{\"success\": false, \"error\": \"Invalid balance format\", \"balance\": \"$BALANCE\"}" >&2
    exit 1
fi

echo "{\"success\": true, \"message\": \"Wallet balance test completed successfully\", \"balance_sol\": $BALANCE}" >&2
echo "{\"success\": true, \"message\": \"Wallet balance test completed successfully\", \"balance_sol\": $BALANCE}"
exit 0