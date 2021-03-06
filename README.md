# 
https://www.jianshu.com/p/fbedfcdea606
https://github.com/jaegertracing/jaeger

# Usage

## in django

### tacing all request by middleware
#### settings.py add config
```
MIDDLEWARE = [
    'tracing.django.middleware.OpenTracingMiddleware',
    ...
]

SERVICE_NAME = 'service_a'

OPENTRACING_TRACER_CONFIG = {
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

```

#### after server running:

```python
import logging
from opentracing_instrumentation.client_hooks.requests import install_patches

from tracing.logger_handler import ErrorTraceHandler

install_patches()

logging.getLogger('').handlers = [logging.StreamHandler(), ErrorTraceHandler()]
logger = logging.getLogger(__name__)
```

### tacing some request by decorator
```python
import logging

import requests
from django.http import JsonResponse
from opentracing_instrumentation.client_hooks.requests import install_patches

from tracing import init_tracer
from tracing.django import trace
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

tracer = init_tracer('service_b', trace_config)
install_patches()


@trace(tracer)
def error(request):
    try:
        response = requests.get('http://service_c:5000/error/')
    except Exception as e:
        logger.error('call service_c fail')
        raise e
    return JsonResponse(response.json())

```


## in flask

### tacing all request by middleware
```python
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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

```


### tacing some request by decorator
```python
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

    response = requests.get('http://172.21.0.3:5000/error/')
    return jsonify(response.json())


@app.route('/good/')
@trace(tracer)
def good():
    logger.info('service good')
    response = requests.get('http://172.21.0.3:5000/good/')
    return jsonify(response.json())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

```