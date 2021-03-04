# coding: utf-8

import logging
import opentracing
from opentracing.ext import tags

from logging import StreamHandler


SPAN_KIND_LOGGER = 'logger'
LOGGER_ERROR = 'logger.error'
ERROR_MESSAGE = 'error.message'


logger = logging.getLogger('jaeger_tracing')


class TraceErrorHandler(StreamHandler):
    """
    Custom StreamHandler implementation to forward python logger records to Jaeger / OpenTracing
    """

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

        if record.levelno == logging.ERROR:
            try:
                with opentracing.tracer.start_span(record.funcName,
                                                   child_of=opentracing.tracer.active_span) as logger_span:

                    logger_span.set_tag(tags.COMPONENT, 'Flask')
                    logger_span.set_tag(tags.SPAN_KIND, SPAN_KIND_LOGGER)

                    logger_span.log_kv({
                        'event': 'logger.error',
                        'error.message': msg,
                        'error.stack': record.stack_info,
                    })
            except Exception:
                pass
