import importlib
import inspect
import logging
import pkgutil
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision

from insight_engine.config import ConfigLoader
from insight_engine.middleware.fraudio_middleware import FraudioMiddleware

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()


class FraudioTracingSampler(Sampler):
    def __init__(self, delegate_sampler):
        self.delegate_sampler = delegate_sampler

    def get_description(self):
        return self.__class__.__name__

    def should_sample(
            self,
            parent_context,
            trace_id: int,
            name: str,
            kind=None,
            attributes=None,
            links=None,
            trace_state=None
    ):
        if attributes and 'http.target' in attributes:
            path = attributes['http.target']
        else:
            # Do not make traces unless the root span is related to an HTTP request
            return SamplingResult(Decision.DROP)

        if len(path) == 0 or path in FraudioMiddleware.WHITELISTED_URLS or \
                path.startswith(FraudioMiddleware.WHITELISTED_URL_PREFIXES):
            return SamplingResult(Decision.DROP)

        return self.delegate_sampler.should_sample(
            parent_context,
            trace_id,
            name,
            kind,
            attributes,
            links,
            trace_state
        )


# In order to have meaningful traces without polluting the code, we have this heuristic to find important high-level
#   coroutines to trace. The expectation is that this is sufficient (and not overkill) to have useful traces.
def trace_functions_in_module(module):
    tracer = trace.get_tracer(__name__)
    module_name = module.__name__

    # Process async functions and classes in the module
    def _decorate_module_members(target_module, target_module_name):
        for member_name, member in inspect.getmembers(target_module):
            if (inspect.isfunction(member) and
                    not member_name.startswith('_') and
                    member.__module__ == target_module_name):
                full_name = f"{target_module_name}.{member_name}"
                wrapper = (
                    _wrap_async_with_trace(member, full_name, tracer)
                    if inspect.iscoroutinefunction(member)
                    else _wrap_with_trace(member, full_name, tracer)
                )
                setattr(target_module, member_name, wrapper)
            elif (inspect.isclass(member) and
                  not member_name.startswith('_') and
                  member.__module__ == target_module_name):
                for method_name, method in inspect.getmembers(member, predicate=inspect.isfunction):
                    if not method_name.startswith('_') and method.__module__ == target_module_name:
                        full_name = f"{target_module_name}.{member_name}.{method_name}"
                        wrapper = (
                            _wrap_async_with_trace(method, full_name, tracer)
                            if inspect.iscoroutinefunction(method)
                            else _wrap_with_trace(method, full_name, tracer)
                        )
                        setattr(member, method_name, wrapper)

    # Process the requested module
    _decorate_module_members(module, module_name)

    # Process immediate submodules (files) within the requested module
    if hasattr(module, '__path__'):
        for finder, submodule_name, is_pkg in pkgutil.iter_modules(module.__path__):
            if not submodule_name.startswith('_'):
                full_submodule_name = f"{module_name}.{submodule_name}"
                submodule = importlib.import_module(full_submodule_name)
                _decorate_module_members(submodule, full_submodule_name)


def _wrap_with_trace(func, name, tracer):
    @wraps(func)
    def traced_func(*args, **kwargs):
        with tracer.start_as_current_span(name):
            return func(*args, **kwargs)
    return traced_func


def _wrap_async_with_trace(func, name, tracer):
    @wraps(func)
    async def traced_func(*args, **kwargs):
        with tracer.start_as_current_span(name):
            return await func(*args, **kwargs)
    return traced_func
