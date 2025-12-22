# Workout Tracker API

A FastAPI-based REST API for managing workout exercises with PostgreSQL persistence.

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- Or for local development:
  - Python 3.12+
  - [uv](https://docs.astral.sh/uv/) package manager

## Project Structure

```
├── services/
│   ├── api/                 # FastAPI REST service
│   │   ├── Dockerfile       # API container definition
│   │   ├── pyproject.toml   # API-specific dependencies
│   │   ├── src/
│   │   │   ├── api.py       # FastAPI application
│   │   │   └── database/    # Database models, config, repository
│   │   └── tests/           # API tests
│   │
│   └── frontend/            # Streamlit dashboard
│       ├── Dockerfile       # Frontend container definition
│       ├── pyproject.toml   # Frontend-specific dependencies
│       ├── src/
│       │   ├── dashboard.py # Streamlit UI
│       │   └── client.py    # HTTP client for API
│       └── tests/           # Frontend tests
│
├── data/                    # Local development data
│   └── exports/             # Exported CSV/JSON files
│
├── scripts/                 # Utility scripts
│   ├── api.http             # HTTP requests for API testing
│   └── seed.py              # Database seeding script
│
├── docker-compose.yml       # Multi-service orchestration
└── pyproject.toml           # Root project dependencies (for local dev)
```

## Setup

### Option 1: Docker Compose (Recommended)

```bash
# 1. Start all services (database, API, frontend)
docker-compose up -d

# 2. Check all services are running
docker-compose ps

# 3. Open dashboard
open http://localhost:8501

# 4. Stop all services
docker-compose down

# 5. Stop and remove all data (fresh start)
docker-compose down -v
```

**Services:**
- **PostgreSQL Database**: Internal (port 5432)
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit Dashboard**: http://localhost:8501

### Option 2: Local Development (Without Docker)

```bash
# Install dependencies using uv
uv sync

# Terminal 1 - Start API
uv run uvicorn services.api.src.api:app --reload

# Terminal 2 - Start dashboard
uv run streamlit run services/frontend/src/dashboard.py
```

> **Note:** Local development uses SQLite by default. Set `DATABASE_URL` environment variable to use PostgreSQL.

## Configuration

The application uses sensible defaults. Override via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `data/workout_tracker.db` | Database file path |
| `API_PORT` | `8000` | API server port |
| `API_DEBUG` | `false` | Enable debug mode |
| `APP_LOG_LEVEL` | `INFO` | Logging level |
| `APP_CORS_ORIGINS` | `*` | Allowed CORS origins |

```bash
# Optional: Create .env from example
cp .env.example .env
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check with DB status |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/{id}` | Get exercise by ID |
| POST | `/exercises` | Create new exercise |
| PATCH | `/exercises/{id}` | Update exercise (partial) |
| DELETE | `/exercises/{id}` | Delete exercise |

### Example API Calls

```bash
# Get all exercises
curl http://localhost:8000/exercises

# Create new exercise
curl -X POST http://localhost:8000/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Deadlift", "sets": 3, "reps": 8, "weight": 100.0}'

# Update exercise
curl -X PATCH http://localhost:8000/exercises/1 \
  -H "Content-Type: application/json" \
  -d '{"weight": 105.0}'

# Delete exercise
curl -X DELETE http://localhost:8000/exercises/1
```

The `scripts/api.http` file contains ready-to-use HTTP requests for VS Code REST Client or JetBrains HTTP Client.

## User Interfaces

The Streamlit Dashboard provides a visual web interface for managing exercises.

### Streamlit Dashboard

A web-based dashboard with real-time statistics and full CRUD operations.

**Features:**
- List & filter exercises (Weighted/Bodyweight/All)
- Search by exercise name
- Real-time metrics (total exercises, sets, volume)
- Create, update, and delete exercises
- Auto-refresh every 30 seconds

**Running the Dashboard:**
```bash
# With Docker
docker-compose up -d
# Access at http://localhost:8501

# Without Docker (API must be running)
uv run streamlit run services/frontend/src/dashboard.py
```

**User Guide:**
1. View exercises in the main table
2. Use dropdown to filter by type (Weighted/Bodyweight/All)
3. Search exercises by name
4. Click "Load Exercise" to update an existing exercise
5. Fill the form to create new exercises
6. Delete exercises from the bottom section


## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest services/api/tests/test_api.py -v
uv run pytest services/frontend/tests/test_client.py -v

# Run with coverage
uv run pytest --cov=services
```


## Database

- **Docker:** PostgreSQL 15 (data persists via Docker volume)
- **Local dev:** SQLite (`data/workout_tracker.db`)
- **Seed data:** Use the dashboard to add exercises, or run:
  ```bash
  uv run python scripts/seed.py
  ```

## Tech Stack

- **Framework:** FastAPI 0.115+
- **Server:** Uvicorn
- **Database:** PostgreSQL 15 (Docker) / SQLite3 (local)
- **Validation:** Pydantic 2.10+
- **Dashboard:** Streamlit 1.40+
- **HTTP Client:** httpx
- **Package Manager:** uv
- **Container:** Docker + Docker Compose

## AI Assistance

### Tools Used
- **GitHub Copilot:** Code completion for FastAPI routes, Pydantic models, and test cases
- **Claude (AI Assistant):** Architecture guidance, project restructuring, and documentation

### How Outputs Were Verified
- All generated code was tested locally using `pytest`
- API endpoints verified via Swagger UI and `scripts/api.http`
- Dashboard functionality tested manually in browser
- Docker builds verified with `docker-compose up --build`
