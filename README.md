# TaskLens Aggregator Backend

High-performance FastAPI backend that orchestrates NVIDIA Nemotron models to generate structured hardware task plans from component images.

## Architecture

This backend implements a **two-stage AI pipeline**:

1. **Stage 1: Visual Identification** (Nemotron Nano 2 VL)
   - Analyzes base64-encoded hardware images
   - Identifies component model and current state
   - Returns structured component information

2. **Stage 2: Chronological Planning** (Nemotron Nano 3)
   - Takes identified component + user goal
   - Generates safe, chronologically-ordered task plan
   - Enforces structured JSON output via schema validation
   - Includes error states and recovery procedures

## Features

- Fully asynchronous API using FastAPI
- Strict Pydantic schema validation
- Comprehensive error handling and logging
- CORS-enabled for frontend integration
- Environment-based configuration
- Production-ready with health checks

## Prerequisites

- Python 3.9 or higher
- NVIDIA API key ([Get one here](https://build.nvidia.com/))
- Virtual environment (recommended)

## Setup Instructions

### 1. Clone and Navigate

```bash
cd "c:\Users\dinht\Desktop\HackUTD Project"
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` and add your NVIDIA API key:

```env
NVIDIA_API_KEY=nvapi-your_actual_key_here
```

### 5. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

## API Documentation

Once running, access:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "nano2_vlm_url": "https://ai.api.nvidia.com/v1/vlm/nvidia/nemotron-nano-2-vlm",
  "nano3_llm_url": "https://ai.api.nvidia.com/v1/chat/completions"
}
```

### Generate Task Plan

```bash
POST /api/v1/plan/generate
Content-Type: application/json
```

Request Body:
```json
{
  "image_data": "base64_encoded_image_string_here...",
  "user_goal": "Blink an LED"
}
```

Response (200 OK):
```json
{
  "identified_component": "Raspberry Pi 4 Model B",
  "component_state": "Unpowered",
  "goal": "Blink an LED",
  "plan_steps": [
    {
      "step_number": 1,
      "action": "Connect the Raspberry Pi to power supply",
      "component": "Raspberry Pi 4 Model B",
      "safety_level": "safe",
      "estimated_time_seconds": 30
    },
    {
      "step_number": 2,
      "action": "Insert GPIO jumper wire to pin 18",
      "component": "GPIO pins",
      "safety_level": "caution",
      "estimated_time_seconds": 45
    }
  ],
  "common_errors": [
    {
      "error_name": "LED not blinking",
      "symptoms": ["LED remains off", "No visible light output"],
      "recovery_steps": [
        "Check GPIO pin connection",
        "Verify LED polarity (anode to GPIO, cathode to ground)",
        "Test LED with multimeter"
      ]
    }
  ],
  "total_estimated_time_seconds": 300
}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Generate plan (replace with actual base64 image)
curl -X POST http://localhost:8000/api/v1/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "iVBORw0KGgoAAAANSUhEUgA...",
    "user_goal": "Blink an LED"
  }'
```

### Using Python

```python
import requests
import base64

# Read and encode image
with open("raspberry_pi.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

# Make request
response = requests.post(
    "http://localhost:8000/api/v1/plan/generate",
    json={
        "image_data": image_base64,
        "user_goal": "Blink an LED"
    }
)

plan = response.json()
print(f"Generated {len(plan['plan_steps'])} steps")
```

## Project Structure

```
HackUTD Project/
├── main.py              # FastAPI application entry point
├── schemas.py           # Pydantic models and JSON schema
├── services.py          # Nemotron orchestration logic
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your actual config (create this)
└── README.md           # This file
```

## Configuration Options

All configuration via environment variables in `.env`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NVIDIA_API_KEY` | Yes | - | Your NVIDIA API key |
| `NANO2_VLM_URL` | No | NVIDIA endpoint | Nemotron Nano 2 VL endpoint |
| `NANO3_LLM_URL` | No | NVIDIA endpoint | Nemotron Nano 3 endpoint |
| `API_TIMEOUT` | No | 60 | Request timeout in seconds |
| `MAX_RETRIES` | No | 3 | Max retry attempts |
| `DEBUG` | No | false | Enable debug mode |

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid input)
- `500` - Internal server error
- `503` - Service unavailable (NVIDIA API error)
- `504` - Gateway timeout

Error response format:
```json
{
  "detail": "Error description here"
}
```

## Development

### Run with auto-reload

```bash
uvicorn main:app --reload
```

### Run tests

```bash
pytest tests/  # Add tests in tests/ directory
```

### Enable debug logging

Set `DEBUG=true` in `.env` for detailed error messages.

## Integration with Frontend

The backend is configured with CORS to accept requests from:

- `http://localhost:3000` (React/Vite default)
- `http://localhost:5173` (Vite alternate)

To add more origins, edit `config.py`:

```python
cors_origins: list = [
    "http://localhost:3000",
    "https://your-frontend-domain.com"
]
```

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### "NVIDIA_API_KEY not configured"
- Ensure `.env` file exists and contains valid API key
- Restart the server after updating `.env`

### "Invalid base64 image data"
- Verify image is properly base64 encoded
- Check image size (very large images may timeout)

### "NVIDIA API error: 401"
- API key is invalid or expired
- Get a new key from https://build.nvidia.com/

### "Request timeout"
- Increase `API_TIMEOUT` in `.env`
- Check network connectivity to NVIDIA endpoints

## License

MIT License - Built for HackUTD

## Support

For issues or questions:
1. Check the API docs at `/docs`
2. Review logs in console output
3. Verify `.env` configuration
4. Test with `/health` endpoint

---

Built with FastAPI, powered by NVIDIA Nemotron
