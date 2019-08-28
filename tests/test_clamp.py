# Licensed under Apache License Version 2.0 - see LICENSE

# Built-ins
from __future__ import absolute_import, division, print_function
import operator
import pickle
import sys

# 3rd party
import pytest

# This module
import iteration_utilities

# Test helper
import helper_funcs as _hf
from helper_cls import T, toT


clamp = iteration_utilities.clamp


def test_clamp_empty1():
    assert list(clamp([], T(10), T(100))) == []


def test_clamp_normal1():
    assert list(clamp(toT(range(10)), T(2), T(7))) == toT([2, 3, 4, 5, 6, 7])


def test_clamp_normal2():
    # only low
    assert list(clamp(toT(range(10)), T(2))) == toT([2, 3, 4, 5, 6, 7, 8, 9])


def test_clamp_normal3():
    # only high
    assert list(clamp(toT(range(10)),
                      high=T(7))) == toT([0, 1, 2, 3, 4, 5, 6, 7])


def test_clamp_normal4():
    # both, inclusive
    assert list(clamp(toT(range(10)), low=T(2), high=T(7),
                      inclusive=True)) == toT([3, 4, 5, 6])


def test_clamp_normal5():
    # no low/high
    assert list(clamp(toT(range(10)))) == toT([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_clamp_normal6():
    # only low without remove
    assert list(clamp(toT(range(10)), T(2), remove=False)) == (
            toT([2, 2, 2, 3, 4, 5, 6, 7, 8, 9]))


def test_clamp_normal7():
    # only high without remove
    assert list(clamp(toT(range(10)), high=T(7),
                      remove=False)) == toT([0, 1, 2, 3, 4, 5, 6, 7, 7, 7])


def test_clamp_normal8():
    # both without remove
    assert list(clamp(toT(range(10)), low=T(2), high=T(7),
                      remove=False)) == toT([2, 2, 2, 3, 4, 5, 6, 7, 7, 7])


def test_clamp_normal9():
    # no low/high (given as None)
    assert list(clamp(toT(range(10)),
                      None, None)) == toT([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_clamp_attributes1():
    it = clamp(toT(range(5)), T(1))
    assert it.low == T(1)
    assert it.high is None
    assert it.remove
    assert not it.inclusive


def test_clamp_failure1():
    with pytest.raises(TypeError):
        list(clamp(toT(range(10)), T('a'), T(3)))


def test_clamp_failure2():
    with pytest.raises(TypeError):
        list(clamp(map(T, range(10)), T(3), T('a')))


def test_clamp_failure3():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP, match=_hf.FailNext.EXC_MSG):
        next(clamp(_hf.FailNext()))


def test_clamp_failure4():
    with pytest.raises(_hf.FailIter.EXC_TYP, match=_hf.FailIter.EXC_MSG):
        clamp(_hf.FailIter())


def test_clamp_failure5():
    # Too few arguments
    with pytest.raises(TypeError):
        clamp()


def test_clamp_failure6():
    # Changing next method
    with pytest.raises(_hf.CacheNext.EXC_TYP, match=_hf.CacheNext.EXC_MSG):
        # needs to be outside of the range and "remove=True"
        list(clamp(_hf.CacheNext(1), 2, remove=True))


def test_clamp_copy1():
    _hf.iterator_copy(clamp([T(20), T(50)], T(10), T(100)))


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle1():
    clmp = clamp(toT(range(10)), T(2), T(7))
    assert next(clmp) == T(2)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([3, 4, 5, 6, 7])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle2():
    # inclusive
    clmp = clamp(map(T, range(10)), T(2), T(7), inclusive=True)
    assert next(clmp) == T(3)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([4, 5, 6])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle3():
    # only low
    clmp = clamp(map(T, range(10)), T(2))
    assert next(clmp) == T(2)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([3, 4, 5, 6, 7, 8, 9])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle4():
    # only high
    clmp = clamp(map(T, range(10)), high=T(7))
    assert next(clmp) == T(0)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([1, 2, 3, 4, 5, 6, 7])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle5():
    # only high, with inclusive
    clmp = clamp(map(T, range(10)), high=T(7), inclusive=True)
    assert next(clmp) == T(0)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([1, 2, 3, 4, 5, 6])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle6():
    # only low, with inclusive
    clmp = clamp(map(T, range(10)), T(2), inclusive=True)
    assert next(clmp) == T(3)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([4, 5, 6, 7, 8, 9])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle7():
    # no low no high
    clmp = clamp(map(T, range(10)))
    assert next(clmp) == T(0)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([1, 2, 3, 4, 5, 6, 7, 8, 9])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
def test_clamp_pickle8():
    # only high but without remove
    clmp = clamp(map(T, range(10)), high=T(7), remove=False)
    assert next(clmp) == T(0)
    x = pickle.dumps(clmp)
    assert list(pickle.loads(x)) == toT([1, 2, 3, 4, 5, 6, 7, 7, 7])


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
def test_clamp_lengthhint1():
    # When remove=False we can determine the length-hint.
    it = clamp(toT(range(5)), low=T(2), high=T(5), remove=False)
    assert operator.length_hint(it) == 5
    next(it)
    assert operator.length_hint(it) == 4
    next(it)
    assert operator.length_hint(it) == 3
    next(it)
    assert operator.length_hint(it) == 2
    next(it)
    assert operator.length_hint(it) == 1
    next(it)
    assert operator.length_hint(it) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
def test_clamp_lengthhint2():
    # When low and high are not given we can determine the length-hint
    it = clamp(toT(range(5)))
    assert operator.length_hint(it) == 5
    next(it)
    assert operator.length_hint(it) == 4
    next(it)
    assert operator.length_hint(it) == 3
    next(it)
    assert operator.length_hint(it) == 2
    next(it)
    assert operator.length_hint(it) == 1
    next(it)
    assert operator.length_hint(it) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
def test_clamp_lengthhint3():
    # Only works if "remove=False", otherwise the length-hint simply returns 0.
    it = clamp(toT(range(5)), low=T(2), high=T(5), remove=True)
    assert operator.length_hint(it) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
def test_clamp_lengthhint_failure1():
    f_it = _hf.FailLengthHint(toT([1, 2, 3]))
    it = clamp(f_it)
    with pytest.raises(_hf.FailLengthHint.EXC_TYP, match=_hf.FailLengthHint.EXC_MSG):
        operator.length_hint(it)

    with pytest.raises(_hf.FailLengthHint.EXC_TYP, match=_hf.FailLengthHint.EXC_MSG):
        list(it)


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
def test_clamp_lengthhint_failure2():
    of_it = _hf.OverflowLengthHint(toT([1, 2, 3]), sys.maxsize + 1)
    it = clamp(of_it)
    with pytest.raises(OverflowError):
        operator.length_hint(it)

    with pytest.raises(OverflowError):
        list(it)
