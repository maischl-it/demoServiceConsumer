import os
import threading
import time
import requests
from flask import Flask

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter,BatchSpanProcessor

app=None

metricsValue = 0

def decrement_metrics():
    global metricsValue

    while True:
        if (metricsValue > 0):
            metricsValue -= 1

        time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=decrement_metrics).start()

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )

    tracer=trace.get_tracer(__name__)

    app = Flask(__name__)

    FlaskInstrumentor().instrument_app(app)

    app.run(host='0.0.0.0', port=3001)


@app.route("/", methods=['POST', 'GET'])
def home():
    global metricsValue
    metricsValue += 1

    url = os.environ.get("url", "http://172.17.0.4:3000/")
    response = requests.get(url)
    content = str(response.content)

    return "Response: "+content


@app.route("/metrics", methods=['POST', 'GET'])
def metrics():
    return '{"value":' + str(metricsValue) + '}'
