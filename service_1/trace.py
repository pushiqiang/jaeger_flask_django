import logging
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
                'reporting_host': 'your-reporting-host',
                'reporting_port': 'your-reporting-port',
            },
            'logging': True,
        },
        service_name=service_name,
        validate=True,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()
