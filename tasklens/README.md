# TaskLens - AI Hardware Assembly Guide

**AI-powered hardware assembly guidance using NVIDIA Nemotron models.**

TaskLens is a Progressive Web App that provides real-time, step-by-step wiring instructions for hardware assembly using computer vision and AI planning.

## 🚀 Live Demo

- **Frontend**: https://tasklensutd.netlify.app/
- **Backend**: https://tasklens-production.up.railway.app/

## ✨ Features

- 📷 **Real-time Camera Integration** - Point your camera at hardware components
- 🤖 **NVIDIA Nemotron AI** - Dual-stage AI pipeline for visual identification and intelligent planning
- 📱 **Progressive Web App** - Install on mobile devices for native-like experience
- ⚡ **Safety-First Design** - Highlights safe vs unsafe pin connections
- 🎯 **Step-by-Step Guidance** - 5-step wiring plans with visual overlays

## 🏗️ Architecture

### Two-Stage AI Pipeline

1. **Visual Identification** - NVIDIA Nemotron Nano 2 VL identifies hardware components
2. **Intelligent Planning** - NVIDIA Nemotron Nano 3 generates safe, chronological wiring instructions

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- TailwindCSS + shadcn/ui
- PWA with Service Workers

**Backend:**
- FastAPI (Python)
- NVIDIA NIM APIs
- Pydantic for validation
- HTTPX for async requests

## 🛠️ Local Development

### Prerequisites

- Python 3.8+
- Node.js 24+
- NVIDIA API Key

### Backend Setup

```bash
cd tasklens/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Add your NVIDIA API key to .env
# NVIDIA_API_KEY=your_key_here

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd tasklens/frontend
npm install
npm run dev
```

Visit http://localhost:8080

## 📦 Deployment

### Backend (Render.com)

1. Push to GitHub
2. Connect Render to your repo
3. Set root directory: `tasklens/backend`
4. Add environment variable: `NVIDIA_API_KEY`
5. Deploy!

### Frontend (Netlify)

```bash
cd tasklens/frontend
npm run build
netlify deploy --prod
```

## 🎮 Usage

1. Open the app on your phone or computer
2. Allow camera permissions
3. Enter your goal (e.g., "Blink an LED")
4. Point camera at your hardware
5. Tap "Scan & Analyze"
6. Follow the step-by-step wiring plan!

## 🔐 Environment Variables

**Backend (.env):**
```
NVIDIA_API_KEY=your_nvidia_api_key
```

**Frontend (.env.production):**
```
VITE_API_BASE_URL=https://your-backend-url.com
```

## 📄 License

MIT

## 🙏 Acknowledgments

- Built with NVIDIA NIM APIs
- Powered by Nemotron models
- UI components from shadcn/ui
