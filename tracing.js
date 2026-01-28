const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPLogExporter } = require('@opentelemetry/exporter-logs-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { SimpleLogRecordProcessor } = require('@opentelemetry/sdk-logs');

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
});

const logExporter = new OTLPLogExporter({
    url: `${otlpEndpoint}/v1/logs`,
    headers: otlpHeaders,
});

const metricExporter = new OTLPMetricExporter({
    url: `${otlpEndpoint}/v1/metrics`,
    headers: otlpHeaders,
});

const sdk = new NodeSDK({
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
console.log('OpenTelemetry tracing initialized');
console.log(`Service: ${serviceName}`);
console.log(`Environment: ${environment}`);
console.log(`OTLP Endpoint: ${otlpEndpoint}`);
console.log('Exporters: traces, logs, metrics');

process.on('SIGTERM', () => {
    sdk.shutdown()
        .then(() => console.log('Tracing terminated'))
        .catch((error) => console.log('Error terminating tracing', error))
        .finally(() => process.exit(0));
});
