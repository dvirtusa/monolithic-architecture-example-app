# OpenTelemetry Integration with PlayerZero

This project is instrumented with OpenTelemetry to export traces to PlayerZero for observability and monitoring.

## Overview

Both the Node.js and Python applications are configured to automatically capture and export telemetry data including:

- **Traces**: Request/response flows, database queries, external HTTP calls
- **Service metadata**: Service name, version, environment
- **Automatic instrumentation**: Express, FastAPI, MongoDB, HTTP clients

## Architecture

```
┌─────────────────┐        OTLP/HTTP         ┌──────────────────┐
│   Node.js App   │──────────────────────────▶│                  │
│  (port 8080)    │                           │   PlayerZero     │
└─────────────────┘                           │   OTLP Endpoint  │
                                              │                  │
┌─────────────────┐        OTLP/HTTP         │                  │
│   Python App    │──────────────────────────▶│                  │
│  (port 5000)    │                           └──────────────────┘
└─────────────────┘
```

## Quick Start

### 1. Get PlayerZero API Key

1. Log in to [PlayerZero](https://playerzero.ai)
2. Navigate to **Settings** → **API Keys**
3. Create a new API key for OTLP

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your PlayerZero API key
nano .env
```

Update the following variables:

```env
PLAYERZERO_API_KEY=your-actual-api-key-here
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.playerzero.app
ENVIRONMENT=production
```

### 3. Run with Docker Compose

```bash
# Build and start all services with telemetry enabled
docker-compose up --build

# Check logs to verify telemetry initialization
docker-compose logs nodejs-app | grep "OpenTelemetry"
docker-compose logs python-app | grep "OpenTelemetry"
```

Expected output:
```
nodejs-app  | OpenTelemetry tracing initialized
nodejs-app  | Service: nodejs-monolithic-app
nodejs-app  | Environment: docker
nodejs-app  | OTLP Endpoint: https://otlp.playerzero.app

python-app  | OpenTelemetry tracing initialized
python-app  | Service: python-monolithic-app
python-app  | Environment: docker
python-app  | OTLP Endpoint: https://otlp.playerzero.app
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PLAYERZERO_API_KEY` | PlayerZero API key for authentication | - | Yes |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint URL | `https://otlp.playerzero.app` | No |
| `OTEL_SERVICE_NAME` | Service identifier | `nodejs-app` / `python-app` | No |
| `OTEL_ENVIRONMENT` | Deployment environment | `development` | No |

### Service Names

The services are automatically named in `docker-compose.yml`:

- **Node.js**: `nodejs-monolithic-app`
- **Python**: `python-monolithic-app`

These names will appear in PlayerZero dashboards for filtering and analysis.

## What's Being Traced

### Node.js App

**Auto-instrumented:**
- Express HTTP server (routes, middleware)
- MongoDB queries via Mongoose
- Outbound HTTP requests
- Error handling and exceptions

**Manual instrumentation:**
- Custom spans can be added using OpenTelemetry API

### Python App

**Auto-instrumented:**
- FastAPI endpoints and middleware
- Motor/PyMongo database operations
- HTTPX client requests
- Request validation (Pydantic)

**Manual instrumentation:**
- Custom spans can be added using OpenTelemetry API

## Implementation Details

### Node.js Implementation

**Files:**
- `tracing.js` - OpenTelemetry SDK initialization
- `package.json` - OpenTelemetry dependencies
- `Dockerfile` - Updated CMD to require tracing.js

**Key packages:**
```json
{
  "@opentelemetry/sdk-node": "^0.45.1",
  "@opentelemetry/auto-instrumentations-node": "^0.40.3",
  "@opentelemetry/exporter-trace-otlp-http": "^0.45.1"
}
```

**Startup:**
```bash
node --require ./tracing.js app.js
```

### Python Implementation

**Files:**
- `app/tracing.py` - OpenTelemetry configuration
- `app/main.py` - Calls `setup_telemetry()`
- `requirements.txt` - OpenTelemetry dependencies

**Key packages:**
```
opentelemetry-distro==0.43b0
opentelemetry-exporter-otlp==1.22.0
opentelemetry-instrumentation-fastapi==0.43b0
opentelemetry-instrumentation-pymongo==0.43b0
```

## Viewing Traces in PlayerZero

1. Navigate to [PlayerZero Dashboard](https://playerzero.ai)
2. Go to **Traces** or **APM** section
3. Filter by service name:
   - `nodejs-monolithic-app`
   - `python-monolithic-app`
4. View request traces, latency, errors, and dependencies

## Troubleshooting

### Traces Not Appearing

**Check logs:**
```bash
docker-compose logs nodejs-app | grep -i "telemetry\|otlp\|error"
docker-compose logs python-app | grep -i "telemetry\|otlp\|error"
```

**Common issues:**

1. **Missing API key:**
   ```
   Error: PLAYERZERO_API_KEY environment variable not set
   ```
   Solution: Add API key to `.env` file

2. **Network connectivity:**
   ```
   Error: Failed to connect to otlp.playerzero.app
   ```
   Solution: Check firewall, VPN, or proxy settings

3. **Invalid endpoint:**
   ```
   Error: 401 Unauthorized
   ```
   Solution: Verify API key is correct and active

### Disable Telemetry (Development)

To run without telemetry:

```bash
# Option 1: Remove API key from .env
PLAYERZERO_API_KEY=

# Option 2: Override endpoint to localhost (no-op)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

### Test Telemetry Locally

Use a local OTLP collector for testing:

```bash
# Run Jaeger with OTLP support
docker run -d \
  -p 4318:4318 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Update .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# View traces at http://localhost:16686
```

## Custom Instrumentation

### Node.js

```javascript
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('my-service');

async function myFunction() {
    const span = tracer.startSpan('myFunction');
    try {
        // Your code here
        span.setAttribute('custom.attribute', 'value');
    } finally {
        span.end();
    }
}
```

### Python

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def my_function():
    with tracer.start_as_current_span("my_function") as span:
        span.set_attribute("custom.attribute", "value")
        # Your code here
```

## Performance Impact

OpenTelemetry adds minimal overhead:

- **CPU**: < 5% increase
- **Memory**: ~10-20 MB per service
- **Latency**: < 1ms per request

Traces are batched and exported asynchronously to avoid blocking requests.

## Security

- API keys are passed via environment variables (never hardcoded)
- Traces are sent over HTTPS (TLS encrypted)
- Sensitive data (passwords, tokens) are NOT captured in traces
- Configure span attribute filtering if needed

## Support

For issues related to:

- **OpenTelemetry setup**: Check this documentation
- **PlayerZero integration**: Contact [PlayerZero Support](https://playerzero.ai/support)
- **Application bugs**: Open an issue in this repository

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [PlayerZero Documentation](https://docs.playerzero.ai)
- [OTLP Specification](https://opentelemetry.io/docs/specs/otlp/)
