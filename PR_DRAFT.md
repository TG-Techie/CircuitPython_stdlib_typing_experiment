Draft Pull Request `__class_getitem__`
(this may be better as two PRs)
(start below)

---
<!-- The next line is the PR title-->
### Improve cpython `typing` compatibility with `__class_getitem__`

This PR adds the `__class_getitem__` method to classes in-order to better support cpython like type-hinting. It also has two other typing related features.

Circuitpython is largely compatible with the cpython like typing because it supports type-hint syntax without executing it. 
There are three exceptions to that.

However, the protocol / generic typing features require some non-type-hint syntax since `Generic` and `Protocol` need to be passed to a class's bases.
##### example
```python
T = TypeVar('T')
class Wrapper(Generic[T]):
    wrapped: T
    ...
class Peripheral(Protocol[T]):
  def deinit(self) -> None:
    ...
```

#### Why


### Rationale

## Circuitpython Core Support


This PR adds 3 toggle-able features to the core:
#### [Pep 560](https://peps.python.org/pep-0560/#class-getitem) 
add `__class_getitem__` as discussed above.

Adds .subscr to `mp_type_type

#### [Pep 585](https://peps.python.org/pep-0585/) 
add generic `[]` operator to builtin containers and collections to return themselves. 
  ex:`dict[str, int] is dict # True`


#### [Pep 604 like](https://peps.python.org/pep-0604/) 
  This adds the `|` operator on type so it returns `object` 
  ex: `(str | None) is object # True`

## Implementing the `typing` module

TODO: add link to runtime 

Only add the typing feature that have to be used outside of type-hints.

Should it be implemented in python-land or in the core?

If it is implemented in the core? 

The answer may be either. 

Working minimain

no @runtime_checkable, but that shouldn't work anyways

no way to cut-off the **class_getitem** functionality **without** auto-generating an extra class. (If Foo[a, b, c] did not have a typevar or paramspec in a, b, c)>> That class would manually raise an error when **class_getitem** is called on it.
  > In the typing\_.py implementation in python-land, circuitpython implementation this can be turned on/off by setting the GENERATE_NONGENERIC_BASES attribute on the `Generic` class.

> :warning: TODO: add example here?

## Questions I have / Feedback

- Should the `typing` module be in python-land or the core
- 


### Background

The `__class_getitem__` method is a special method that was added in cpython 3.7 used to supper the `[]` operator on classes without using metaclasses. 

### Misc Other Thoughts
- For later discussion: Use of `TYPE_CHECKING` or `try:...` or making a new circuitpython-ism (maybe `from micropython import annotation_only` like `TYPE_CHECKING`)

### Considered alternatives:

#### Special Syntax
Add ignoring `[...]` in class definitions 

#### type `[]` without `__class_getitem__`
- add the `[]`` operator to all type object to take __anything__ and return the type it was called on. See a [rudimentary implementation here](https://github.com/TG-Techie/circuitpython/blob/5a08692980f8568d6ef05b8d207a1114080aaf86/py/objtype.c#L1153-L1169)
  > This would have a smaller code footprint, however it would make every type everywhere return itself from the `[]` operator. `SomeType[1, 2, 3] is SomeType # True`
