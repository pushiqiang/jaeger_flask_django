import requests
from flask import Flask, jsonify
from opentracing_instrumentation.client_hooks.requests import install_patches

from .tracing import init_tracer, trace


app = Flask(__name__)
tracer = init_tracer('service_b')
install_patches()


@app.route('/b/')
@trace(tracer)
def index():
    data = requests.get('service_c:5000/c/')
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run()
