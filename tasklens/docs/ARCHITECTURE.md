# TaskLens Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Lovable)                       │
│                  React/TypeScript + Tailwind CSS                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP POST
                            │ {image_data, user_goal}
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TaskLens FastAPI Backend                       │
│                     (This Implementation)                        │
├─────────────────────────────────────────────────────────────────┤
│  Endpoint: POST /api/v1/plan/generate                           │
│  • Input Validation (Pydantic)                                  │
│  • CORS Middleware                                               │
│  • Error Handling & Logging                                      │
└───────────────┬──────────────────┬──────────────────────────────┘
                │                  │
                ↓                  ↓
    ┌─────────────────┐  ┌─────────────────┐
    │  Stage 1        │  │  Stage 2        │
    │  Visual ID      │→ │  Planning       │
    │  Nano 2 VL      │  │  Nano 3         │
    └─────────────────┘  └─────────────────┘
                │                  │
                ↓                  ↓
        ┌────────────────────────────┐
        │   NVIDIA AI Endpoints      │
        │   • Nemotron Nano 2 VL     │
        │   • Nemotron Nano 3        │
        └────────────────────────────┘
                │
                ↓
        ┌────────────────────────────┐
        │   Structured JSON Plan     │
        │   • Component Info         │
        │   • Chronological Steps    │
        │   • Safety Levels          │
        │   • Error Recovery         │
        └────────────────────────────┘
```

## Component Architecture

### 1. Entry Point: [main.py](main.py)

```python
FastAPI Application
├── Lifespan Management (startup/shutdown)
├── CORS Middleware Configuration
├── Primary Endpoint: /api/v1/plan/generate
├── Health Check Endpoint: /health
└── Global Exception Handling
```

**Responsibilities:**
- Initialize FastAPI app
- Configure CORS for frontend communication
- Route requests to service layer
- Handle HTTP errors and responses

### 2. Service Layer: [services.py](services.py)

```python
NemotronService
├── identify_component()      # Stage 1: VLM
├── generate_plan()            # Stage 2: LLM
└── orchestrate_full_pipeline() # Sequential coordination
```

**Key Features:**
- Async/await for non-blocking I/O
- Base64 image handling
- Structured JSON schema enforcement
- Retry logic and timeout handling

**Stage 1 - Visual Identification:**
```
Input: Base64 Image + User Goal
  ↓
Nemotron Nano 2 VL (Vision-Language Model)
  ↓
Output: {component: "...", state: "..."}
```

**Stage 2 - Chronological Planning:**
```
Input: Component + State + User Goal
  ↓
Nemotron Nano 3 (LLM with JSON Schema)
  ↓
Output: Structured TaskPlan (validated)
```

### 3. Data Models: [schemas.py](schemas.py)

```python
Pydantic Schemas
├── TaskRequest          # Input validation
├── TaskPlan             # Output validation
├── Step                 # Individual step model
├── ErrorState           # Error handling model
└── PLAN_SCHEMA          # JSON schema for Nemotron
```

**Data Flow:**
```
TaskRequest → Validation → Service → PLAN_SCHEMA → Nemotron
                                          ↓
                                    JSON Response
                                          ↓
                                   Pydantic Parse
                                          ↓
                                    TaskPlan → Frontend
```

### 4. Configuration: [config.py](config.py)

```python
Settings (Pydantic BaseSettings)
├── NVIDIA API Key (from env)
├── Endpoint URLs
├── Timeouts & Retries
└── CORS Origins
```

**Environment Variables:**
- `NVIDIA_API_KEY`: Required for API access
- `NANO2_VLM_URL`: Vision model endpoint
- `NANO3_LLM_URL`: Language model endpoint
- `API_TIMEOUT`: Request timeout (default: 60s)
- `DEBUG`: Enable detailed logging

## Request Flow Diagram

```
1. Frontend Request
   POST /api/v1/plan/generate
   Body: {image_data: "base64...", user_goal: "Blink LED"}
          ↓
2. Input Validation (Pydantic)
   TaskRequest schema validation
          ↓
3. Service Orchestration
   nemotron_service.orchestrate_full_pipeline()
          ↓
4. Stage 1: Visual Identification
   ┌────────────────────────────────┐
   │ identify_component()           │
   │ • Validate base64 encoding     │
   │ • Prepare VLM prompt           │
   │ • Call Nemotron Nano 2 VL      │
   │ • Parse component & state      │
   └────────────────────────────────┘
          ↓
   component = "Raspberry Pi 4"
   state = "Unpowered"
          ↓
