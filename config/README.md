# Configuration Directory

This directory contains configuration files for the Workout Tracker project.

## Files

### `docker-compose.yml`
Multi-service orchestration configuration for Docker Compose.

**Location:** `config/docker-compose.yml`
**Symlink:** Root directory has a symlink for convenience
**Usage:**
```bash
docker compose up -d
# Works from root via symlink
```

### `.env.example`
Template for environment variables.

**Location:** `config/.env.example`
**Symlink:** Root directory has a symlink for convenience
**Setup:**
```bash
# Copy template to create your .env file
cp config/.env.example .env
# OR use the symlink
cp .env.example .env

# Edit .env and add your secrets
nano .env
```

## Environment Variables

Your `.env` file should be placed in the **project root** (not in this config directory). It's gitignored to prevent committing secrets.

### Required Variables

- **`ANTHROPIC_API_KEY`**: Your Anthropic API key for AI Coach features
  - Get your key from: https://console.anthropic.com/

### Optional Variables

See `.env.example` for all available configuration options including:
- Database settings
- API server configuration
- AI model selection
- Redis configuration
- Logging levels

## Directory Purpose

The `/config/` directory centralizes all configuration files to:
1. Improve project organization
2. Separate config from code
3. Make it easier to find and manage settings
4. Maintain backward compatibility via symlinks

## Backward Compatibility

Symlinks in the project root ensure existing workflows continue to work:
- `docker-compose.yml` → `config/docker-compose.yml`
- `.env.example` → `config/.env.example`

Your actual `.env` file remains in the project root for compatibility with tools that expect it there.
