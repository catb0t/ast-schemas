# -*- coding: utf-8 -*-
"""Decorator registry for the syntax machinery.

This is used to support decorated lambdas (chains of ``Call`` nodes terminating
in a ``Lambda``), since some decorators must be applied in a particular order.

Especially the ``tco`` and ``continuations`` macros use this.
"""

# This module is kept separate from unpythonic.syntax.util simply to make
# the MacroPy dependency optional. If the user code doesn't use macros,
# the decorator registry gets populated at startup as usual, and then sits idle.

from heapq import heappush

# Idea shamelessly stolen from MacroPy's macro registry.
decorator_registry = []
tco_decorators = set()
def register_decorator(priority=0.0, istco=False):
    """Decorator that registers a custom decorator for the syntax machinery.

    Unknown decorators cannot be reordered robustly, hence ``sort_lambda_decorators``
    only sorts known decorators, i.e. those registered via this function.

    Usage::

        @register_decorator(priority=100)
        def mydeco(f):
            ...

    The final result is still ``mydeco``, with the side effect that it is
    registered as a known decorator with the given priority value.

    priority: number (float is ok; nominal range 0..100). The smallest number
    is the outermost decorator, largest the innermost.

    tco: set this to True when registering a decorator that applies TCO.

    The TCO flag is basically only needed by the ``tco`` and ``fploop`` modules.
    It exists because the ``tco`` macro needs to know whether a given function
    already has TCO applied to it (so that it won't be applied twice).
    """
    def register(f):
        heappush(decorator_registry, (priority, f.__name__))
        if istco:
            tco_decorators.add(f.__name__)
        return f
    return register
