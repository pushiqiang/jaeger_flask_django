import requests

from django.http import JsonResponse
from opentracing_instrumentation.client_hooks.requests import install_patches

from .tracing import init_tracer, trace

tracer = init_tracer('service_b')
install_patches()


@trace(tracer)
def hello(request):
    data = requests.get('http://service_c:5000/c/')
    return JsonResponse(data)
