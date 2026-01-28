# OpenTelemetry Integration with PlayerZero

This project is instrumented with OpenTelemetry to export traces to PlayerZero for observability and monitoring.

## Overview

Both the Node.js and Python applications are configured to automatically capture and export telemetry data including:

- **Traces**: Request/response flows, database queries, external HTTP calls
- **Logs**: Application logs exported via OTLP
- **Metrics**: Application metrics exported via OTLP
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
OTEL_EXPORTER_OTLP_ENDPOINT=https://sdk.playerzero.app/otlp
OTEL_SERVICE_NAME=My Dataset Name
ENVIRONMENT=production
```

**Note:** Authorization headers are preconfigured in the tracing files.

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
nodejs-app  | Service: My Dataset Name
nodejs-app  | Environment: docker
nodejs-app  | OTLP Endpoint: https://sdk.playerzero.app/otlp
nodejs-app  | Exporters: traces, logs, metrics

python-app  | OpenTelemetry tracing initialized
python-app  | Service: My Dataset Name
python-app  | Environment: docker
python-app  | OTLP Endpoint: https://sdk.playerzero.app/otlp
python-app  | Exporters: traces, logs, metrics
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_ENABLED` | Enable/disable telemetry | `true` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint URL | `https://sdk.playerzero.app/otlp` |
| `OTEL_SERVICE_NAME` | Service/dataset name | `My Dataset Name` |
| `OTEL_ENVIRONMENT` | Deployment environment | `development` |

### Preconfigured Headers

Authorization headers are hardcoded in the tracing configuration files:

```
Authorization: Bearer 697853e8466deb4c15041e24
X-PzProd: true
```

### Exporters

All three OTLP exporters are enabled:
- **Traces**: `otel.traces.exporter=otlp`
- **Logs**: `otel.logs.exporter=otlp`
- **Metrics**: `otel.metrics.exporter=otlp`

These export to the PlayerZero OTLP endpoint for unified observability.

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
  "@opentelemetry/sdk-logs": "^0.45.1",
  "@opentelemetry/sdk-metrics": "^1.19.0",
  "@opentelemetry/auto-instrumentations-node": "^0.40.3",
  "@opentelemetry/exporter-trace-otlp-http": "^0.45.1",
  "@opentelemetry/exporter-logs-otlp-http": "^0.45.1",
  "@opentelemetry/exporter-metrics-otlp-http": "^0.45.1"
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
   - `My Dataset Name` (or your configured `OTEL_SERVICE_NAME`)
4. View request traces, latency, errors, and dependencies

## Troubleshooting

### Traces Not Appearing

**Check logs:**
```bash
docker-compose logs nodejs-app | grep -i "telemetry\|otlp\|error"
docker-compose logs python-app | grep -i "telemetry\|otlp\|error"
```

**Common issues:**

1. **Network connectivity:**
   ```
   Error: Failed to connect to sdk.playerzero.app
   ```
   Solution: Check firewall, VPN, or proxy settings

2. **Invalid authorization:**
   ```
   Error: 401 Unauthorized
   ```
   Solution: Verify the authorization headers in tracing.js/tracing.py are correct

### Disable Telemetry

To completely disable telemetry:

```bash
OTEL_ENABLED=false
```

Alternatively, override the endpoint to localhost:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

### Graceful Failure Handling

Telemetry is optional and non-blocking:
- If the OTLP endpoint is unreachable, the application continues normally
- Export errors are suppressed to avoid log noise
- Shorter timeouts (5s) prevent slow startup

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

- Authorization headers are configured in the tracing files
- Traces, logs, and metrics are sent over HTTPS (TLS encrypted)
- Sensitive data (passwords, tokens) are NOT captured in telemetry
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
