#!/bin/bash

# HON Automated Reporting - Universal Script Runner
# Prevents Claude Code memory loss by handling environment setup correctly

set -e  # Exit on any error

PROJECT_ROOT="/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting"

echo "🏠 HON Automated Reporting - Universal Runner"
echo "================================================"

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in project root"
    echo "Expected location: $PROJECT_ROOT/.env"
    exit 1
fi

# Load environment variables
echo "📁 Loading environment from: $PROJECT_ROOT/.env"
export $(cat .env | grep -v '^#' | xargs)

# Activate virtual environment with universal fallback
echo "🐍 Activating Python virtual environment..."
cd backend

# Universal venv activation (matches CLAUDE.md)
if source venv_new/bin/activate 2>/dev/null; then
    echo "✅ Activated: venv_new"
elif source venv/bin/activate 2>/dev/null; then
    echo "✅ Activated: venv"
elif source env/bin/activate 2>/dev/null; then
    echo "✅ Activated: env"
elif source .venv/bin/activate 2>/dev/null; then
    echo "✅ Activated: .venv"
else
    echo "❌ Error: No virtual environment found"
    echo "Available options: venv_new/ venv/ env/ .venv/"
    ls -la | grep -E "(venv|env)"
    exit 1
fi

# Verify environment variables are loaded
echo "🔧 Verifying environment..."
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ SUPABASE_SERVICE_KEY not set"
    exit 1
fi

echo "✅ Environment verified"
echo "   SUPABASE_URL: ${SUPABASE_URL:0:30}..."
echo "   Backend Port: 8007"
echo "   Frontend Port: 3007"

# Execute the command passed as arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <python_script.py> [args...]"
    echo "Example: $0 test_pivot_aggregation.py"
    echo "Example: $0 main.py"
    exit 1
fi

echo "🚀 Executing: python $@"
python "$@"