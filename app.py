import flask
import requests
import threading
import time

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

metricsValue = 0

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
    global metricsValue
    metricsValue += 1

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("spanConsumer") as span:
        span.set_attribute("application","consumer")

        # requests.get("https://enaqbph6yivud.x.pipedream.net/")
        requests.get("http://provider-demoserviceprovider.demo.svc.cluster.local:3000")
        # requests.get("http://172.17.0.4:3000")
    
    # time.sleep(3)
    requests.get("https://maischl-it.de")

    return "consumer"

@app.route("/metrics", methods=['POST', 'GET'])
def metrics():
    return '{"value":' + str(metricsValue) + '}'

def decrement_metrics():
    global metricsValue

    while True:
        if (metricsValue > 0):
            metricsValue -= 1

        time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=decrement_metrics).start()

    app.run(host='0.0.0.0', port=5000)
