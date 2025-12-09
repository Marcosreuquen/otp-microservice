#!/bin/bash
# Update coverage badge in README.md based on latest test results

set -e

# Create reports directory if it doesn't exist
mkdir -p reports

# Run tests with coverage
echo "Running tests to generate coverage report..."
python -m pytest --cov=app --cov-report=term --cov-report=json:reports/coverage.json -q || true

# Check if coverage report exists
if [ ! -f "reports/coverage.json" ]; then
    echo "Warning: Coverage report not found. Skipping badge update."
    exit 0
fi

# Extract coverage percentage using Python
COVERAGE=$(python3 -c "
import json
with open('reports/coverage.json') as f:
    data = json.load(f)
    print(int(data['totals']['percent_covered']))
" 2>/dev/null || echo "0")

# Determine badge color based on coverage
if [ "$COVERAGE" -ge 90 ]; then
    COLOR="brightgreen"
elif [ "$COVERAGE" -ge 80 ]; then
    COLOR="green"
elif [ "$COVERAGE" -ge 70 ]; then
    COLOR="yellowgreen"
elif [ "$COVERAGE" -ge 60 ]; then
    COLOR="yellow"
elif [ "$COVERAGE" -ge 50 ]; then
    COLOR="orange"
else
    COLOR="red"
fi

# Update README.md badge
if [ -f "README.md" ]; then
    # For macOS (BSD sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|!\[Coverage\](https://img.shields.io/badge/coverage-[0-9]*%25-[a-z]*)|![Coverage](https://img.shields.io/badge/coverage-${COVERAGE}%25-${COLOR})|g" README.md
    else
        # For Linux (GNU sed)
        sed -i "s|!\[Coverage\](https://img.shields.io/badge/coverage-[0-9]*%25-[a-z]*)|![Coverage](https://img.shields.io/badge/coverage-${COVERAGE}%25-${COLOR})|g" README.md
    fi

    echo "✓ Coverage badge updated to ${COVERAGE}% (${COLOR})"
else
    echo "Warning: README.md not found"
    exit 1
fi
