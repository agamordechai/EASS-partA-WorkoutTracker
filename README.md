# Workout Tracker API

A FastAPI-based REST API for managing workout exercises with SQLite persistence.

## Setup

### With Docker (Recommended)

```bash
# Build and start the API
docker compose up --build

# Or run in background
docker compose up -d --build

# Stop
docker compose down
```

The API runs at **http://localhost:8000**

### Without Docker (Local Development)

```bash
# Install dependencies with uv
uv pip install -e .

# Run the server
uvicorn app.main:app --reload
```

## API Usage Examples

### View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### HTTP File
The `api.http` file contains ready-to-use HTTP requests that can be executed directly in:
- **VS Code**: Install the REST Client extension
- **IntelliJ IDEA / PyCharm**: Built-in support
- **Other IDEs**: Most modern IDEs support `.http` files

### Example API Calls

#### Using curl

```bash
# Get all exercises
curl http://localhost:8000/exercises

# Get specific exercise
curl http://localhost:8000/exercises/1

# Create new exercise
curl -X POST http://localhost:8000/exercises \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deadlift",
    "sets": 3,
    "reps": 8,
    "weight": 100.0
  }'

# Update exercise (partial update)
curl -X PATCH http://localhost:8000/exercises/1 \
  -H "Content-Type: application/json" \
  -d '{"weight": 105.0}'

# Delete exercise
curl -X DELETE http://localhost:8000/exercises/1
```

#### Using HTTPie

```bash
# Get all exercises
http GET http://localhost:8000/exercises

# Create new exercise
http POST http://localhost:8000/exercises \
  name="Deadlift" \
  sets:=3 \
  reps:=8 \
  weight:=100.0

# Update exercise
http PATCH http://localhost:8000/exercises/1 \
  weight:=105.0
```


## Database

- **Location**: `./data/workout_tracker.db`
- **Type**: SQLite
- **Persistence**: Data persists via Docker volume mount
- **Seed data**: 6 sample exercises created on first run

### Resetting Database with Seed Script

To reset the database with fresh sample data:

```bash
# Using uv
uv run python scripts/seed.py

# Or with standard Python
python scripts/seed.py
```

This will clear existing exercises and populate the database with 10 sample workout exercises.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn
- **Database**: SQLite3
- **Validation**: Pydantic 2.10+
- **Package Manager**: uv
- **Container**: Docker + Docker Compose

## Project Structure

```
workout-tracker/
├── app/
│   ├── main.py           # FastAPI routes
│   ├── models.py         # Pydantic models
│   └── repository.py     # Database layer
├── data/                 # SQLite database (gitignored)
├── scripts/
│   └── seed.py           # Database seeding script
├── tests/
│   └── test_api.py       # API tests
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker orchestration
└── pyproject.toml        # Dependencies
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/{id}` | Get exercise by ID |
| POST | `/exercises` | Create new exercise |
| PATCH | `/exercises/{id}` | Update exercise |
| DELETE | `/exercises/{id}` | Delete exercise |

## Running Tests

```bash
pytest
pytest -v  # verbose
pytest --cov=app tests/  # with coverage
```

## AI Assistance

### Tools Used
- **GitHub Copilot**: Code completion and suggestions for FastAPI routes, Pydantic models, and test cases
- **AI Chat Assistant**: Architecture guidance and troubleshooting
