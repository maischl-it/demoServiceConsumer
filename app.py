from flask import Flask
import requests
import os
import threading
import time

app = Flask(__name__)

metricsValue = 0


@app.route("/", methods=['POST', 'GET'])
def home():
    global metricsValue
    metricsValue += 1

    url = os.environ.get("url", "http://provider.default.svc.cluster.local")
    response = requests.get(url)
    content = str(response.content)

    return "Response: "+content


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

    app.run(host='0.0.0.0', port=3001)
