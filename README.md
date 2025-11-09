# TaskLens - AI Hardware Architect

Real-time, AI-powered hardware assembly guidance with visual overlays.

## Project Structure

```
tasklens/
├── backend/              # FastAPI Backend
│   ├── api/             # API routes and endpoints
│   │   └── main.py      # FastAPI application
│   ├── core/            # Core functionality
│   │   ├── config.py    # Configuration management
│   │   └── schemas.py   # Pydantic models & JSON schemas
│   ├── services/        # Business logic
│   │   └── nemotron.py  # NVIDIA Nemotron orchestration
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables (create this)
│
├── frontend/            # React Frontend
│   ├── src/            # Source code
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable UI components
│   │   └── hooks/      # Custom React hooks
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
│
├── docs/               # Documentation
│   ├── README.md       # Detailed documentation
│   ├── ARCHITECTURE.md # System architecture
│   └── INTEGRATION.md  # Integration guide
│
└── scripts/            # Utility scripts
    ├── setup.sh        # Unix/Mac setup script
    ├── setup.bat       # Windows setup script
    └── test_setup.py   # Environment validation
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- NVIDIA API key ([Get one here](https://build.nvidia.com/))

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

# Configure environment
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY

# Run backend
cd api
uvicorn main:app --reload
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

Frontend will run at: http://localhost:8080

## Usage

1. Open http://localhost:8080 in your browser
2. Click "Start Live Camera Feed"
3. Enter your goal (e.g., "Blink an LED")
4. Point camera at hardware
5. Click "Scan & Analyze Frame"
6. Follow step-by-step instructions with visual overlays

## API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Generate Wiring Plan
```
POST http://localhost:8000/api/v1/plan/generate
Content-Type: application/json

{
  "image_data": "base64_image_string",
  "user_goal": "Blink an LED"
}
```

## Technology Stack

**Backend:**
- FastAPI - Async Python web framework
- Pydantic - Data validation
- HTTPX - Async HTTP client
- NVIDIA Nemotron - AI models (Vila VLM + Nano 3 LLM)

**Frontend:**
- React 18 - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Vite - Build tool
- Shadcn/ui - Component library

## Documentation

- [Full Documentation](docs/README.md)
- [Architecture Details](docs/ARCHITECTURE.md)
- [Integration Guide](docs/INTEGRATION.md)

## License

MIT License - Built for HackUTD

## Support

For issues or questions, see the [troubleshooting guide](docs/README.md#troubleshooting).
