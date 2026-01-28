const otelEnabled = process.env.OTEL_ENABLED !== 'false';

if (!otelEnabled) {
    console.log('OpenTelemetry disabled (OTEL_ENABLED=false)');
    module.exports = { shutdown: () => Promise.resolve() };
    return;
}

let sdk;

try {
    const { NodeSDK } = require('@opentelemetry/sdk-node');
    const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
    const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
    const { OTLPLogExporter } = require('@opentelemetry/exporter-logs-otlp-http');
    const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
    const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
    const { Resource } = require('@opentelemetry/resources');
    const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
    const { SimpleLogRecordProcessor } = require('@opentelemetry/sdk-logs');
    const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');

    // Suppress verbose OpenTelemetry logs (only show errors)
    diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.ERROR);

    const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'https://sdk.playerzero.app/otlp';
    const serviceName = process.env.OTEL_SERVICE_NAME || 'My Dataset Name';
    const environment = process.env.OTEL_ENVIRONMENT || 'development';

    const otlpHeaders = {
        'Authorization': 'Bearer 697853e8466deb4c15041e24',
        'X-PzProd': 'true',
    };

    const traceExporter = new OTLPTraceExporter({
        url: `${otlpEndpoint}/v1/traces`,
        headers: otlpHeaders,
        timeoutMillis: 5000,
    });

    const logExporter = new OTLPLogExporter({
        url: `${otlpEndpoint}/v1/logs`,
        headers: otlpHeaders,
        timeoutMillis: 5000,
    });

    const metricExporter = new OTLPMetricExporter({
        url: `${otlpEndpoint}/v1/metrics`,
        headers: otlpHeaders,
        timeoutMillis: 5000,
    });

    sdk = new NodeSDK({
        resource: new Resource({
            [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
            [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
            [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: environment,
        }),
        traceExporter,
        logRecordProcessor: new SimpleLogRecordProcessor(logExporter),
        metricReader: new PeriodicExportingMetricReader({
            exporter: metricExporter,
            exportIntervalMillis: 60000,
        }),
        instrumentations: [
            getNodeAutoInstrumentations({
                '@opentelemetry/instrumentation-fs': {
                    enabled: false,
                },
            }),
        ],
    });

    sdk.start();
    console.log('OpenTelemetry initialized successfully');
    console.log(`Service: ${serviceName}`);
    console.log(`Environment: ${environment}`);
    console.log(`OTLP Endpoint: ${otlpEndpoint}`);
    console.log('Exporters: traces, logs, metrics');

} catch (error) {
    console.warn(`Failed to initialize OpenTelemetry: ${error.message}`);
    console.warn('Application will continue without telemetry');
    sdk = null;
}

process.on('SIGTERM', () => {
    if (sdk) {
        sdk.shutdown()
            .then(() => console.log('Tracing terminated'))
            .catch((error) => console.log('Error terminating tracing', error))
            .finally(() => process.exit(0));
    } else {
        process.exit(0);
    }
});

module.exports = { shutdown: () => sdk ? sdk.shutdown() : Promise.resolve() };
