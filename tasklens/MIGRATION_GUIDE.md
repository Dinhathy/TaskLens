# Migration Guide - Old Structure to New Clean Architecture

## What Changed?

The project has been reorganized from a flat structure to a clean, modular architecture.

### Before (Old Structure)
```
HackUTD Project/
├── main.py
├── config.py
├── schemas.py
├── services.py
├── requirements.txt
├── .env
├── tasklens-frameflow/  # Frontend in subfolder
│   ├── src/
│   └── package.json
├── README.md
├── ARCHITECTURE.md
└── setup.sh
```

### After (New Structure)
```
tasklens/
├── backend/
│   ├── api/
│   │   └── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── schemas.py
│   ├── services/
│   │   └── nemotron.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
│   ├── README.md
│   └── ARCHITECTURE.md
├── scripts/
│   └── setup.sh
└── start-backend.sh
```

## Key Changes

### 1. Backend Reorganization

**File Moves:**
- `main.py` → `backend/api/main.py`
- `config.py` → `backend/core/config.py`
- `schemas.py` → `backend/core/schemas.py`
- `services.py` → `backend/services/nemotron.py`
- `requirements.txt` → `backend/requirements.txt`
- `.env` → `backend/.env`

**Import Changes:**
```python
# Old imports
from schemas import TaskRequest
from services import NemotronService
from config import get_settings

# New imports
from core.schemas import TaskRequest
from services.nemotron import NemotronService
from core.config import get_settings
```

### 2. Frontend Reorganization

**Directory Move:**
- `tasklens-frameflow/` → `frontend/`

**No code changes needed** - Frontend code remains the same, just moved to a cleaner location.

### 3. Documentation Consolidation

**Moves:**
- `README.md` → `docs/README.md` (detailed docs)
- `ARCHITECTURE.md` → `docs/ARCHITECTURE.md`
- `INTEGRATION_COMPLETE.md` → `docs/INTEGRATION.md`
- New `README.md` created at root level

### 4. Scripts Organization

**Moves:**
- `setup.sh` → `scripts/setup.sh`
- `setup.bat` → `scripts/setup.bat`
- `test_setup.py` → `scripts/test_setup.py`
- `sample_request.py` → `scripts/sample_request.py`

**New Files:**
- `start-backend.sh` (root level)
- `start-backend.bat` (root level)
- `start-frontend.sh` (root level)
- `start-frontend.bat` (root level)

## How to Use the New Structure

### Starting the Application

**Old Way:**
```bash
# Backend (from project root)
uvicorn main:app --reload

# Frontend (from tasklens-frameflow/)
cd tasklens-frameflow
npm run dev
```

**New Way:**
```bash
# Backend - Use startup script
./start-backend.sh  # or start-backend.bat on Windows

# Frontend - Use startup script
./start-frontend.sh  # or start-frontend.bat on Windows
```

Or manually:
```bash
# Backend
cd tasklens/backend/api
uvicorn main:app --reload

# Frontend
cd tasklens/frontend
npm run dev
```

### Environment Configuration

**Old Location:**
```
HackUTD Project/.env
```

**New Location:**
```
tasklens/backend/.env
```

**Action Required:**
```bash
# Copy your .env file
cp "c:\Users\dinht\Desktop\HackUTD Project\.env" tasklens/backend/.env
```

### Running Scripts

**Old Way:**
```bash
python test_setup.py
```

**New Way:**
```bash
cd tasklens/backend
python ../scripts/test_setup.py
```

Or:
```bash
cd tasklens/scripts
python test_setup.py
```

## Benefits of New Structure

### 1. **Separation of Concerns**
- Backend and frontend are clearly separated
- Each has its own dependencies and configuration
- Easier to deploy independently

### 2. **Modular Backend**
- API routes in `api/`
- Business logic in `services/`
- Models and config in `core/`
- Follows standard Python package structure

### 3. **Better Organization**
- Documentation centralized in `docs/`
- Utility scripts in `scripts/`
- Clear entry points with startup scripts

### 4. **Scalability**
- Easy to add new services
- Simple to add new API routes
- Clear where new files should go

### 5. **Professional Structure**
- Follows industry best practices
- Similar to production applications
- Easier for new developers to understand

## Troubleshooting

### "Module not found" errors

**Problem:**
```
ModuleNotFoundError: No module named 'schemas'
```

**Solution:**
Make sure you're running from the correct directory:
```bash
cd tasklens/backend/api
uvicorn main:app --reload
```

### Import errors

**Problem:**
```
ImportError: cannot import name 'TaskRequest' from 'schemas'
```

**Solution:**
Check that files use new import paths:
```python
from core.schemas import TaskRequest  # ✓ Correct
from schemas import TaskRequest        # ✗ Old way
```

### .env not found

**Problem:**
```
WARNING: .env file not found!
```

**Solution:**
```bash
cd tasklens/backend
cp .env.example .env
# Edit .env and add NVIDIA_API_KEY
```

### Frontend can't connect to backend

**Problem:**
API calls fail with "Connection refused"

**Solution:**
1. Ensure backend is running: `./start-backend.sh`
2. Check backend is on port 8000: http://localhost:8000/health
3. Verify CORS settings in `backend/core/config.py` include port 8080

## Migration Checklist

- [ ] Navigate to new `tasklens/` directory
- [ ] Copy `.env` file to `backend/` folder
- [ ] Install backend dependencies: `cd backend && pip install -r requirements.txt`
- [ ] Install frontend dependencies: `cd frontend && npm install`
- [ ] Test backend: `./start-backend.sh`
- [ ] Test frontend: `./start-frontend.sh`
- [ ] Verify health endpoint: http://localhost:8000/health
- [ ] Verify frontend loads: http://localhost:8080
- [ ] Test full scan flow

## Old Files

The old flat structure is still at:
```
c:\Users\dinht\Desktop\HackUTD Project\
```

You can safely delete the old files once you've verified the new structure works:
```bash
# Backup first (optional)
zip -r old-structure-backup.zip "c:\Users\dinht\Desktop\HackUTD Project\"

# Then clean up old files
rm -rf "c:\Users\dinht\Desktop\HackUTD Project\main.py"
rm -rf "c:\Users\dinht\Desktop\HackUTD Project\config.py"
# etc.
```

Or keep the old structure as a backup until you're comfortable with the new one.

## Quick Reference

### New Directory Map

| Old Path | New Path |
|----------|----------|
| `main.py` | `backend/api/main.py` |
| `config.py` | `backend/core/config.py` |
| `schemas.py` | `backend/core/schemas.py` |
| `services.py` | `backend/services/nemotron.py` |
| `tasklens-frameflow/` | `frontend/` |
| `README.md` | `docs/README.md` |
| `.env` | `backend/.env` |

### New Commands

| Task | Command |
|------|---------|
| Start backend | `./start-backend.sh` |
| Start frontend | `./start-frontend.sh` |
| Run from backend/api | `uvicorn main:app --reload` |
| Test setup | `cd backend && python ../scripts/test_setup.py` |

---

**Questions?** See [SETUP.md](SETUP.md) for detailed setup instructions.
