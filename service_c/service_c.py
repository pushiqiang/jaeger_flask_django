import requests
from flask import Flask, jsonify
from opentracing_instrumentation.client_hooks.requests import install_patches

from .tracing import init_tracer, trace


app = Flask(__name__)
tracer = init_tracer('service_c')
install_patches()


@app.route('/c/')
@trace(tracer)
def index():
    data = requests.get('service_d/d/')
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run()
