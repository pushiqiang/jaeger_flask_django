# Use jaeger - a Distributed Tracing System in flask and django development

# Usage

[blog](https://blog.csdn.net/pushiqiang/article/details/114449564)

## in django

### tracing all request by middleware
#### settings.py
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
        'reporting_port': 'your-reporting-port',
    },
    'logging': True,
}

```

### tracing specific request by decorator
#### 1: initialize a global tracer
```python
from tracing import init_tracer

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

```

#### 2: import tracer and decorator views

```python

from django.http import JsonResponse

from tracing.django import trace

# tracer: init_tracer('service_b', trace_config)
from example import tracer


@trace(tracer)
def error(request):
    data = {'name': 'error'}
    return JsonResponse(data)

```

## in flask

### tracing all request by middleware(flask request hook)
```python
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
        'reporting_port': 'your-reporting-port',
    },
    'logging': True,
}

tracer = init_tracer('service_c', trace_config)


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
    data = {'name': 'error'}
    return jsonify(data)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

```

### tracing specific request by decorator
```python
from flask import Flask, jsonify
from tracing import init_tracer
from tracing.flask import trace

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

@app.route('/error/')
@trace(tracer)
def error():
    data = {'name': 'error'}
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

```

## auto patch http client(auto inject span context)
```python
import requests
# only patch requests, or you can:
# from opentracing_instrumentation.client_hooks import install_all_patches
# install_all_patches()
from opentracing_instrumentation.client_hooks.requests import install_patches

install_patches()
# http request will bring the `trace_id` in headers
response = requests.get('http://service_d:5000/good/')
```

## auto tracing error logs
```python
import logging
from flask import jsonify

from tracing.flask import trace
from tracing.logger_handler import ErrorTraceHandler

from example import app, tracer

logging.getLogger('').handlers.add(ErrorTraceHandler())
logger = logging.getLogger(__name__)

@app.route('/error/')
@trace(tracer)
def error():
    try:
        data = 2 / 0
    except Exception as e:
        logger.error('exception error', exc_info=True)

    logger.critical('critical error', exc_info=True)

    return jsonify(data)

```
