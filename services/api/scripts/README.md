# Scripts Directory - DEPRECATED

## ⚠️ This directory is deprecated

Scripts have been reorganized into purpose-specific directories:

- **CLI Tools** → `/cli/`
  - `workout_cli.py` - User-facing CLI commands
  - `cli/tests/` - CLI tests

- **Development Utilities** → `/dev/`
  - `refresh.py` - Async refresh script
  - `seed.py` - Database seeding
  - `demo.sh` - Demo script
  - `api.http` - HTTP request examples
  - `dev/tests/` - Dev utility tests

- **MCP Servers** → `/mcp/`
  - `exercises_server.py` - MCP server for exercises
  - `probe.py` - MCP testing tool

## Migration

Update your scripts and commands:

### Before
```bash
python scripts/cli.py stats
python scripts/refresh.py
python scripts/exercises_mcp.py
```

### After
```bash
python cli/workout_cli.py stats
python dev/refresh.py
python mcp/exercises_server.py
```

### Makefile
The `Makefile` has been updated to use the new paths.

## Backward Compatibility

A deprecated wrapper (`scripts/cli.py`) is provided for temporary backward compatibility, but it will be removed in a future version.
