# TaskLens - AI Visual Task Assistant

Real-time, AI-powered visual guidance for hardware assembly, repairs, and hands-on tasks. Point your camera at components and get instant step-by-step instructions powered by GPT-4o Vision.

## Overview

TaskLens combines computer vision and AI to provide intelligent, real-time guidance for:
- **Hardware Assembly**: Electronics, Arduino/Raspberry Pi projects, PC building
- **Home Repairs**: Plumbing, electrical work, appliance fixes
- **Automotive Work**: Engine repairs, part replacement, diagnostics
- **Carpentry**: Woodworking, furniture assembly, DIY projects

## Live Deployment

- **Frontend**: https://tasklens.netlify.app
- **Backend API**: Deployed on Render
- **Status**: Production-ready

## Project Structure

```
tasklens/
├── backend/              # FastAPI Backend
│   ├── api/             # API routes and endpoints
│   │   └── main.py      # FastAPI application with CORS and middleware
│   ├── core/            # Core functionality
│   │   ├── config.py    # Environment configuration
│   │   └── schemas.py   # Pydantic models & JSON schemas
│   ├── services/        # Business logic
│   │   └── openai_service.py  # OpenAI GPT-4o orchestration
│   ├── requirements.txt # Python dependencies
│   ├── render.yaml      # Render deployment config
│   └── Procfile         # Process configuration
│
├── frontend/            # React PWA Frontend
│   ├── src/            # Source code
│   │   ├── pages/      # Page components (Index.tsx - main camera UI)
│   │   ├── components/ # Reusable UI components
│   │   └── hooks/      # Custom React hooks
│   ├── public/         # Static assets and PWA manifest
│   ├── dist/           # Production build output
│   └── package.json    # Node dependencies
│
└── test_setup.py       # Environment validation script
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

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

# Configure environment variables
# Create a .env file with:
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
VISION_MODEL=gpt-4o
TEXT_MODEL=gpt-4o-mini
DEBUG_MODE=True

# Run backend
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000

### 2. Frontend Setup

```bash
# Navigate to frontend
cd tasklens/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at: http://localhost:5173

### 3. Production Build

```bash
# Build frontend for production
cd tasklens/frontend
npm run build

# Frontend build output will be in dist/
# Deploy dist/ folder to Netlify or any static hosting
```

## Usage

1. **Open the app**: Navigate to https://tasklens.netlify.app or your local URL
2. **Grant camera access**: Allow camera permissions when prompted
3. **Enter your goal**: Type what you want to accomplish (e.g., "Wire an LED to Arduino", "Fix a leaky faucet")
4. **Capture the scene**: Point your camera at the hardware/components
5. **Click "Scan & Analyze"**: AI will identify components and generate a task plan
6. **Follow instructions**: Get 5 step-by-step instructions with safety guidance

## API Endpoints

### Root / Health Check
```http
GET https://your-backend.onrender.com/
```

Response:
```json
{
  "service": "TaskLens Aggregator Backend",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "plan_generation": "/api/v1/plan/generate",
    "health": "/health"
  }
}
```

### Generate Task Plan
```http
POST https://your-backend.onrender.com/api/v1/plan/generate
Content-Type: application/json

{
  "image_data": "base64_encoded_jpeg_string",
  "user_goal": "Your task description"
}
```

Response:
```json
[
  {
    "step_number": 1,
    "instruction": "Identify the Arduino Uno board...",
    "safe_pins": ["5V", "GND", "D13"],
    "unsafe_pins": ["VIN", "RESET"],
    "target_location": {"x": 150, "y": 200, "label": "Arduino"}
  },
  ...
]
```

## Technology Stack

### Backend
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **httpx** - Async HTTP client for API calls
- **OpenAI GPT-4o** - Vision model for component identification
- **OpenAI GPT-4o-mini** - Fast text model for task planning
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool and dev server
- **Shadcn/ui** - Beautiful component library
- **PWA** - Progressive Web App with offline support
- **MediaDevices API** - Camera access with 4K support

