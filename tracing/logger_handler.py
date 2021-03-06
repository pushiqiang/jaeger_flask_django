# coding: utf-8
import datetime
import logging
from logging import Handler

import opentracing

from tracing import tags


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
            operation_name = 'logger[{}]'.format(record.name)
            parent_span = opentracing.tracer.active_span
            if not parent_span:
                return
            with opentracing.tracer.start_span(operation_name, child_of=parent_span) as logger_span:
                logger_span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_LOG)
                logger_span.set_tag(tags.LOGGER, record.name)

                logger_span.log_kv({
                    'event': tags.LOG_ERROR,
                    'message': msg,
                    'log.stack_info': record.stack_info,
                    'log.asctime': getattr(record, 'asctime', datetime.datetime.now()),
                    'log.created': record.created,
                    'log.filename': record.filename,
                    'log.funcName': record.funcName,
                    'log.levelname': record.levelname,
                    'log.lineno': record.lineno,
                    'log.module': record.module,
                    'log.msecs': record.msecs,
                    'log.name': record.name,
                    'log.pathname': record.pathname,
                    'log.process': record.process,
                    'log.thread': record.thread
                })
        except Exception as e:
            self.handleError(record)
