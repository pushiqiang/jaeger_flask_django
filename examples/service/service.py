import logging

import requests
from opentracing_instrumentation.client_hooks.requests import install_patches

from flask import Flask, jsonify
from tracing import init_tracer
from tracing.flask import trace
from tracing.logger_handler import ErrorTraceHandler

logging.getLogger('').handlers = [logging.StreamHandler(), ErrorTraceHandler()]
logger = logging.getLogger(__name__)

trace_config = {
    'sampler': {
        'type': 'const',
        'param': 1,
    },
    'local_agent': {
        'reporting_host': 'jaeger',
        # 'reporting_port': 'your-reporting-port',
    },
    'logging': True,
}

app = Flask(__name__)
tracer = init_tracer('service', trace_config)
install_patches()


@app.route('/error/')
@trace(tracer)
def error():
    try:
        a = 2 / 0
    except Exception as e:
        logger.error('exception error', exc_info=True)

    logger.critical('critical error', exc_info=True)

    response = requests.get('http://service_a:5000/error/')
    return jsonify(response.json())


@app.route('/good/')
@trace(tracer)
def good():
    logger.info('service good')
    response = requests.get('http://service_a:5000/good/')
    return jsonify(response.json())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
