# Development Guide — NAGARPAALAN AI

This guide covers everything you need to set up, run, and contribute to NAGARPAALAN AI locally.

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Running Services](#running-services)
- [Database Migrations](#database-migrations)
- [Code Organization & Conventions](#code-organization--conventions)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### 1. Install Prerequisites

| Tool             | Minimum Version | Installation                                          |
|------------------|-----------------|-------------------------------------------------------|
| Python           | 3.11+           | [python.org](https://www.python.org/downloads/)       |
| Node.js          | 18+             | [nodejs.org](https://nodejs.org/)                     |
| Docker           | 24+             | [docker.com](https://www.docker.com/get-started)      |
| Docker Compose   | v2+             | Included with Docker Desktop                          |
| Git              | 2.40+           | [git-scm.com](https://git-scm.com/)                  |

### 2. Clone & Configure

```bash
# Clone the repository
git clone https://github.com/your-org/nagarpaalan.git
cd nagarpaalan

# Create your local environment file
cp .env.example .env
```

Edit `.env` to customize credentials, ports, or feature flags as needed. The defaults work out of the box for local development.

### 3. Start Infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

Verify all containers are healthy:

```bash
docker compose -f infrastructure/docker-compose.yml ps
```

You should see `nagarpaalan-db` and `nagarpaalan-redis` both reporting `healthy`.

### 4. Set Up the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Set Up the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend is now available at **http://localhost:5173** and proxies API requests to the backend.

---

## Running Services

### Start all infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

### Stop all infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml down
```

### Stop and remove volumes (⚠️ destroys data)

```bash
docker compose -f infrastructure/docker-compose.yml down -v
```

### View logs

```bash
# All services
docker compose -f infrastructure/docker-compose.yml logs -f

# Specific service
docker compose -f infrastructure/docker-compose.yml logs -f db
docker compose -f infrastructure/docker-compose.yml logs -f redis
```

### Connect to PostgreSQL directly

```bash
docker exec -it nagarpaalan-db psql -U nagarpaalan -d nagarpaalan_db
```

### Connect to Redis CLI

```bash
docker exec -it nagarpaalan-redis redis-cli
```

---

## Database Migrations

NAGARPAALAN uses [Alembic](https://alembic.sqlalchemy.org/) for database schema versioning. All migration commands should be run from the `backend/` directory with the virtual environment activated.

### Create a new migration

After modifying SQLAlchemy models:

```bash
alembic revision --autogenerate -m "add users table"
```

> **Always review** the generated migration file in `alembic/versions/` before applying it. Auto-generated migrations can miss certain changes (e.g., renamed columns).

### Apply migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply next N migrations
alembic upgrade +1
```

### Rollback migrations

```bash
# Rollback the last migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Rollback all migrations (⚠️ destructive)
alembic downgrade base
```

### View migration history

```bash
# List all migrations with status
alembic history --verbose

# Show current applied revision
alembic current
```

### Migration best practices

1. **One logical change per migration** — don't bundle unrelated schema changes.
2. **Always review auto-generated code** — Alembic can't detect column renames or data migrations.
3. **Test both upgrade and downgrade** — every migration should be fully reversible.
4. **Never edit an already-applied migration** — create a new one instead.

---

## Code Organization & Conventions

### Backend (Python / FastAPI)

```
backend/
├── alembic/               # Migration scripts
│   ├── versions/          # Individual migration files
│   └── env.py             # Alembic environment config
├── app/
│   ├── api/               # Route handlers grouped by domain
│   │   └── v1/            # Versioned API routes
│   ├── core/              # App-wide config, security, deps
│   │   ├── config.py      # Pydantic Settings
│   │   ├── database.py    # Async engine & session factory
│   │   └── security.py    # JWT, password hashing
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic (one per domain)
│   └── main.py            # FastAPI app factory
├── tests/                 # Pytest test suite
│   ├── conftest.py        # Shared fixtures
│   ├── test_api/          # Integration tests
│   └── test_services/     # Unit tests
├── alembic.ini            # Alembic configuration
└── requirements.txt       # Pinned dependencies
```

#### Conventions

- **Naming**: snake_case for files, functions, variables. PascalCase for classes.
- **Imports**: Use absolute imports (`from app.models.user import User`).
- **Type hints**: Required on all function signatures.
- **Docstrings**: Google-style docstrings on all public functions and classes.
- **Linting**: `ruff check .` — must pass with zero errors.
- **Formatting**: `ruff format .` — auto-format before committing.

### Frontend (React / TypeScript)

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   └── common/        # Buttons, inputs, cards
│   ├── pages/             # Route-level views
│   ├── services/          # API client functions
│   ├── stores/            # State management (Zustand / Context)
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Helper functions
│   └── App.tsx            # Root component with router
├── public/                # Static assets
├── index.html             # HTML entry point
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies & scripts
```

#### Conventions

- **Naming**: PascalCase for components. camelCase for functions, variables, hooks.
- **Components**: One component per file. File name matches component name.
- **Hooks**: Prefix with `use` (e.g., `useGrievances.ts`).
- **Types**: Co-locate with usage or place in `types/` for shared types.
- **Linting**: ESLint with strict TypeScript rules.

---

## Environment Variables Reference

| Variable            | Default                        | Description                                  |
|---------------------|--------------------------------|----------------------------------------------|
| `APP_NAME`          | `NAGARPAALAN AI`               | Application display name.                    |
| `APP_VERSION`       | `0.1.0`                        | Current application version.                 |
| `DEBUG`             | `false`                        | Enable debug mode (`true` / `false`).        |
| `LOG_LEVEL`         | `INFO`                         | Logging level: DEBUG, INFO, WARNING, ERROR.  |
| `LOG_FORMAT`        | `json`                         | Log output format: `json` or `text`.         |
| `API_V1_PREFIX`     | `/api/v1`                      | Base path prefix for v1 API routes.          |
| `CORS_ORIGINS`      | `["http://localhost:5173"]`    | Allowed CORS origins (JSON array).           |
| `POSTGRES_HOST`     | `localhost`                    | PostgreSQL server hostname.                  |
| `POSTGRES_PORT`     | `5432`                         | PostgreSQL server port.                      |
| `POSTGRES_USER`     | `nagarpaalan`                  | PostgreSQL username.                         |
| `POSTGRES_PASSWORD` | `changeme`                     | PostgreSQL password. **Change in production.**|
| `POSTGRES_DB`       | `nagarpaalan_db`               | PostgreSQL database name.                    |
| `REDIS_HOST`        | `localhost`                    | Redis server hostname.                       |
| `REDIS_PORT`        | `6379`                         | Redis server port.                           |
| `REDIS_DB`          | `0`                            | Redis database index (0–15).                 |

> ⚠️ **Never commit `.env` files to version control.** The `.gitignore` is configured to exclude them.

---

## Troubleshooting

### Docker containers won't start

**Symptom**: `docker compose up` fails or containers exit immediately.

**Solutions**:
1. Ensure Docker Desktop is running.
2. Check for port conflicts: `netstat -ano | findstr :5432` (Windows) or `lsof -i :5432` (macOS/Linux).
3. If ports are in use, change `POSTGRES_PORT` or `REDIS_PORT` in `.env`.
4. Remove orphan volumes and retry:
   ```bash
   docker compose -f infrastructure/docker-compose.yml down -v
   docker compose -f infrastructure/docker-compose.yml up -d
   ```

### Database connection refused

**Symptom**: Backend raises `ConnectionRefusedError` when starting.

**Solutions**:
1. Verify the database container is healthy: `docker ps`.
2. Ensure `POSTGRES_HOST` in `.env` is `localhost` (not `db` — `db` is only used inside Docker networks).
3. Wait a few seconds after starting containers — PostgreSQL needs time to initialize on first run.

### Alembic migration errors

**Symptom**: `alembic upgrade head` fails with a revision error.

**Solutions**:
1. Ensure you're in the `backend/` directory with the virtualenv activated.
2. Check `alembic.ini` has the correct `sqlalchemy.url` or that it reads from environment variables.
3. If the database schema is out of sync, check `alembic current` against `alembic history`.
4. For a fresh start (dev only): drop the database and re-run migrations:
   ```bash
   docker exec -it nagarpaalan-db psql -U nagarpaalan -c "DROP DATABASE nagarpaalan_db;"
   docker exec -it nagarpaalan-db psql -U nagarpaalan -c "CREATE DATABASE nagarpaalan_db;"
   alembic upgrade head
   ```

### Frontend can't reach the backend API

**Symptom**: Network errors or CORS errors in the browser console.

**Solutions**:
1. Ensure the backend is running on port 8000.
2. Check that `CORS_ORIGINS` in `.env` includes the frontend URL (`http://localhost:5173`).
3. If using a Vite proxy, verify `vite.config.ts` has the correct proxy target.

### Redis connection issues

**Symptom**: `ConnectionError: Error connecting to Redis`.

**Solutions**:
1. Verify the Redis container is running: `docker ps | grep redis`.
2. Test connectivity: `docker exec -it nagarpaalan-redis redis-cli ping` (should return `PONG`).
3. Check `REDIS_HOST` and `REDIS_PORT` in `.env`.

### PostGIS extension not available

**Symptom**: `ERROR: type "geometry" does not exist`.

**Solutions**:
1. The init script should have run automatically. Verify:
   ```bash
   docker exec -it nagarpaalan-db psql -U nagarpaalan -d nagarpaalan_db -c "SELECT PostGIS_Version();"
   ```
2. If it returns nothing, manually enable the extension:
   ```bash
   docker exec -it nagarpaalan-db psql -U nagarpaalan -d nagarpaalan_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```

---

<p align="center"><em>Questions? Open an issue or reach out on the team channel.</em></p>
