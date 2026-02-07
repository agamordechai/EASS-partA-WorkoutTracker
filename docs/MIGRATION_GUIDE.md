# Project Reorganization Migration Guide

## Overview

The Workout Tracker project has been reorganized to improve maintainability, reduce code duplication, and create clearer separation of concerns.

## What Changed

### Directory Structure

**Before:**
```
/
├── scripts/              # Mixed purposes (CLI, dev, MCP, tests)
├── services/
│   ├── api/
│   ├── ai_coach/
│   ├── worker/
│   └── frontend/
├── docker-compose.yml
├── .env.example
├── service-contract.md
└── exercises.md
```

**After:**
```
/
├── config/               # NEW: Configuration files
│   ├── docker-compose.yml
│   └── .env.example
├── cli/                  # NEW: User-facing CLI tools
│   ├── workout_cli.py
│   └── tests/
├── dev/                  # NEW: Development utilities
│   ├── refresh.py
│   ├── seed.py
│   ├── demo.sh
│   ├── api.http
│   └── tests/
├── mcp/                  # NEW: MCP server tools
│   ├── exercises_server.py
│   └── probe.py
├── services/
│   ├── shared/           # NEW: Shared library
│   │   ├── models/       # Common Pydantic models
│   │   ├── clients/      # Base HTTP clients
│   │   └── config/       # Shared config utilities
│   ├── api/
│   ├── ai_coach/
│   ├── worker/
│   └── frontend/
├── docs/
│   ├── architecture/     # NEW: Architecture docs
│   ├── service-contract.md    # MOVED
│   └── exercises.md           # MOVED
├── docker-compose.yml    # Symlink to config/
└── .env.example          # Symlink to config/
```

### File Movements

| Old Path | New Path | Notes |
|----------|----------|-------|
| `scripts/cli.py` | `cli/workout_cli.py` | Deprecated wrapper exists |
| `scripts/test_cli.py` | `cli/tests/test_workout_cli.py` | |
| `scripts/refresh.py` | `dev/refresh.py` | |
| `scripts/seed.py` | `dev/seed.py` | |
| `scripts/demo.sh` | `dev/demo.sh` | |
| `scripts/api.http` | `dev/api.http` | |
| `scripts/test_refresh.py` | `dev/tests/test_refresh.py` | |
| `scripts/exercises_mcp.py` | `mcp/exercises_server.py` | |
| `scripts/mcp_probe.py` | `mcp/probe.py` | |
| `docker-compose.yml` | `config/docker-compose.yml` | Symlink in root |
| `.env.example` | `config/.env.example` | Symlink in root |
| `service-contract.md` | `docs/service-contract.md` | |
| `exercises.md` | `docs/exercises.md` | |

### Code Changes

#### Import Path Updates

**AI Coach Service** (`services/ai_coach/src/models.py`):
```python
# Before
class ExerciseFromAPI(BaseModel):
    id: int
    name: str
    # ...

# After
from services.shared.models import ExerciseResponse
ExerciseFromAPI = ExerciseResponse  # Alias for compatibility
```

**API Service** (`services/api/src/database/models.py`):
```python
# Before
class Exercise(BaseModel):
    name: str
    # ...

# After
from services.shared.models import ExerciseBase as Exercise
```

**Worker Service** (`services/worker/src/tasks/refresh.py`):
```python
# Before
from scripts.refresh import ExerciseRefresher, IdempotencyStore

# After
from dev.refresh import ExerciseRefresher, IdempotencyStore
```

**MCP Probe** (`mcp/probe.py`):
```python
# Before
from scripts.exercises_mcp import list_exercises, get_exercise

# After
from mcp.exercises_server import list_exercises, get_exercise
```

## Migration Steps

### For Developers

1. **Pull the latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update your local commands:**
   - CLI: `python scripts/cli.py` → `python cli/workout_cli.py`
   - Refresh: `python scripts/refresh.py` → `python dev/refresh.py`
   - MCP: `python scripts/exercises_mcp.py` → `python mcp/exercises_server.py`

3. **Use the Makefile (already updated):**
   ```bash
   make db-seed    # Uses cli/workout_cli.py
   make stats      # Uses cli/workout_cli.py
   ```

4. **Update any custom scripts** that reference old paths

### For CI/CD

No changes required! The Makefile has been updated and Docker Compose still works (via symlinks).

### For Documentation

Update any references to:
- `scripts/` → `cli/`, `dev/`, or `mcp/`
- `service-contract.md` → `docs/service-contract.md`
- `exercises.md` → `docs/exercises.md`

## Backward Compatibility

- **Symlinks**: `docker-compose.yml` and `.env.example` remain in root via symlinks
- **Deprecated wrapper**: `scripts/cli.py` still works but shows a deprecation warning
- **Makefile**: All commands updated to use new paths

## Benefits

1. **Clearer organization**: CLI, dev tools, and MCP servers are now separated
2. **Reduced duplication**: Shared models eliminate duplicate code across services
3. **Better discoverability**: Purpose-driven directories make it clear where to find tools
4. **Easier testing**: Tests are organized alongside their respective tools
5. **Consistent data models**: Single source of truth for Exercise models

## New Shared Library

### Location
`services/shared/`

### What's Included

- **Models** (`services/shared/models/exercise.py`):
  - `ExerciseBase` - Base exercise model
  - `ExerciseCreate` - For creating exercises
  - `ExerciseResponse` - API responses
  - `ExerciseEditRequest` - Partial updates
  - `PaginatedExerciseResponse` - Paginated lists

- **Clients** (`services/shared/clients/base_client.py`):
  - `BaseAPIClient` - Base HTTP client with health checks, connection management

- **Config** (`services/shared/config/base_settings.py`):
  - `LogLevel` - Consistent log level enum
  - `build_redis_url()` - Redis URL builder

### Usage

```python
from services.shared.models import ExerciseResponse, ExerciseCreate
from services.shared.clients import BaseAPIClient
from services.shared.config import LogLevel, build_redis_url
```

## Troubleshooting

### Import errors

If you see `ModuleNotFoundError` for shared models:
- Ensure you're running from the project root
- Check that Python path includes the project root

### Deprecated warnings

If you see warnings about `scripts/cli.py`:
- Update your command to use `cli/workout_cli.py`
- The wrapper will be removed in a future version

### Tests failing

- Run `make test` from project root
- Check that all import paths in your code are updated

## Questions?

See [Architecture Documentation](./architecture/) for detailed design decisions.
