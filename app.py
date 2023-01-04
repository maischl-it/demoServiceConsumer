import flask
import requests
import time

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

tracer=TracerProvider(resource=Resource.create({SERVICE_NAME: "DemoConsumer"}))

trace.set_tracer_provider(tracer)

jaeger_exporter=JaegerExporter(
        agent_host_name="simplest-agent.default.svc.cluster.local",
        # agent_host_name="172.17.0.2",
        agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)


app = flask.Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/", methods=['POST', 'GET'])
def hello():
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("spanConsumer") as span:
        span.set_attribute("application","consumer")

        requests.get("http://provider-demoserviceprovider.demo.svc.cluster.local:3000")
        # requests.get("http://172.17.0.4:3000")
    
    # time.sleep(3)
    requests.get("https://maischl-it.de")

    return "consumer"


app.run(debug=True, host='0.0.0.0', port=5000)
