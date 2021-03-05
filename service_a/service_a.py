import logging
import requests
from flask import Flask, jsonify
from opentracing_instrumentation.client_hooks.requests import install_patches

from tracing import init_tracer, trace


app = Flask(__name__)
tracer = init_tracer('service_a')
install_patches()


logger = logging.getLogger(__name__)


@app.route('/a/')
@trace(tracer)
def index():
    data = {'name': 'service_a'}
    try:
        a = 2 / 0
    except Exception as e:
        logger.error('exception error', exc_info=True)
    logger.critical('critical error', exc_info=True)
    # data = requests.get('http://service_c:5000/c/')
    data = requests.get('http://172.21.0.2:5000/b/')
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
