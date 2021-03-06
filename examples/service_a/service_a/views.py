import logging

import requests
from django.http import JsonResponse
from opentracing_instrumentation.client_hooks.requests import install_patches

from tracing.logger_handler import ErrorTraceHandler

install_patches()

logging.getLogger('').handlers = [logging.StreamHandler(), ErrorTraceHandler()]
logger = logging.getLogger(__name__)


def error(request):
    try:
        response = requests.get('http://service_b:5000/error/')
    except Exception as e:
        logger.error('call service_b fail')
        raise e
    return JsonResponse(response.json())


def good(request):
    response = requests.get('http://service_b:5000/good/')
    logger.error('logger.error test')
    return JsonResponse(response.json())
