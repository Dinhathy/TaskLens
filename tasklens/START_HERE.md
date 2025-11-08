# 🚀 START HERE - TaskLens Quick Start

## You're in the new clean structure!

All files have been reorganized. Follow these steps to get running:

## ⚡ Quick Start (3 Steps)

### Step 1: Copy Your Environment File

```bash
# From the old location, copy your .env file
cd "c:\Users\dinht\Desktop\HackUTD Project\tasklens"
cp "../.env" backend/.env
```

Or create a new one:
```bash
cd backend
cp .env.example .env
# Edit .env and add: NVIDIA_API_KEY=your_actual_key_here
```

### Step 2: Start Backend

**Windows:**
```bash
start-backend.bat
```

**Mac/Linux:**
```bash
./start-backend.sh
```

### Step 3: Start Frontend (New Terminal)

**Windows:**
```bash
start-frontend.bat
```

**Mac/Linux:**
```bash
./start-frontend.sh
```

## ✅ Verify It Works

1. **Backend:** http://localhost:8000/health
2. **Frontend:** http://localhost:8080
3. **API Docs:** http://localhost:8000/docs

## 📁 New Structure

```
tasklens/
├── backend/           # Python FastAPI
│   ├── api/          # main.py here
│   ├── core/         # config.py, schemas.py
│   └── services/     # nemotron.py
├── frontend/         # React app
├── docs/             # Documentation
└── scripts/          # Utilities
```

## 🔧 Manual Start (If Scripts Don't Work)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cd api
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## ❓ Common Issues

### "NVIDIA_API_KEY not configured"
```bash
cd backend
nano .env  # or notepad .env on Windows
# Add: NVIDIA_API_KEY=your_key_here
```

### "Module not found" errors
```bash
cd backend/api
uvicorn main:app --reload
```

### Port already in use
```bash
# Kill process on port 8000 or 8080
# Or change port in config
```

## 📚 Full Documentation

- [SETUP.md](SETUP.md) - Complete setup guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File locations
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migration help
- [DIRECTORY_TREE.txt](DIRECTORY_TREE.txt) - Visual tree

## 🎯 What Changed?

- ✅ Files organized into backend/frontend/docs/scripts
- ✅ Python files moved to backend with proper imports
- ✅ Frontend moved from tasklens-frameflow/ to frontend/
- ✅ Startup scripts created for easy launching
- ✅ All import paths updated

## 🆘 Need Help?

1. Check the error message in terminal
2. See [SETUP.md](SETUP.md) for detailed instructions
3. Verify .env file exists in backend/ directory
4. Make sure you're in the right directory

---

**Everything is ready! Just copy .env and run the startup scripts.** 🚀
