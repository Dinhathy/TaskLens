# TaskLens Setup Guide

Complete setup instructions for the TaskLens project.

## Directory Structure

```
tasklens/
├── backend/              # Python FastAPI backend
├── frontend/             # React TypeScript frontend
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── start-backend.sh      # Start backend (Unix/Mac)
├── start-backend.bat     # Start backend (Windows)
├── start-frontend.sh     # Start frontend (Unix/Mac)
└── start-frontend.bat    # Start frontend (Windows)
```

## Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **NVIDIA API Key** - [Get one](https://build.nvidia.com/)

## Initial Setup

### 1. Backend Setup

```bash
# Navigate to backend
cd tasklens/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your NVIDIA API key
# NVIDIA_API_KEY=your_actual_key_here
```

**Verify backend setup:**
```bash
cd api
python -c "from core.config import get_settings; print('Config OK')"
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd tasklens/frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

## Running the Application

### Option 1: Using Startup Scripts (Recommended)

**Windows:**
```bash
# Terminal 1 - Backend
start-backend.bat

# Terminal 2 - Frontend
start-frontend.bat
```

**Mac/Linux:**
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend
./start-frontend.sh
```

### Option 2: Manual Start

**Backend:**
```bash
cd tasklens/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd tasklens/frontend
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing the Setup

### 1. Test Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "nano2_vlm_url": "https://ai.api.nvidia.com/v1/vlm/...",
  "nano3_llm_url": "https://ai.api.nvidia.com/v1/chat/completions"
}
```

### 2. Test Frontend

1. Open http://localhost:8080
2. You should see the TaskLens welcome screen
3. Click "Start Live Camera Feed"
4. Grant camera permissions
5. Camera feed should appear

### 3. Test Full Flow

1. In camera view, enter goal: "Blink an LED"
2. Point camera at hardware (Raspberry Pi, Arduino, etc.)
3. Click "Scan & Analyze Frame"
4. Should see:
   - Loading spinner
   - Analysis screen with captured image
   - Visual overlay on hardware
   - Step-by-step instructions

## Common Issues

### Backend Issues

**Problem: "NVIDIA_API_KEY not configured"**
```bash
# Solution: Edit backend/.env
cd tasklens/backend
nano .env  # or notepad .env on Windows
# Add: NVIDIA_API_KEY=your_actual_key_here
```

**Problem: "Module not found" errors**
```bash
# Solution: Reinstall dependencies
cd tasklens/backend
source venv/bin/activate
pip install -r requirements.txt
```

**Problem: Import errors with "core" or "services"**
```bash
# Solution: Run from api directory
cd tasklens/backend/api
uvicorn main:app --reload
```

### Frontend Issues

**Problem: "Cannot find module '@/components/ui'"**
```bash
# Solution: Reinstall dependencies
cd tasklens/frontend
rm -rf node_modules
npm install
```

**Problem: Port 8080 already in use**
```bash
# Solution: Change port in vite.config.ts
# Or kill process using port 8080
```

**Problem: Camera permission denied**
- Check browser settings → Site permissions → Camera → Allow
- Try using HTTPS (use ngrok for local HTTPS)

### API Integration Issues

**Problem: CORS errors**
- Ensure backend is running on port 8000
- Check backend/core/config.py includes port 8080 in cors_origins

**Problem: "Failed to analyze hardware"**
- Check backend console for specific error
- Verify NVIDIA API key is valid
- Check network connectivity

## Development Tips

### Backend Development

```bash
# Run with auto-reload
cd tasklens/backend/api
uvicorn main:app --reload

# Run with debug logging
DEBUG=true uvicorn main:app --reload

# Test specific endpoint
curl -X POST http://localhost:8000/api/v1/plan/generate \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64...", "user_goal": "test"}'
```

### Frontend Development

```bash
# Run dev server
cd tasklens/frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure Reference

### Backend Files

```
backend/
├── api/
│   ├── __init__.py
│   └── main.py          # FastAPI app & endpoints
├── core/
│   ├── __init__.py
│   ├── config.py        # Settings & configuration
│   └── schemas.py       # Pydantic models
├── services/
│   ├── __init__.py
│   └── nemotron.py      # AI orchestration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── .env.example         # Environment template
```

### Frontend Files

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Index.tsx    # Main application page
│   │   └── NotFound.tsx
│   ├── components/
│   │   └── ui/          # Shadcn components
│   ├── hooks/
│   │   └── use-toast.ts
│   └── App.tsx          # Root component
├── public/              # Static assets
├── package.json         # Node dependencies
├── vite.config.ts       # Vite configuration
└── tailwind.config.ts   # Tailwind configuration
```

## Next Steps

1. ✅ Complete setup following this guide
2. ✅ Test backend health endpoint
3. ✅ Test frontend loads correctly
4. ✅ Test camera access
5. ✅ Test full scan flow with hardware

## Additional Resources

- [Full Documentation](docs/README.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](http://localhost:8000/docs) (when running)
- [Troubleshooting Guide](docs/README.md#troubleshooting)

## Support

For issues or questions:
1. Check this setup guide
2. Review [docs/README.md](docs/README.md)
3. Check backend logs in console
4. Test endpoints at http://localhost:8000/docs

---

**Happy Building! 🚀**
