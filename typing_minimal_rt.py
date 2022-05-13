# LICENSE: MIT
#
# Copyright (c) 2022, Jonah "Jay" Y-M (@TG-Techie)
#
# See repo for license text.

"""
`typing` (typing_minimal_rt)
=======================

A prototype module for circuitpython to replace the `typing` module in the cpython standard library.
This aims to add compatibility only for features that cannot go in type-hints.

Please review the assoicated README.md / Pull request for more information. 

This below code works in-conjuntion with changes made to circuitpython:
see preliminary changes in `py/objtype.c` file here https://github.com/TG-Techie/circuitpython/tree/add_class_getitem
"""

from __future__ import annotations


TYPE_CHECKING = False  # evaluates to True at type-check time


class Generic:

    GENERATE_NONGENERIC_BASES = False

    def __new__(cls, *_, **__):
        assert cls is not Generic, "Generic(...) cannot be instantiated"
        return object.__new__(cls)

    def __class_getitem__(cls, params):
        assert not isinstance(
            params, slice
        ), "slicing now allowed in type parameters, ex `Generic[T:S]`"
        # check all the inputs are of the correct types
        typeparams = _check_are_typeparams(params)
        # generic only allows typevar like
        if cls is Generic:
            assert all(
                isinstance(tp, _TypeVarLike) for tp in typeparams
            ), "Generic[...] only supports TypeVar, ParamSpec, etc type parameters"
        elif cls.GENERATE_NONGENERIC_BASES:
            # generate a non-generic base when the there are no TypeVar like items in the type params
            # assume strings are forwards refs and not generic
            # TDOD: revisit assumption
            if all(not isinstance(t, _TypeVarLike) for t in typeparams):
                if wrapper_cls := getattr(cls, "_nongeneric_wrapper_cls", None):
                    wrapper_cls = cls._nongeneric_wrapper_cls = type(  # type: ignore
                        cls.__name__,
                        (wrapper_cls,),
                        {"__class_getitem__": _nongeneric_class_getitem},
                    )
                    wrapper_cls.__module__ = cls.__module__
                    wrapper_cls.__qualname__ = cls.__qualname__
                    wrapper._generic_base_cls = cls  # type: ignore
                return wrapper_cls
        return cls


class _TypeVarLike:
    # # these attrs are skipped but would be present in cpython
    # __name__: str # the name of the type variable, the first argument to TypeVar
    # __covariant__: bool
    # __contravariant__: bool
    # __bound__: <type param> | None
    # __module__: str | None

    # _TypeVarLike subclseses only have one instance, store related values in the class
    __single_instance: _TypeVarLike  # auto-created
    __repr_str: str  # defined in the subclass

    def __new__(
        cls,
        name: str,
        *,
        bound=None,
        contravariant=False,
        covariant=False,
    ):
        # intentiaonally not using super()
        assert (
            cls is not _TypeVarLike
        ), "_TypeVarLike(...) called, it should not be instantiated"

        assert not (
            covariant and contravariant
        ), "Bivariant types are not supported, cannot be both covariant and contravariant"
        # skipped # self.__constraints__ = tuple of constraints given
        # skipped #  self.__module__ = callsite_globals['__name__] exlcuding 'typing'

        # TODO(tg-techie): should there be one per name, and store them in a dict?
        # only make one instance per class to save memory
        if (self := getattr(cls, "__single_instance", None)) is None:
            self = cls.__single_instance = object.__new__(cls)
            # if making a new one, init the realted values in the class __dict__
            assert hasattr(cls, "__repr_str")  # define these in the subclasses

        return self

    def __repr__(self) -> str:
        return self.__repr_str


class TypeVar(_TypeVarLike):
    # # additional skipped field
    # __constraints__: tuple[<type parmas ...>] | tuple[()]

    __repr_str = "<TypeVar>"

    def __new__(
        cls,
        name: str,
        *constraints,
        bound=None,
        contravariant=False,
        covariant=False,
    ):
        assert cls is TypeVar, "TypeVar cannot be subclassed"

        assert not (
            constraints and bound is not None
        ), "Constraints cannot be combined with bound=..."

        assert (
            not constraints or len(constraints) > 1
        ), "A single constraint is not allowed"

        _check_are_typeparams(constraints)

        return _TypeVarLike.__new__(
            cls,
            name=name,
            bound=bound,
            contravariant=contravariant,
            covariant=covariant,
        )


# see pep 544
# exclude support for @runtime_checkable
class Protocol:
    def __new__(cls, *_, **__):
        assert cls is not Protocol, "Protocol cannot be instantiated"
        return object.__new__(cls)

    def __class_getitem__(cls, params: type) -> type[Protocol]:
        _check_are_typeparams(params)
        return cls


# see pep 612
# the related `Concatenate[...]` type is only used in annotations so does not need to exist at runtime
class ParamSpec(_TypeVarLike):

    __repr_str = "<ParamSpec>"

    def __new__(cls, name, *, bound=None, covariant=False, contravariant=False):
        assert cls is ParamSpec, "ParamSpec cannot be subclassed"
        return _TypeVarLike.__new__(
            cls,
            name=name,
            bound=bound,
            covariant=covariant,
            contravariant=contravariant,
        )


# see pep 646
class TypeVarTuple(_TypeVarLike):

    __repr_str = "<TypeVarTuple>"

    def __new__(cls, name):
        assert cls is TypeVarTuple, "TypeVarTuple cannot be subclassed"
        return _TypeVarLike.__new__(cls, name=name)

    def __iter__(self):  # -> Unpack[Self]
        return self


# Unpack[...] is a special form in cpython, here we use a class (tho we could use {TypeVarTuple(...): object})
class Unpack:
    __new__ = None  # type: ignore

    def __class_getitem__(cls, params):
        assert isinstance(
            params, TypeVarTuple
        ), "Unpack[...] only supports a single TypeVarTuple"
        return params


_allowed_param_types = (type, str, _TypeVarLike)


def _check_are_typeparams(params) -> tuple:
    global _allowed_param_types
    typeparams = params if params.__class__ is tuple else (params,)
    assert all(
        isinstance(tp, _allowed_param_types) for tp in typeparams
    ), " type parameters must be types, ForwardRefs (strings), TypeVars, or ParamSpecs"
    return typeparams


def _nongeneric_class_getitem(cls: type[Generic], _params):
    raise TypeError(
        f"{cls.__name__} is not generic and cannot be used with type parameters"
    )


# FUTURE/TODO(tg-techie): make it so isinstance(obj, Protocol) returns False

# check that __class_getitem__ is supported,
try:
    Generic[TypeVar("T")]
except TypeError:
    raise RuntimeError(
        " Class typing parameters (ex: Generic[T]) not supported, "
        "you may need to use a different version of circuitpython."
        "(see: https://github.com/tg-techie/CircuitPython_stdlib_typing_experiment)"
    )
