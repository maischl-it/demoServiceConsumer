import flask
import requests

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3Format
from opentelemetry.propagators.textmap import TextMapPropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

set_global_textmap(B3Format())

tracer=TracerProvider()

trace.set_tracer_provider(tracer)

jaeger_exporter=JaegerExporter(
        agent_host_name="172.17.0.3",
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

    with tracer.start_as_current_span("example-request") as span:
        span.set_attribute("customAttributeSEM","testsem")

        requests.get("http://172.17.0.4:3000")
    return "hello"


app.run(debug=True, port=5000)