# coding: utf-8

import six

from jaeger_client import Config

# Name of the HTTP header used to encode trace ID
DEFAULT_TRACE_ID_HEADER = 'trace_id' if six.PY3 else b'trace_id'


def init_tracer(service_name: str, config: dict):
    """
    initialize the global tracer
    :param service_name:
    :param config:
    :return:
    """
    assert isinstance(config, dict)
    # default use `trace_id` replace jaeger `uber-trace-id`
    config['trace_id_header'] = config.get('trace_id_header',
                                           DEFAULT_TRACE_ID_HEADER)

    config = Config(config=config, service_name=service_name, validate=True)

    # this call also sets opentracing.tracer
    return config.initialize_tracer()
