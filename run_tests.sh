#!/bin/sh

# Run all test cases
for test_file in tests/test_*.py; do
    echo "Running test case: $test_file"
    python -m unittest "$test_file"
    echo ""
done