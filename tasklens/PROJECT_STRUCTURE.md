# TaskLens Project Structure

Complete directory structure and file reference for the TaskLens project.

## Directory Tree

```
tasklens/
│
├── 📁 backend/                      # Python FastAPI Backend
│   ├── 📁 api/                      # API Layer
│   │   ├── __init__.py             # Package initializer
│   │   └── main.py                 # FastAPI app, routes, middleware
│   │
│   ├── 📁 core/                     # Core Functionality
│   │   ├── __init__.py             # Package initializer
│   │   ├── config.py               # Settings & configuration
│   │   └── schemas.py              # Pydantic models & JSON schemas
│   │
│   ├── 📁 services/                 # Business Logic
│   │   ├── __init__.py             # Package initializer
│   │   └── nemotron.py             # NVIDIA Nemotron orchestration
│   │
│   ├── __init__.py                 # Backend package init
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (YOU CREATE THIS)
│   └── .env.example                # Environment template
│
├── 📁 frontend/                     # React TypeScript Frontend
│   ├── 📁 src/                      # Source Code
│   │   ├── 📁 pages/               # Page Components
│   │   │   ├── Index.tsx           # Main app (camera, scan, analysis)
│   │   │   └── NotFound.tsx        # 404 page
│   │   │
│   │   ├── 📁 components/          # Reusable Components
│   │   │   ├── NavLink.tsx         # Navigation link wrapper
│   │   │   └── 📁 ui/              # Shadcn UI components (50+ files)
│   │   │
│   │   ├── 📁 hooks/               # Custom React Hooks
│   │   │   ├── use-toast.ts        # Toast notifications
│   │   │   └── use-mobile.tsx      # Mobile detection
│   │   │
│   │   ├── 📁 lib/                 # Utilities
│   │   │   └── utils.ts            # Helper functions
│   │   │
│   │   ├── App.tsx                 # Root component
│   │   ├── main.tsx                # Entry point
│   │   ├── index.css               # Global styles
│   │   └── App.css                 # App-specific styles
│   │
│   ├── 📁 public/                   # Static Assets
│   │   ├── lovable-uploads/        # Uploaded images
│   │   └── (other static files)
│   │
│   ├── index.html                  # HTML entry point
│   ├── package.json                # Node dependencies
│   ├── package-lock.json           # Lock file
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.ts          # Tailwind CSS config
│   ├── tsconfig.json               # TypeScript config
│   ├── tsconfig.app.json           # App TypeScript config
│   ├── tsconfig.node.json          # Node TypeScript config
│   ├── postcss.config.js           # PostCSS config
│   ├── components.json             # Shadcn components config
│   ├── eslint.config.js            # ESLint config
│   └── README.md                   # Frontend documentation
│
├── 📁 docs/                         # Documentation
│   ├── README.md                   # Complete project documentation
│   ├── ARCHITECTURE.md             # System architecture details
│   └── INTEGRATION.md              # Integration guide
│
├── 📁 scripts/                      # Utility Scripts
│   ├── setup.sh                    # Unix/Mac setup script
│   ├── setup.bat                   # Windows setup script
│   ├── test_setup.py               # Environment validation
│   └── sample_request.py           # API testing script
│
├── 📄 README.md                     # Main project README
├── 📄 SETUP.md                      # Setup instructions
├── 📄 MIGRATION_GUIDE.md            # Migration from old structure
├── 📄 PROJECT_STRUCTURE.md          # This file
│
├── 🚀 start-backend.sh              # Start backend (Unix/Mac)
├── 🚀 start-backend.bat             # Start backend (Windows)
├── 🚀 start-frontend.sh             # Start frontend (Unix/Mac)
├── 🚀 start-frontend.bat            # Start frontend (Windows)
│
└── 📄 .gitignore                    # Git ignore rules
```

## File Descriptions

### Backend Files

#### `backend/api/main.py` (194 lines)
**Purpose:** FastAPI application entry point
- Defines all API routes
- Configures CORS middleware
- Implements error handling
- Endpoints:
  - `GET /` - Service info
  - `GET /health` - Health check
  - `POST /api/v1/plan/generate` - Generate wiring plan

**Key Imports:**
```python
from core.schemas import TaskRequest, TaskPlan, WiringStep
from services.nemotron import NemotronService
from core.config import get_settings
```

#### `backend/core/config.py` (45 lines)
**Purpose:** Configuration management
- Loads environment variables
- Defines Settings class with Pydantic
- Manages CORS origins, API endpoints, timeouts

**Key Settings:**
- `nvidia_api_key`: NVIDIA API key
- `nano2_vlm_url`: Vision model endpoint
- `nano3_llm_url`: Language model endpoint
- `cors_origins`: Allowed frontend origins

