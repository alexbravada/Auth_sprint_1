from functools import wraps

from opentelemetry import trace


tracer = trace.get_tracer(__name__)


def trace(span_name: str = 'span_name'):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            with tracer.start_as_current_span(span_name):
                return fn(*args, **kwargs)

        return decorator

    return wrapper
