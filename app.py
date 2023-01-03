import flask
import requests

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer=TracerProvider()

trace.set_tracer_provider(tracer)

jaeger_exporter=JaegerExporter(
        agent_host_name="simplest-agent.default.svc.cluster.local",
        agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)


app = flask.Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/")
def hello():
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("spanConsumer") as span:
        span.set_attribute("application","consumer")

        requests.get("http://provider-demoserviceprovider.demo.svc.cluster.local:3000")
    return "consumer"


app.run(debug=True, host='0.0.0.0', port=5000)