### Deployment
- **Render** - Backend hosting (Python web service)
- **Netlify** - Frontend hosting (static site)
- **GitHub** - Version control and CI/CD

## Features

### AI-Powered Analysis
- **Component Identification**: GPT-4o Vision identifies hardware components, tools, and parts
- **Multi-Domain Support**: Electronics, plumbing, automotive, carpentry, general repairs
- **Safety-First Approach**: Warns about unsafe connections and provides safety guidance

### Camera Capabilities
- **High Resolution**: Supports up to 4K (3840x2160) on compatible devices
- **Fallback Support**: Automatically uses Full HD (1920x1080) if 4K unavailable
- **Mobile Optimized**: Rear camera preference for mobile devices
- **Real-time Preview**: Live camera feed with capture functionality

### User Experience
- **Progressive Web App**: Installable on mobile devices
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Offline Support**: Service worker for offline functionality
- **Fast Response**: Optimized API calls with retry logic and timeout handling

## Environment Variables

### Backend (.env or Render Dashboard)
```env
OPENAI_API_KEY=sk-...                    # Required: OpenAI API key
OPENAI_BASE_URL=https://api.openai.com/v1  # Default OpenAI endpoint
VISION_MODEL=gpt-4o                      # Vision model for image analysis
TEXT_MODEL=gpt-4o-mini                   # Text model for planning
API_TIMEOUT=60                           # API request timeout (seconds)
MAX_RETRIES=3                            # Max retry attempts
DEBUG_MODE=False                         # Enable debug logging in production
```

### Frontend
No environment variables needed - API endpoint is configured in source code.

## Development

### Run Tests
```bash
# Validate environment setup
python test_setup.py

# Test API endpoint
cd tasklens/backend
python -c "from core.config import get_settings; print(get_settings().openai_api_key[:10])"
```

### Local Development Tips
1. Backend runs on port 8000, frontend on 5173
2. CORS is configured for localhost origins
3. Use DEBUG_MODE=True for detailed error messages
4. Check Render logs for backend debugging
5. Use browser DevTools Network tab for frontend debugging

## Troubleshooting

### Common Issues

**"Failed to fetch" errors**
- Check that backend is running and accessible
- Verify CORS configuration includes your frontend URL
- Check browser console for specific error messages

**"OPENAI_API_KEY not configured"**
- Ensure API key is set in Render dashboard or .env file
- Verify key has no trailing whitespace or newlines
- Check that key is valid at platform.openai.com

**Camera not working**
- Grant camera permissions in browser
- Use HTTPS or localhost (camera requires secure context)
- Check browser console for OverconstrainedError
- Try different devices if one fails

**High API costs**
- GPT-4o vision calls cost ~$0.01-0.03 per request
- Consider rate limiting in production
- Use caching for repeated requests
- Monitor usage at platform.openai.com/usage

## Architecture

### Request Flow
1. User captures image with camera → Base64 JPEG encoding
2. Frontend sends image + goal to backend API
3. Backend sanitizes and validates input
4. **Stage 1**: GPT-4o Vision identifies components and analyzes scene
5. **Stage 2**: GPT-4o-mini generates 5-step task plan with safety guidance
6. Backend returns structured JSON response
7. Frontend renders step-by-step instructions

### Security Features
- Rate limiting (30 requests/minute per IP)
- Request size limits (10MB max)
- Input validation and sanitization
- CORS whitelist for allowed origins
- No API keys exposed to frontend
- Request ID tracking for debugging

## License

MIT License - Built for HackUTD 2024

## Credits

Built by the TaskLens team for HackUTD Ripple Effect 2024.

**Technologies**: OpenAI GPT-4o, FastAPI, React, TypeScript, Tailwind CSS

---

**Note**: This is a hackathon project. For production use, consider additional security hardening, comprehensive error handling, and usage monitoring.
