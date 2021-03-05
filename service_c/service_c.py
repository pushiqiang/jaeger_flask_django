import requests
from opentracing_instrumentation.client_hooks.requests import install_patches

from flask import Flask, jsonify
from tracing import init_tracer
from tracing.flask import after_request_trace, before_request_trace

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

tracer = init_tracer('service_c', trace_config)
install_patches()


@app.before_request
def start_trace():
    before_request_trace(tracer)


@app.after_request
def end_trace(response):
    after_request_trace(response)
    return response


@app.teardown_request
def end_trace_with_error(e):
    if error is not None:
        after_request_trace(error=e)


@app.errorhandler(Exception)
def exception_trace(e):
    after_request_trace(error=e)
    raise e


@app.route('/error/')
def error():
    response = requests.get('http://service_d:5000/error/')
    return jsonify(response.json())


@app.route('/good/')
def success():
    response = requests.get('http://service_d:5000/good/')
    return jsonify(response.json())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
