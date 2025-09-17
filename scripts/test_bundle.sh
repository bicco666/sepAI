#!/bin/bash

# Bundle Test Script - Runs all individual tests
echo "Running Complete Test Suite..." >&2

# Array of test scripts to run
TEST_SCRIPTS=(
    "test_wallet_status.sh"
    "test_wallet_balance.sh"
    "test_wallet_network.sh"
    "test_wallet_health.sh"
    "test_agent_status.sh"
    "test_system_health.sh"
    "test_ideas_list.sh"
    "test_strategies_list.sh"
    "test_trades_history.sh"
)

TOTAL_TESTS=${#TEST_SCRIPTS[@]}
PASSED=0
FAILED=0
RESULTS=()

for script in "${TEST_SCRIPTS[@]}"; do
    script_path="scripts/$script"

    if [ -f "$script_path" ] && [ -x "$script_path" ]; then
        echo "Running $script..." >&2
        OUTPUT=$($script_path 2>&1)
        EXIT_CODE=$?

        if [ $EXIT_CODE -eq 0 ]; then
            echo "✓ $script passed" >&2
            PASSED=$((PASSED + 1))
            RESULTS+=("{\"name\": \"$script\", \"success\": true, \"output\": $OUTPUT}")
        else
            echo "✗ $script failed" >&2
            FAILED=$((FAILED + 1))
            RESULTS+=("{\"name\": \"$script\", \"success\": false, \"output\": $OUTPUT}")
        fi
    else
        echo "⚠ $script not found or not executable" >&2
        FAILED=$((FAILED + 1))
        RESULTS+=("{\"name\": \"$script\", \"success\": false, \"output\": {\"error\": \"Script not found or not executable\"}}")
    fi
done

# Create JSON output
RESULTS_JSON=$(printf '%s,' "${RESULTS[@]}" | sed 's/,$//')
OUTPUT="{
  \"success\": $([ $FAILED -eq 0 ] && echo true || echo false),
  \"message\": \"Test suite completed: $PASSED passed, $FAILED failed\",
  \"summary\": {
    \"total\": $TOTAL_TESTS,
    \"passed\": $PASSED,
    \"failed\": $FAILED,
    \"success_rate\": $((PASSED * 100 / TOTAL_TESTS))
  },
  \"results\": [$RESULTS_JSON]
}"

echo "$OUTPUT"

# Exit with failure if any test failed
[ $FAILED -eq 0 ]