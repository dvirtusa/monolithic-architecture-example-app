# Monolithic App - Python Version

A production-ready Python implementation of the monolithic architecture example, built with FastAPI and MongoDB.

## Features

- **User Registration** with comprehensive validation
- **JWT Authentication** for secure API access
- **Password Hashing** using bcrypt
- **Input Validation** with Pydantic
- **Unique Email Constraint** enforced at database level
- **Proper Error Handling** with custom exceptions
- **Health Check Endpoint** for monitoring
- **Interactive API Documentation** (Swagger/ReDoc)
- **Comprehensive Test Suite**
- **OpenTelemetry Integration** for distributed tracing
- **PlayerZero Web SDK** for frontend session tracking

## Project Structure

```
python_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB connection
│   ├── tracing.py           # OpenTelemetry initialization
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   └── pages.py         # HTML page routes
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py  # Business logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py      # JWT & password utilities
│   │   └── exceptions.py    # Custom exceptions
│   └── templates/
│       └── home.html        # Jinja2 template
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   └── test_auth.py         # Authentication tests
├── .env.example
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9+
- MongoDB 4.4+
- Docker (optional, for containerized deployment)

---

## Quick Start with Docker (Recommended)

### Run with Docker Compose (Full Stack)

From the **root directory** of the project:

```bash
# Start all services (MongoDB + Node.js + Python)
docker-compose up --build

# Access Python app at http://localhost:5000
# Access API docs at http://localhost:5000/docs
```

### Run Python App Only (Docker)

```bash
cd python_app

# Build the image
docker build -t python-monolithic-app .

# Run with external MongoDB
docker run -p 5000:8080 \
  -e MONGODB_URL=mongodb://user:password@host.docker.internal:27017/monolithic_app_db \
  -e SECRET_KEY=your-secret-key-here \
  -e DATABASE_NAME=monolithic_app_db \
  python-monolithic-app
```

### Docker Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URL` | Full MongoDB connection string | Yes |
| `DATABASE_NAME` | Database name | Yes |
| `SECRET_KEY` | JWT signing secret | Yes |
| `HOST` | Server host | No (default: 0.0.0.0) |
| `PORT` | Server port | No (default: 8080) |

---

## Installation (Local Development)

1. **Clone and navigate to the Python app:**
   ```bash
   cd python_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start MongoDB** (if not running):
   ```bash
   mongod
   ```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `monolithic_app_db` |
| `SECRET_KEY` | JWT signing key | (change in production!) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8080` |
| `DEBUG` | Enable debug mode | `false` |

### Observability Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAYERZERO_PROJECT_ID` | PlayerZero project ID for Web SDK | - |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint URL | `https://sdk.playerzero.app/otlp` |
| `OTEL_SERVICE_NAME` | Service/dataset name | `My Dataset Name` |
| `OTEL_ENVIRONMENT` | Deployment environment | `development` |

**Note:** Authorization headers are preconfigured in `app/tracing.py`.

## Running the Application

**Development:**
```bash
cd python_app
python -m app.main
```

**Or with uvicorn directly:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Access the application at: http://localhost:8080

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Home page (HTML) | No |
| `GET` | `/health` | Health check | No |
| `POST` | `/api/auth/register` | Register new user | No |
| `POST` | `/api/auth/login` | Login & get token | No |
| `GET` | `/api/auth/me` | Get current user | Yes |
| `GET` | `/docs` | Swagger UI docs | No |
| `GET` | `/redoc` | ReDoc docs | No |

### Register User

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Current User

```bash
curl http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

## Password Requirements

Passwords must:
- Be at least 8 characters long
- Contain at least one uppercase letter
- Contain at least one lowercase letter
- Contain at least one digit
- Contain at least one special character (!@#$%^&*(),.?":{}|<>)

## Running Tests

```bash
cd python_app
pytest -v
```

**With coverage:**
```bash
pytest --cov=app --cov-report=html
```

## Issues Fixed from Original Node.js Version

| Original Issue | Python Solution |
|----------------|-----------------|
| No error handling | Custom exceptions + global error handlers |
| No input validation | Pydantic models with validators |
| Client-side only auth | JWT-based server-side authentication |
| No password field | Bcrypt-hashed passwords |
| Hardcoded port/host | Environment variables via pydantic-settings |
| All logic in one file | Modular structure (routes, services, models) |
| No tests | Comprehensive pytest test suite |
| No unique email constraint | MongoDB unique index |
| No logging | Python logging throughout |

## Technology Stack

- **FastAPI** - Modern, fast web framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **Jinja2** - HTML templating
- **pytest** - Testing framework

---

## Docker Reference

### Dockerfile Features

- Based on `python:3.11-slim` for minimal image size
- Non-root user for security
- Multi-stage build optimization
- Health check ready

### Useful Docker Commands

```bash
# Build the image
docker build -t python-monolithic-app .

# Run container
docker run -p 5000:8080 --env-file .env python-monolithic-app

# Run with inline environment variables
docker run -p 5000:8080 \
  -e MONGODB_URL=mongodb://localhost:27017 \
  -e DATABASE_NAME=monolithic_app_db \
  -e SECRET_KEY=your-secret-key \
  python-monolithic-app

# View container logs
docker logs -f <container_id>

# Execute shell in running container
docker exec -it <container_id> /bin/bash

# Stop container
docker stop <container_id>
```

### Docker Compose (from root directory)

```bash
# Start all services
docker-compose up -d

# View Python app logs
docker-compose logs -f python-app

# Restart Python app only
docker-compose restart python-app

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Health Check

The application exposes a health endpoint:

```bash
curl http://localhost:5000/health
# Response: {"status": "healthy"}
```
