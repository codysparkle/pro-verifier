#!/bin/bash
# Comprehensive linting script for ProVerifer

set -e

echo "🔍 Running comprehensive code quality checks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo ""
echo "📋 1. Running Black (code formatting)..."
black --check --diff src/ main.py || {
    echo "❌ Black formatting issues found. Run 'black src/ main.py' to fix."
    exit 1
}
echo "✅ Black formatting checks passed"

echo ""
echo "📋 2. Running isort (import sorting)..."
isort --check-only --diff src/ main.py || {
    echo "❌ Import sorting issues found. Run 'isort src/ main.py' to fix."
    exit 1
}
echo "✅ Import sorting checks passed"

echo ""
echo "📋 3. Running Flake8 (linting)..."
flake8 src/ main.py
echo "✅ Flake8 linting passed"

echo ""
echo "📋 4. Running MyPy (type checking)..."
mypy src/ main.py --ignore-missing-imports
echo "✅ MyPy type checking passed"

echo ""
echo "📋 5. Running Bandit (security checks)..."
bandit -r src/ main.py -f json -o reports/bandit-report.json || true
bandit -r src/ main.py
echo "✅ Bandit security checks completed"

echo ""
echo "📋 6. Running Codespell (spell checking)..."
codespell src/ main.py README.md || {
    echo "ℹ️  Spell checking completed with suggestions"
}
echo "✅ Spell checking completed"

echo ""
echo "🎉 All code quality checks completed successfully!"
echo "📊 Reports saved in ./reports/ directory"
