# coding: utf-8
import datetime
import logging
import opentracing

from tracing import tags


class LogTraceHandler(logging.Handler):
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
                # ref: https://docs.python.org/zh-cn/3/library/logging.html#logrecord-attributes
                logger_span.log_kv({
                    'log.content': msg,
                    'log.level': record.levelname,
                    'log.time': getattr(record, 'asctime', datetime.datetime.now()),
                    'log.pathname': record.pathname,
                    'log.lineno': record.lineno,
                    'log.process': record.process,
                    'log.thread': record.thread,
                    'log.stack_info': record.stack_info,
                })
        except Exception as e:
            self.handleError(record)
