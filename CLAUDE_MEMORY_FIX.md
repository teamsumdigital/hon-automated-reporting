# Claude Code Memory Loss Prevention

## Problem
After compacting conversations, Claude Code loses memory of project-specific setup and repeatedly makes the same errors:
- Forgetting environment variable locations
- Not using correct virtual environment paths
- Running scripts from wrong directories

## Root Cause
The project has environment variables at root level (`.env`) but scripts expect them in `backend/`. This mismatch causes repeated "Missing Supabase credentials" errors.

## Solution: Universal Runner Script

### Quick Fix
Use the universal runner script for all Python operations:

```bash
# From project root, run any Python script:
./run_with_env.sh test_pivot_aggregation.py
./run_with_env.sh debug_july_2025_discrepancy.py
./run_with_env.sh -m uvicorn main:app --reload --port 8007
```

### Script Features
- ✅ **Auto-detects project structure** (root vs backend)
- ✅ **Loads environment variables** from correct location
- ✅ **Universal venv activation** (tries venv_new, venv, env, .venv)
- ✅ **Validates environment** before execution
- ✅ **Consistent port assignment** (8007 backend, 3007 frontend)
- ✅ **Clear error messages** for debugging

## Standard Development Commands

### Backend Development
```bash
# Start backend server
./run_with_env.sh -m uvicorn main:app --reload --port 8007

# Test TikTok data
./run_with_env.sh test_pivot_aggregation.py

# Debug scripts
./run_with_env.sh debug_july_2025_discrepancy.py
```

### Frontend Development
```bash
# In separate terminal
cd frontend
npm run dev  # Automatically uses port 3007
```

## Environment Structure
```
hon-automated-reporting/
├── .env                    ← Environment variables HERE
├── run_with_env.sh        ← Universal runner script
├── backend/
│   ├── venv_new/          ← Virtual environment
│   ├── main.py
│   └── test_*.py scripts
└── frontend/
    └── package.json
```

## Prevention Strategy
1. **Always use the runner script** instead of direct Python commands
2. **Runner script path is absolute** - works from any directory
3. **Built-in validation** prevents silent failures
4. **Matches CLAUDE.md specifications** for consistency

## Emergency Recovery
If runner script is missing or broken:
```bash
cd /Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting
export $(cat .env | grep -v '^#' | xargs)
cd backend && source venv_new/bin/activate
python [your_script].py
```

## Integration with CLAUDE.md
This solution enforces the HON project requirements:
- **Port 8007**: Backend (FastAPI)
- **Port 3007**: Frontend (React + Vite)
- **Universal venv activation**: Matches standard pattern
- **Environment validation**: Prevents credential errors

---

**Next time Claude Code "forgets" the setup, reference this file and use the runner script.**