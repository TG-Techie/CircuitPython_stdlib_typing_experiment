# LICENSE: MIT
#
# Copyright (c) 2022, Jonah "Jay" Y-M (@TG-Techie)
#
# See repo for license text.

"""
`typing` (typing_syntax_only)
=======================

This is more even more bare-bones implementation than `typing_minimal_rt.py`, 
please see that file or the README for more information.

This modules aims to add syntax-level only compatibility for features that cannot go in type-hints and 
"""

from __future__ import annotations


TYPE_CHECKING = False  # evaluates to True at type-check time


class Generic:
    def __new__(cls, *_, **__):
        assert cls is not Generic, "Generic(...) cannot be instantiated"
        return object.__new__(cls)

    def __class_getitem__(cls, params):
        # TypeVar(...) and ParamSpec(...) return None instead of a type
        if cls is Generic:
            allowed = (None, (None,))
            assert params in allowed or all(tp in allowed for tp in params), (
                "Generic[...] only supports TypeVar(...), ParamSpec(...), etc parameters "
                "(`None` at runtime)"
            )
        return cls


def TypeVar(name: str, *constraints, bound=None, contravariant=False, covariant=False):
    return None


# see pep 544
# exclude support for @runtime_checkable
class Protocol:
    def __new__(cls, *_, **__):
        assert cls is not Protocol, "Protocol cannot be instantiated"
        return object.__new__(cls)

    def __class_getitem__(cls, params: type) -> type[Protocol]:
        return cls


# see pep 612
# the related `Concatenate[...]` type is only used in annotations so does not need to exist at runtime
def ParamSpec(name, *, bound=None, covariant=False, contravariant=False):
    return None


# see pep 646
def TypeVarTuple(name):
    return (None,)


# special form in the pep
Unpack = {(None,): None}

# check that __class_getitem__ is supported,
try:
    assert (
        Generic[None] is Generic
    )  # check that either __class_getitem__ is supported or type[] passthrough is supported
except TypeError:
    raise RuntimeError(
        " Class typing parameters (ex: Generic[T]) not supported, "
        "you may need to use a different version of circuitpython."
        "(see: https://github.com/tg-techie/CircuitPython_stdlib_typing_experiment)"
    )
