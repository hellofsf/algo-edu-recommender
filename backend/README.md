# AlgoEdu Recommender Backend

Algorithm Education Recommendation System Backend - Phase 1

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for local development)

### Local Development Setup

1. **Clone and install dependencies:**
   ```bash
   cd backend
   pip install -e ".[dev]"
   ```

2. **Generate JWT keys:**
   ```bash
   mkdir -p secrets
   openssl genrsa -out secrets/jwt-private.pem 2048
   openssl rsa -in secrets/jwt-private.pem -pubout -out secrets/jwt-public.pem
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

5. **Run the application:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users (requires authentication)
- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/me/progress` - Get learning progress
- `GET /api/v1/users/me/stats` - Get user statistics

### Health Checks
- `GET /api/v1/health` - Full health check with service status
- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/ready` - Readiness probe

## Running Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── deps.py          # Dependency injection
│   │   └── v1/
│   │       ├── auth.py      # Authentication routes
│   │       ├── users.py     # User routes
│   │       └── health.py    # Health check routes
│   ├── core/
│   │   ├── security.py     # JWT & password hashing
│   │   └── rate_limit.py   # Rate limiting middleware
│   ├── db/
│   │   ├── session.py      # PostgreSQL connection
│   │   └── neo4j.py        # Neo4j connection
│   ├── models/
│   │   └── user.py         # User SQLAlchemy model
│   ├── schemas/
│   │   ├── auth.py         # Auth Pydantic schemas
│   │   └── user.py         # User Pydantic schemas
│   └── services/
│       └── auth.py         # Authentication service
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   └── test_auth.py       # Authentication tests
├── secrets/               # JWT keys (gitignored)
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## Tech Stack

- **Framework:** FastAPI 0.115.x + Uvicorn
- **Database:** PostgreSQL (asyncpg + SQLAlchemy 2.0)
- **Graph DB:** Neo4j
- **Cache:** Redis
- **Auth:** JWT RS256
- **Validation:** Pydantic v2
- **Testing:** pytest + pytest-asyncio
