# NAGARPAALAN 

**Modular Civic Infrastructure Intelligence Platform**

NAGARPAALAN AI is a modern, full-stack platform for monitoring, analyzing, and managing civic infrastructure. Built with a modular architecture, it combines geospatial analytics, real-time data pipelines, and AI-driven insights to empower municipal decision-making.

---

## Overview

NAGARPAALAN (नगरपालन — "City Governance") provides a unified interface for civic bodies to track infrastructure health, route citizen grievances, forecast maintenance needs, and visualize spatial data — all backed by a robust API and extensible plugin architecture.

---

## Architecture

| Layer        | Technology                          | Purpose                                |
|--------------|-------------------------------------|----------------------------------------|
| **Frontend** | React + TypeScript + Vite           | Interactive dashboards & maps          |
| **Backend**  | FastAPI (Python)                    | REST API, business logic, AI services  |
| **Database** | PostgreSQL 16 + PostGIS 3.4         | Relational + geospatial data store     |
| **Cache**    | Redis 7                            | Caching, task queues, pub/sub          |
| **Infra**    | Docker Compose                     | Local development orchestration        |

> See [`docs/architecture.md`](docs/architecture.md) for detailed diagrams and component descriptions.

---

## Tech Stack

| Component       | Version / Details          |
|-----------------|----------------------------|
| Python          | 3.11+                     |
| FastAPI         | 0.110+                    |
| SQLAlchemy      | 2.x (async)               |
| Alembic         | 1.13+                     |
| PostgreSQL      | 16                        |
| PostGIS         | 3.4                       |
| Redis           | 7 (Alpine)                |
| React           | 18+                       |
| TypeScript      | 5.x                       |
| Vite            | 5.x                       |
| Docker Compose  | v2+                       |
| Node.js         | 18+                       |

---

## Prerequisites

Ensure the following are installed on your development machine:

- **Python** 3.11 or higher — [python.org](https://www.python.org/downloads/)
- **Node.js** 18 or higher — [nodejs.org](https://nodejs.org/)
- **Docker** & **Docker Compose** v2+ — [docker.com](https://www.docker.com/get-started)
- **Git** — [git-scm.com](https://git-scm.com/)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/nagarpaalan.git
cd nagarpaalan
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your preferred values (database credentials, ports, etc.)
```

### 3. Start infrastructure services

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

This starts PostgreSQL (with PostGIS) and Redis. Verify they're healthy:

```bash
docker compose -f infrastructure/docker-compose.yml ps
```

### 4. Set up the backend

```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The API server starts at **http://localhost:8000**.

### 5. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at **http://localhost:5173**.

### 6. Open the application

Visit **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## API Documentation

Once the backend is running, interactive API docs are available at:

| Format       | URL                                      |
|--------------|------------------------------------------|
| Swagger UI   | [http://localhost:8000/docs](http://localhost:8000/docs)   |
| ReDoc        | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## Health Endpoints

| Endpoint             | Method | Description                          | Expected Response       |
|----------------------|--------|--------------------------------------|-------------------------|
| `/health`            | GET    | Application liveness check           | `{"status": "healthy"}` |
| `/health/ready`      | GET    | Readiness (DB + Redis connectivity)  | `{"status": "ready", "checks": {...}}` |
| `/api/v1/info`       | GET    | App version and environment info     | `{"app": "NAGARPAALAN AI", "version": "0.1.0"}` |

---

## Project Structure

```
nagarpaalan/
├── backend/                 # FastAPI application
│   ├── alembic/             # Database migrations
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Config, security, dependencies
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   └── main.py          # FastAPI app entry point
│   ├── tests/               # Backend test suite
│   └── requirements.txt     # Python dependencies
├── frontend/                # React + TypeScript SPA
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Route-level page components
│   │   ├── services/        # API client layer
│   │   ├── stores/          # State management
│   │   └── App.tsx          # Root component
│   ├── public/              # Static assets
│   └── package.json         # Node.js dependencies
├── infrastructure/          # Docker & deployment configs
│   ├── docker-compose.yml   # Local dev services
│   └── init-db/             # Database initialization scripts
├── docs/                    # Project documentation
│   ├── architecture.md      # System architecture
│   └── development.md       # Developer guide
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Development

### Running database migrations

```bash
cd backend

# Create a new migration after modifying models
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

### Running tests

```bash
cd backend
pytest -v
```

### Linting & formatting

```bash
# Backend
ruff check .
ruff format .

# Frontend
cd frontend
npm run lint
npm run format
```

> See [`docs/development.md`](docs/development.md) for the full developer guide.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>NAGARPAALAN AI</strong> — नगरपालन · Civic Intelligence for the Modern City
</p>