5. Stage 2: Plan Generation
   ┌────────────────────────────────┐
   │ generate_plan()                │
   │ • Build context prompt         │
   │ • Attach PLAN_SCHEMA           │
   │ • Call Nemotron Nano 3         │
   │ • Validate with TaskPlan       │
   └────────────────────────────────┘
          ↓
6. Response Assembly
   TaskPlan JSON (validated)
          ↓
7. Frontend Receives
   {
     identified_component: "...",
     plan_steps: [...],
     common_errors: [...]
   }
```

## Error Handling Strategy

```python
Exception Hierarchy
├── Input Validation Errors → 400 Bad Request
│   └── Pydantic ValidationError
│
├── Service Errors → 503 Service Unavailable
│   ├── httpx.HTTPStatusError (NVIDIA API)
│   └── httpx.TimeoutException → 504 Gateway Timeout
│
├── Processing Errors → 500 Internal Server Error
│   ├── JSON Parsing Failures
│   └── Unexpected Exceptions
│
└── Configuration Errors → 500 Internal Server Error
    └── Missing API Key
```

## Async Architecture

```python
# All API calls are async to prevent blocking

async def generate_plan(request: TaskRequest):
    # Non-blocking orchestration
    plan = await nemotron_service.orchestrate_full_pipeline(...)

    # Stage 1: Async HTTP call
    async with httpx.AsyncClient() as client:
        response1 = await client.post(vlm_url, ...)

    # Stage 2: Async HTTP call
    async with httpx.AsyncClient() as client:
        response2 = await client.post(llm_url, ...)
```

**Benefits:**
- Multiple concurrent requests supported
- No thread blocking on I/O
- Efficient resource utilization
- FastAPI handles async event loop

## Security Considerations

1. **API Key Protection:**
   - Stored in `.env` (not committed)
   - Loaded via environment variables
   - Never exposed in responses

2. **Input Validation:**
   - Pydantic strict validation
   - Base64 encoding verification
   - Request size limits

3. **CORS Configuration:**
   - Whitelist-based origins
   - Explicit methods allowed
   - Credentials support

4. **Error Handling:**
   - No sensitive data in error messages
   - Debug mode controls verbosity
   - Structured error responses

## Performance Optimizations

1. **Async I/O:**
   - Non-blocking NVIDIA API calls
   - Concurrent request handling

2. **Caching:**
   - Settings cached with `@lru_cache`
   - HTTP client connection pooling

3. **Validation:**
   - Early input validation (fail fast)
   - Schema-enforced responses

4. **Logging:**
   - Structured logging
   - Configurable log levels

## Testing Strategy

```
Testing Pyramid
├── test_setup.py          # Environment validation
├── sample_request.py      # Integration testing
├── /health endpoint       # Service health check
└── /docs endpoint         # API contract testing
```

## Deployment Considerations

### Development
```bash
uvicorn main:app --reload
```

### Production
```bash
# With Gunicorn (multiple workers)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Scalability Notes

- **Horizontal Scaling:** Run multiple instances behind load balancer
- **Caching Layer:** Add Redis for response caching
- **Rate Limiting:** Implement per-user request limits
- **Queue System:** Add Celery for async task processing
- **Monitoring:** Integrate Prometheus/Grafana metrics

## Dependencies Graph

```
FastAPI (Web Framework)
├── Uvicorn (ASGI Server)
├── Pydantic (Data Validation)
│   └── Pydantic-Settings (Env Config)
├── HTTPX (Async HTTP Client)
└── Python-Dotenv (Env Loading)
```

## File Dependencies

```
main.py
├── imports schemas.py (TaskRequest, TaskPlan)
├── imports services.py (NemotronService)
└── imports config.py (get_settings)

services.py
├── imports schemas.py (PLAN_SCHEMA, TaskPlan)
└── imports config.py (get_settings)

config.py
└── imports pydantic_settings (BaseSettings)

schemas.py
└── imports pydantic (BaseModel, Field)
```

---

**Architecture Principles Applied:**

1. **Separation of Concerns:** Clear layers (API, Service, Data)
2. **Single Responsibility:** Each module has one job
3. **Dependency Injection:** Settings passed via constructor
4. **Async First:** Non-blocking I/O throughout
5. **Validation at Boundaries:** Input/output strict validation
6. **Fail Fast:** Early validation, explicit errors
7. **Configuration as Code:** Type-safe settings

**Built for HackUTD with production-grade patterns.**
