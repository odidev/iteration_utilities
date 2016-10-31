# Built-ins
from __future__ import absolute_import, division, print_function
import collections
import gc
import weakref

# This module
import iteration_utilities

if iteration_utilities.PY2:
    range = xrange


def _make_tuple(obj):
    if obj is None:
        return tuple()
    if not isinstance(obj, tuple):
        return (obj, )
    else:
        return obj


def memory_leak_decorator(specific_object=None, exclude_object=weakref.ref,
                          collect=False, offset=0):
    """Compares the number of tracked python objects before and after a
    function call and returns a dict containing differences.

    Parameters
    ----------
    func : callable or None, optional
        The function that should be tested. Should be `None` if the function
        is used as a decorator _if_ it should also accept `specific_object` or
        `exclude_object`.
        Default is `None`.

    specific_object : type, tuple of types, None, optional
        Test all tracked types (if it's ``None``) or only the specific type(s).
        Default is ``None``.

    exclude_object : type, tuple of types, None, optional
        Exclude specific type(s) or use all (if it's ``None``).
        Default is ``weakref.ref``.

    collect : bool, optional
        If ``True`` remove cyclic references by calling ``gc.collect`` after
        the function call.
        Default is ``False``.

    offset : int, optional
        Call the function `offset` times before doing the check for a memory
        leak. If the function is unpure (relies on external states) calls might
        introduce some "wanted" memory leaks.
        Default is ``0``.

    Returns
    -------
    difference : collections.Counter
        A Counter containing the types after the function call minus the ones
        before the function call. If the function doesn't return anything this
        Counter should be empty. If it contains types the function probably
        contains a memory leak.

    Notes
    -----
    It is convenient to wrap the explicit call inside a function that doesn't
    return. To enhance this useage the ``memory_leak`` function doesn't allow
    to pass arguments to the ``func``!
    """
    def decorator_factory(func):
        def inner():
            for i in range(offset):
                func()

            # Create Counter before listing the objects otherwise they would
            # be recognized as leak.
            before = collections.Counter()
            after = collections.Counter()

            # Tracked objects before the function call
            before.update(map(type, gc.get_objects()))

            func()
            if collect:
                gc.collect()  # Takes care of cyclic references!

            # Tracked objects after the function call
            after.update(map(type, gc.get_objects()))

            specifics = _make_tuple(specific_object)
            if not specifics:
                specifics = set(after)
            excludes = set(_make_tuple(exclude_object))

            if any(after[specific] - before[specific] > 0
                   for specific in specifics
                   if specific not in excludes and
                   specific in before):
                raise TypeError('leaked objects: {}'.format(
                    {specific: after[specific] - before[specific]
                     for specific in specifics
                     if specific not in excludes and
                     after[specific] - before[specific] > 0}))
        return inner
    return decorator_factory
