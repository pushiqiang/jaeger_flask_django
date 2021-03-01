import logging
from flask import g, request

import opentracing
from opentracing.ext import tags

from jaeger_client import Config


def init_tracer(service_name):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': 'jaeger',
                # 'reporting_port': 'your-reporting-port',
            },
            'logging': True,
        },
        service_name=service_name,
        validate=True,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


def before_request_trace(tracer):
    """
    trace flask request

    eg:
        @app.before_request
        def start_trace():
            before_request_trace(tracer)

    """
    operation_name = request.endpoint
    headers = {}
    for k, v in request.headers:
        headers[k.lower()] = v

    try:
        span_ctx = tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
        scope = tracer.start_active_span(operation_name, child_of=span_ctx)
    except (opentracing.InvalidCarrierException,
            opentracing.SpanContextCorruptedException):
        scope = tracer.start_active_span(operation_name)

    span = scope.span
    span.set_tag(tags.COMPONENT, 'Flask')
    span.set_tag(tags.HTTP_METHOD, request.method)
    span.set_tag(tags.HTTP_URL, request.base_url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)

    g.scope = scope


def after_request_trace(response=None, error=None):
    """
    eg:
        @app.after_request
        def end_trace(response):
            after_request_trace(response)
            return response

        @app.teardown_request
        def end_trace_with_error(error):
            if error is not None:
                after_request_trace(error=error)

    or:
        class APIBaseView(MethodView):
            def dispatch_request(self, *args, **kwargs):
                before_request_trace(tracer)
                try:
                    response = super(APIBaseView, self).dispatch_request(*args, **kwargs)
                except Exception as e:
                    after_request_trace(error=e)
                    raise e
                else:
                    after_request_trace(response)
                    return response
    """
    scope = getattr(g, 'scope', None)
    if not scope:
        return

    if response is not None:
        scope.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
    if error is not None:
        scope.span.set_tag(tags.ERROR, True)
        scope.span.log_kv({
            'event': tags.ERROR,
            'error.object': error,
            'request.args': request.args,
            'request.data': request.data
        })

    scope.close()


def trace(tracer):
    """
    Function decorator that traces functions

    NOTE: Must be placed after the @app.route decorator

    eg:
        @app.route('/log')
        @trace(tracer) # Indicate that /log endpoint should be traced
        def log():
            pass

    """
    def decorator(view_func):
        def wrapper(*args, **kwargs):
            before_request_trace(tracer)
            try:
                response = view_func(*args, **kwargs)
            except Exception as e:
                after_request_trace(error=e)
                raise
            else:
                after_request_trace(response)

            return response

        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator