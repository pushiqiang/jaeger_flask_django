import opentracing

from flask import g, request
from tracing import tags


def format_hex_trace_id(trace_id: int):
    return '{:x}'.format(trace_id)


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
    span.set_tag(tags.TRACE_ID, format_hex_trace_id(span.trace_id))
    span.set_tag(tags.HTTP_METHOD, request.method)
    span.set_tag(tags.HTTP_URL, request.base_url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)

    request_id = headers.get(tags.REQUEST_ID)
    if request_id:
        span.set_tag(tags.REQUEST_ID, request_id)

    g.scope = scope
    return scope


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
            'error.kind': type(error),
            'error.object': error,
            'error.stack': error.__traceback__,
            'request.headers': request.headers,
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
                raise e
            else:
                after_request_trace(response)

            return response

        wrapper.__name__ = view_func.__name__
        return wrapper

    return decorator
