#!/bin/bash
# Install git hooks

set -e

# Get the root directory of the git repository
ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT_DIR"

echo "Installing git hooks..."

# Configure git to use custom hooks directory
git config core.hooksPath .githooks

echo "✓ Git hooks installed successfully!"
echo ""
echo "The following hooks are now active:"
echo "  - pre-commit: Updates coverage badge when Python files change"
echo ""
echo "To disable hooks temporarily, use: git commit --no-verify"
