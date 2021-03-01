import requests
from flask import Flask, jsonify
from opentracing_instrumentation.client_hooks.requests import install_patches

from .tracing import init_tracer, trace


app = Flask(__name__)
tracer = init_tracer('formatter')
install_patches()


@app.route('/d/')
@trace(tracer)
def index():
    raise Exception


if __name__ == '__main__':
    app.debug = True
    app.run()
