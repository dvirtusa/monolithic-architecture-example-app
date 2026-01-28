# Monolithic Architecture Example App

A demonstration of monolithic software architecture as explained in [my blog post on architectures](https://zachgoll.github.io/blog/2019/build-production-web-app-part-4/).

## What is a Monolithic Architecture?

A monolithic architecture bundles all components into one codebase:

* **Views** - User interface templates
* **Application/Business Logic** - Core functionality
* **Data Access/Database** - Data persistence layer

Each layer is separated in this application, but it remains monolithic because any change requires:

1. The entire application to be restarted
2. Changes across multiple parts of the app

## Project Structure

```
├── app.js                 # Main Node.js application
├── tracing.js             # OpenTelemetry tracing initialization
├── views/
│   └── home.ejs          # EJS template
├── python_app/           # Python/FastAPI version (production-ready)
├── Dockerfile            # Node.js container
├── docker-compose.yml    # Full stack orchestration
├── mongo-init.js         # MongoDB initialization
├── .env.example          # Environment variables template
├── OPENTELEMETRY.md      # OpenTelemetry integration guide
└── PLAYERZERO_WEB_SDK.md # Frontend SDK integration guide
```

## Available Versions

| Version | Port | Description |
|---------|------|-------------|
| **Node.js** | 8080 | Original demo application |
| **Python** | 5000 | Production-ready version with auth, validation, tests |

---

## Quick Start with Docker (Recommended)

The easiest way to run both applications with MongoDB:

```bash
# Start all services (MongoDB + Node.js + Python)
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Access Points

| Service | URL |
|---------|-----|
| Node.js App | http://localhost:8080 |
| Python App | http://localhost:5000 |
| Python API Docs | http://localhost:5000/docs |
| MongoDB | localhost:27017 |

### Docker Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f nodejs-app
docker-compose logs -f python-app

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build
```

---

## Run Node.js App Only (Docker)

```bash
# Build the image
docker build -t nodejs-monolithic-app .

# Run with external MongoDB
docker run -p 8080:8080 \
  -e DB_USER=youruser \
  -e DB_PW=yourpassword \
  -e MONGODB_HOST=host.docker.internal \
  nodejs-monolithic-app
```

---

## Run Node.js App Locally (Without Docker)

### Prerequisites

- Node.js 18+
- MongoDB 4.4+

### Setup MongoDB

```bash
# Start MongoDB shell
mongosh

# Create database and user
use monolithic_app_db

db.createUser({
    user: "yourname",
    pwd: "yourpassword",
    roles: ["readWrite", "dbAdmin"]
})
```

### Run the Application

```bash
# Set environment variables
export DB_USER=yourname
export DB_PW=yourpassword

# Install dependencies
npm install

# Start the app
npm run start
```

Visit: http://localhost:8080

---

## Environment Variables

### Core Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | MongoDB username | (required) |
| `DB_PW` | MongoDB password | (required) |
| `MONGODB_HOST` | MongoDB host | `127.0.0.1` |

### Observability Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAYERZERO_PROJECT_ID` | PlayerZero project ID for frontend SDK | - |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint URL | `https://sdk.playerzero.app/otlp` |
| `OTEL_SERVICE_NAME` | Service/dataset name | `My Dataset Name` |
| `OTEL_ENVIRONMENT` | Deployment environment | `development` |

**Note:** Authorization headers are preconfigured in the tracing files. See [OPENTELEMETRY.md](OPENTELEMETRY.md) for details.

---

## Python Version

A production-ready Python/FastAPI implementation is available in the `python_app/` directory with:

- ✅ JWT Authentication
- ✅ Password hashing (bcrypt)
- ✅ Input validation (Pydantic)
- ✅ Proper error handling
- ✅ Comprehensive test suite
- ✅ API documentation (Swagger/ReDoc)

See [python_app/README.md](python_app/README.md) for details.

---

## Observability

Both applications are instrumented with **OpenTelemetry** for backend tracing and **PlayerZero Web SDK** for frontend session tracking:

- **[OpenTelemetry Integration](OPENTELEMETRY.md)** - Backend traces, database queries, HTTP calls
- **[PlayerZero Web SDK](PLAYERZERO_WEB_SDK.md)** - Frontend session recording, error tracking, user identification

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   MongoDB   │  │  Node.js    │  │      Python         │ │
│  │   :27017    │  │   :8080     │  │       :5000         │ │
│  │             │  │             │  │                     │ │
│  │  - users    │◄─┤  app.js     │  │  FastAPI + Motor    │ │
│  │  collection │  │  (Express)  │  │  (async MongoDB)    │ │
│  │             │◄─┼─────────────┼──┤                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Node.js App (Port 8080)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| POST | `/register` | Register user |

### Python App (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |
| GET | `/docs` | Swagger UI |

---

## License

MIT
