#!/bin/bash
# Auto-formatting script for ProVerifer

set -e

echo "🎨 Auto-formatting code..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo ""
echo "📋 1. Running Black (code formatting)..."
black src/ main.py
echo "✅ Black formatting applied"

echo ""
echo "📋 2. Running isort (import sorting)..."
isort src/ main.py
echo "✅ Import sorting applied"

echo ""
echo "🎉 Code formatting completed!"
echo "💡 Run './scripts/lint.sh' to check code quality"
