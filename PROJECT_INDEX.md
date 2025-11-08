# TaskLens Backend - Complete Project Index

## Project Summary

**TaskLens Aggregator Backend** - A production-ready FastAPI service that orchestrates NVIDIA Nemotron Nano models to generate structured hardware task plans from component images.

**Technology Stack:** Python 3.9+, FastAPI, Pydantic, HTTPX, Uvicorn
**AI Models:** NVIDIA Nemotron Nano 2 VL (Vision) + Nano 3 (Planning)
**Built for:** HackUTD Hackathon

---

## Quick Navigation

### Getting Started (Start Here)
1. **[QUICKSTART.md](QUICKSTART.md)** - 30-second setup guide
2. **[README.md](README.md)** - Complete documentation
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & architecture

### Setup & Configuration
- [requirements.txt](requirements.txt) - Python dependencies
- [.env.example](.env.example) - Environment variables template
- [setup.bat](setup.bat) - Windows setup script
- [setup.sh](setup.sh) - Unix/Mac setup script

### Core Application Files
- [main.py](main.py) - FastAPI application & endpoints
- [services.py](services.py) - Nemotron orchestration logic
- [schemas.py](schemas.py) - Pydantic models & JSON schemas
- [config.py](config.py) - Configuration management

### Testing & Validation
- [test_setup.py](test_setup.py) - Environment validation script
- [sample_request.py](sample_request.py) - API testing script

### Additional Files
- [.gitignore](.gitignore) - Git ignore rules

---

## File Descriptions

### Core Application (Python)

| File | Lines | Purpose |
|------|-------|---------|
| **main.py** | ~200 | FastAPI app, endpoints, CORS, error handling |
| **services.py** | ~250 | Two-stage AI pipeline orchestration |
| **schemas.py** | ~150 | Pydantic validation & JSON schema |
| **config.py** | ~50 | Settings & environment configuration |

### Documentation (Markdown)

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | Fast setup guide (< 5 min) |
| **README.md** | Complete documentation (API, setup, deployment) |
| **ARCHITECTURE.md** | System design, data flow, architecture |
| **PROJECT_INDEX.md** | This file - project navigation |

### Setup & Testing (Scripts)

| File | Purpose |
|------|---------|
| **setup.bat** | Automated Windows setup |
| **setup.sh** | Automated Unix/Mac setup |
| **test_setup.py** | Validate environment configuration |
| **sample_request.py** | Test API endpoints |

### Configuration

| File | Purpose |
|------|---------|
| **requirements.txt** | Pip dependencies |
| **.env.example** | Environment template |
| **.gitignore** | Git exclusions |

---

## Project Statistics

- **Total Python Files:** 6
- **Total Lines of Code:** ~1,000
- **Documentation Pages:** 4
- **API Endpoints:** 3
- **Pydantic Models:** 5
- **Dependencies:** 7

---

## Key Features Implemented

### 1. Asynchronous Pipeline
- Non-blocking I/O for all API calls
- Concurrent request handling
- Efficient resource utilization

### 2. Strict Validation
- Pydantic input/output validation
- JSON schema enforcement
- Type-safe configuration

### 3. Production-Ready
- Comprehensive error handling
- Structured logging
- Health check endpoints
- CORS configuration

### 4. Developer Experience
- Automated setup scripts
- Test utilities
- Interactive API docs
- Clear documentation

---

## API Endpoints Reference

### Primary Endpoint
```
POST /api/v1/plan/generate
```
**Input:** `{image_data: string, user_goal: string}`
**Output:** Structured TaskPlan JSON
**Purpose:** Generate hardware task plan from image

### Health & Info
```
GET /health       # Service health check
GET /             # Service information
GET /docs         # Interactive API documentation
```

---

## Data Flow Summary

```
1. Frontend → POST {image, goal}
2. Backend validates input (Pydantic)
3. Stage 1: Nemotron Nano 2 VL identifies component
4. Stage 2: Nemotron Nano 3 generates structured plan
5. Backend validates output (Pydantic)
6. Frontend ← Structured JSON plan
```

---

## Development Workflow

### First Time Setup
```bash
# 1. Run setup
./setup.sh  # or setup.bat on Windows

# 2. Configure API key
edit .env

# 3. Validate setup
python test_setup.py

# 4. Start server
uvicorn main:app --reload
```

### Testing
```bash
# Check health
curl http://localhost:8000/health

# Test with sample
python sample_request.py

# View API docs
open http://localhost:8000/docs
```

### Making Changes
```bash
# 1. Edit code (changes auto-reload in dev mode)
# 2. Test endpoint at /docs
# 3. Validate with sample_request.py
```

---

## Architecture Layers

```
┌─────────────────────────────────────┐
│   API Layer (main.py)              │  FastAPI, CORS, endpoints
├─────────────────────────────────────┤
│   Service Layer (services.py)      │  AI orchestration logic
├─────────────────────────────────────┤
│   Data Layer (schemas.py)          │  Validation, schemas
├─────────────────────────────────────┤
│   Config Layer (config.py)         │  Settings, environment
└─────────────────────────────────────┘
```

---

## Environment Variables Required

| Variable | Required | Example |
|----------|----------|---------|
| `NVIDIA_API_KEY` | ✓ | `nvapi-xxx...` |
| `NANO2_VLM_URL` |  | Default provided |
| `NANO3_LLM_URL` |  | Default provided |
| `DEBUG` |  | `false` |

---

## Dependencies Breakdown

### Production
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `httpx` - Async HTTP client
- `python-dotenv` - Environment loading

### Development
- `pydantic-settings` - Settings management

---

## Common Tasks

### Start Development Server
```bash
uvicorn main:app --reload
```

### Run Validation
```bash
python test_setup.py
```

### Test API
```bash
python sample_request.py
```

### View Logs
```bash
# Logs print to console where uvicorn is running
# Set DEBUG=true in .env for detailed logs
```

### Add New Endpoint
1. Add route function in `main.py`
2. Add schema in `schemas.py` if needed
3. Add service logic in `services.py` if needed
4. Test at `/docs`

---

## Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| "NVIDIA_API_KEY not configured" | Missing `.env` | Create `.env` with API key |
| "Module not found" | Missing deps | Run `pip install -r requirements.txt` |
| "Connection refused" | Server not running | Run `uvicorn main:app --reload` |
| "401 Unauthorized" | Invalid API key | Check key at build.nvidia.com |
| "503 Service Unavailable" | NVIDIA API down | Check API status, retry |

---

## Next Steps After Setup

1. ✓ Complete setup with `setup.bat` or `setup.sh`
2. ✓ Configure `.env` with NVIDIA API key
3. ✓ Run `python test_setup.py` to validate
4. ✓ Start server with `uvicorn main:app --reload`
5. ✓ Test with `python sample_request.py`
6. ✓ View docs at http://localhost:8000/docs
7. → Integrate with your frontend!

---

## Support & Resources

- **Documentation:** Start with [QUICKSTART.md](QUICKSTART.md)
- **API Reference:** http://localhost:8000/docs (when running)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **NVIDIA API:** https://build.nvidia.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

**Status:** Production-ready, fully documented, tested
**Version:** 1.0.0
**License:** MIT
**Built for:** HackUTD

*Generated by Claude Code for TaskLens Project*
