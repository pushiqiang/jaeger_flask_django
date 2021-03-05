# coding: utf-8
import datetime
import logging
import opentracing
from opentracing.ext import tags

from logging import Handler


SPAN_KIND_LOGGER = 'logger'
LOGGER = 'logger'
LOGGER_ERROR = 'logger.error'
ERROR_MESSAGE = 'error.message'


logger = logging.getLogger('jaeger_tracing')


class ErrorTraceHandler(Handler):
    """
    Custom StreamHandler implementation to forward python logger records to Jaeger / OpenTracing
    """
    def __init__(self, level=logging.ERROR):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            operation_name = 'logger[{}]:{}:{}'.format(record.name, record.funcName, record.lineno)
            with opentracing.tracer.start_span(operation_name,
                                               child_of=opentracing.tracer.active_span) as logger_span:

                logger_span.set_tag(tags.SPAN_KIND, LOGGER)
                logger_span.set_tag(LOGGER, record.name)

                logger_span.log_kv({
                    'event': 'logger.error',
                    'message': msg,
                    'error.stack_info': record.stack_info,
                    'error.asctime': getattr(record, 'asctime', datetime.datetime.now()),
                    'error.created': record.created,
                    'error.filename': record.filename,
                    'error.funcName': record.funcName,
                    'error.levelname': record.levelname,
                    'error.lineno': record.lineno,
                    'error.module': record.module,
                    'error.msecs': record.msecs,
                    'error.name': record.name,
                    'error.pathname': record.pathname,
                    'error.process': record.process,
                    'error.thread': record.thread
                })
        except Exception as e:
            self.handleError(record)
