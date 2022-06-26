from flask import Flask
import requests
import os

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def home():

    url = os.environ.get("url", "http://provider.default.svc.cluster.local")
    # response = requests.get("http://127.0.0.1:3000")
    response = requests.get(url)
    content = str(response.content)

    return "Response: "+content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
