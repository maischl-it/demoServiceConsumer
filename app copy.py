import os
import threading
import time
import urllib
from flask import Flask

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor

from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

metricsValue = 0

app = Flask(__name__)
tracer=None

def decrement_metrics():
    global metricsValue

    while True:
        if (metricsValue > 0):
            metricsValue -= 1

        time.sleep(10)

@app.route("/", methods=['POST', 'GET'])
def home():
    global metricsValue
    metricsValue += 1
    content=None

    with tracer.start_as_current_span("rootSpanConsumer"):
        with tracer.start_as_current_span("childSpanConsumer"):
            # content = urllib.request.urlopen("http://172.17.0.4:3000/").read()
            content = urllib.request.urlopen("https://web.de").read()
            content = str(content)

    return "Response: "+content


@app.route("/metrics", methods=['POST', 'GET'])
def metrics():
    return '{"value":' + str(metricsValue) + '}'

if __name__ == '__main__':
    threading.Thread(target=decrement_metrics).start()

    trace.set_tracer_provider(TracerProvider())

    jaeger_exporter=JaegerExporter(
        agent_host_name="172.17.0.2",
        agent_port=6831
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    tracer=trace.get_tracer(__name__)

    # FlaskInstrumentor().instrument_app(app)
    URLLibInstrumentor().instrument()

    app.run(host='0.0.0.0', port=3001)