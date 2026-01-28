import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

logger = logging.getLogger(__name__)

def setup_telemetry():
    """Initialize OpenTelemetry tracing"""
    
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'python-app')
    environment = os.getenv('OTEL_ENVIRONMENT', 'development')
    api_key = os.getenv('PLAYERZERO_API_KEY', '')
    
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
    })
    
    provider = TracerProvider(resource=resource)
    
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{otlp_endpoint}/v1/traces",
        headers=headers,
    )
    
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    trace.set_tracer_provider(provider)
    
    FastAPIInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    
    logger.info("OpenTelemetry tracing initialized")
    logger.info(f"Service: {service_name}")
    logger.info(f"Environment: {environment}")
    logger.info(f"OTLP Endpoint: {otlp_endpoint}")
    
    return provider
