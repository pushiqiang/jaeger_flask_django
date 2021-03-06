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


@trace(tracer)
def good(request):
    response = requests.get('http://service_c:5000/good/')
    logger.error('call service_c success')
    return JsonResponse(response.json())
