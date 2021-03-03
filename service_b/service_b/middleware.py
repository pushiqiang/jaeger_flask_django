from django.conf import settings

from .tracing import before_request_trace, after_request_trace

try:
    # Django >= 1.10
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class OpenTracingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        """
         __init__() is only called once, no arguments, when the Web server
        responds to the first request
        """
        self._init_tracing()
        self.get_response = get_response

    def _init_tracing(self):
        self._tracer_callable = settings.OPENTRACING_TRACER_CALLABLE
        self.tracer = self._tracer_callable()

    def process_view(self, request, view_func, view_args, view_kwargs):
        before_request_trace(self.tracer, request, view_func)

    def process_exception(self, request, exception):
        after_request_trace(request, error=exception)

    def process_response(self, request, response):
        after_request_trace(request, response=response)
        return response
