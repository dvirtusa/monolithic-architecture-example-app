import os
import logging

logger = logging.getLogger(__name__)

def setup_telemetry():
    """Initialize OpenTelemetry tracing, logging, and metrics.
    
    Telemetry is optional and failures are handled gracefully.
    Set OTEL_ENABLED=false to disable telemetry entirely.
    """
    
    otel_enabled = os.getenv('OTEL_ENABLED', 'true').lower() == 'true'
    
    if not otel_enabled:
        logger.info("OpenTelemetry disabled (OTEL_ENABLED=false)")
        return None
    
    try:
        from opentelemetry import trace, metrics
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.semconv.resource import ResourceAttributes
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
    except ImportError as e:
        logger.warning(f"OpenTelemetry packages not available: {e}")
        return None
    
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'https://sdk.playerzero.app/otlp')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'My Dataset Name')
    environment = os.getenv('OTEL_ENVIRONMENT', 'development')
    
    otlp_headers = {
        'Authorization': 'Bearer 697853e8466deb4c15041e24',
        'X-PzProd': 'true',
    }
    
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
    })
    
    try:
        # Traces
        trace_provider = TracerProvider(resource=resource)
        trace_exporter = OTLPSpanExporter(
            endpoint=f"{otlp_endpoint}/v1/traces",
            headers=otlp_headers,
            timeout=5,
        )
        trace_provider.add_span_processor(BatchSpanProcessor(
            trace_exporter,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        ))
        trace.set_tracer_provider(trace_provider)
        
        # Logs
        log_exporter = OTLPLogExporter(
            endpoint=f"{otlp_endpoint}/v1/logs",
            headers=otlp_headers,
            timeout=5,
        )
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(
            log_exporter,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        ))
        set_logger_provider(logger_provider)
        
        # Metrics
        metric_exporter = OTLPMetricExporter(
            endpoint=f"{otlp_endpoint}/v1/metrics",
            headers=otlp_headers,
            timeout=5,
        )
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter,
            export_interval_millis=60000,
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        
        # Auto-instrumentation
        FastAPIInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        PymongoInstrumentor().instrument()
        
        logger.info("OpenTelemetry initialized successfully")
        logger.info(f"Service: {service_name}")
        logger.info(f"Environment: {environment}")
        logger.info(f"OTLP Endpoint: {otlp_endpoint}")
        logger.info("Exporters: traces, logs, metrics")
        
        return trace_provider
        
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry: {e}")
        logger.warning("Application will continue without telemetry")
        return None


def suppress_otel_errors():
    """Suppress noisy OpenTelemetry export errors in logs."""
    logging.getLogger("opentelemetry.sdk.trace.export").setLevel(logging.CRITICAL)
    logging.getLogger("opentelemetry.sdk._logs.export").setLevel(logging.CRITICAL)
    logging.getLogger("opentelemetry.sdk.metrics.export").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)
