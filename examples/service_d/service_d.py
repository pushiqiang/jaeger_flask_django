import logging

from flask import Flask, jsonify
from tracing import init_tracer
from tracing.flask import trace
from tracing.logger_handler import LogTraceHandler

logging.getLogger('').handlers = [logging.StreamHandler(), LogTraceHandler()]
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

init_tracer('service_d', trace_config)


@app.route('/error/')
@trace()
def error():
    raise Exception('service d raise a exception.')


@app.route('/good/')
@trace()
def good():
    data = {'service_d': 'good'}
    logger.error('log service_d some error')
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
