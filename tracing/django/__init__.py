import opentracing
import six

from tracing import tags


def format_request_headers(request_meta):
    headers = {}
    for k, v in six.iteritems(request_meta):
        k = k.lower().replace('_', '-')
        if k.startswith('http-'):
            k = k[5:]
            headers[k] = v
        # TODO feature
    return headers


def format_hex_trace_id(trace_id: int):
    return '{:x}'.format(trace_id)


def before_request_trace(tracer, request, view_func):
    """
    Helper function to avoid rewriting for middleware and decorator.
    Returns a new span from the request with logged attributes and
    correct operation name from the view_func.
    """
    # strip headers for trace info
    headers = format_request_headers(request.META)

    # start new span from trace info
    operation_name = view_func.__name__
    try:
        span_ctx = tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
        scope = tracer.start_active_span(operation_name, child_of=span_ctx)
    except (opentracing.InvalidCarrierException,
            opentracing.SpanContextCorruptedException):
        scope = tracer.start_active_span(operation_name)

    span = scope.span
    span.set_tag(tags.COMPONENT, 'Django')
    span.set_tag(tags.TRACE_ID, format_hex_trace_id(span.trace_id))
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)
    span.set_tag(tags.HTTP_METHOD, request.method)
    span.set_tag(tags.HTTP_URL, request.get_full_path())

    request_id = headers.get(tags.REQUEST_ID)
    if request_id:
        span.set_tag(tags.REQUEST_ID, request_id)

    request.scope = scope

    return scope


def after_request_trace(request, response=None, error=None):
    scope = getattr(request, 'scope', None)

    if scope is None:
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
            'request.headers': format_request_headers(request.META),
            'request.args': request.GET,
            'request.data': request.POST
        })

    scope.close()


def trace(tracer):
    """
    Function decorator that traces functions such as Views
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            before_request_trace(tracer, request, view_func)
            try:
                response = view_func(request, *args, **kwargs)
            except Exception as e:
                after_request_trace(request, error=e)
                raise e
            else:
                after_request_trace(request, response)

            return response

        wrapper.__name__ = view_func.__name__
        return wrapper

    return decorator