#### `backend/core/schemas.py` (148 lines)
**Purpose:** Data validation and schemas
- Pydantic models for request/response
- JSON schemas for AI model structured output

**Key Models:**
- `TaskRequest`: Input (image_data, user_goal)
- `WiringStep`: Individual step with pin guidance
- `TaskPlan`: Complete plan with steps and errors
- `WIRING_PLAN_SCHEMA`: JSON schema for Nemotron
- `PLAN_SCHEMA`: Alternative planning schema

#### `backend/services/nemotron.py` (287 lines)
**Purpose:** AI orchestration logic
- Manages calls to NVIDIA Nemotron models
- Implements two-stage pipeline

**Key Methods:**
- `identify_component()`: Vision analysis (Stage 1)
- `generate_wiring_plan()`: Plan generation (Stage 2)
- `orchestrate_full_pipeline()`: Coordinates both stages

### Frontend Files

#### `frontend/src/pages/Index.tsx` (450+ lines)
**Purpose:** Main application component
- Three-screen state machine (setup → capture → analysis)
- Camera access and frame capture
- API integration
- Visual overlay rendering
- Step navigation

**Key Features:**
- Live camera feed
- Voice input (Web Speech API)
- Base64 image capture
- API calls to backend
- Dynamic step display
- Canvas overlay for pin locations

#### `frontend/src/App.tsx` (28 lines)
**Purpose:** Root application component
- React Router setup
- QueryClient configuration
- Toast provider
- Tooltip provider

#### `frontend/vite.config.ts`
**Purpose:** Vite build configuration
- Dev server on port 8080
- Path aliases (`@` → `./src`)
- React plugin
- Component tagger

#### `frontend/tailwind.config.ts`
**Purpose:** Tailwind CSS configuration
- Custom colors (tech-cyan, tech-dark)
- Custom animations (pulse-glow, fade-in)
- Theme configuration

### Documentation Files

#### `docs/README.md`
Complete project documentation with:
- Setup instructions
- API reference
- Troubleshooting guide
- Usage examples

#### `docs/ARCHITECTURE.md`
System architecture details:
- Data flow diagrams
- Component interaction
- Design patterns
- Scalability considerations

#### `docs/INTEGRATION.md`
Integration guide:
- Frontend-backend connection
- API endpoint details
- Error handling
- Testing procedures

### Script Files

#### `scripts/test_setup.py`
Validates environment setup:
- Python version check
- Dependency verification
- .env file validation
- Module import tests

#### `scripts/sample_request.py`
API testing script:
- Example API calls
- Base64 image encoding
- Response parsing
- Error handling demo

## Import Path Guide

### Backend Imports

All backend code should use **absolute imports** from the package root:

```python
# In backend/api/main.py
from core.schemas import TaskRequest, WiringStep
from core.config import get_settings
from services.nemotron import NemotronService

# In backend/services/nemotron.py
from core.schemas import WIRING_PLAN_SCHEMA
from core.config import get_settings
```

### Frontend Imports

Frontend uses TypeScript path aliases:

```typescript
// @ maps to ./src
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
```

## Running From Different Locations

### From Project Root (`tasklens/`)
```bash
# Backend
./start-backend.sh

# Frontend
./start-frontend.sh
```

### From Backend Directory
```bash
cd backend/api
uvicorn main:app --reload
```

### From Frontend Directory
```bash
cd frontend
npm run dev
```

## File Size Reference

| Category | Files | Total Size |
|----------|-------|------------|
| Backend Python | 4 | ~1,000 lines |
| Frontend TypeScript | 300+ | ~10,000+ lines |
| Documentation | 7 | ~4,000 lines |
| Configuration | 10+ | ~500 lines |

## Dependencies

### Backend (Python)
```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.24.0
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

### Frontend (Node.js)
```
react@18.3.1
react-router-dom@6.30.1
@tanstack/react-query@5.83.0
tailwindcss@3.4.17
vite@5.x.x
typescript@5.6.2
```

## Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend Dev | 8080 | http://localhost:8080 |
| API Docs | 8000 | http://localhost:8000/docs |

## Environment Variables

Required in `backend/.env`:

```bash
NVIDIA_API_KEY=your_key_here          # Required
NANO2_VLM_URL=...                     # Optional (has default)
NANO3_LLM_URL=...                     # Optional (has default)
API_TIMEOUT=60                        # Optional (default: 60)
DEBUG=false                           # Optional (default: false)
```

## Quick Reference

### Start Everything
```bash
# Terminal 1
./start-backend.sh

# Terminal 2
./start-frontend.sh
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:8080
```

### Common Tasks

```bash
# Install backend dependencies
cd backend && pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Run backend tests
cd backend && pytest

# Build frontend
cd frontend && npm run build

# Lint frontend
cd frontend && npm run lint
```

---

For detailed setup instructions, see [SETUP.md](SETUP.md).
