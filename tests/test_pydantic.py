from typing import Type, TypeVar

import pytest
from typing_extensions import Annotated, NotRequired, TypedDict

from typeddict import Extra, Metadata, to_pydantic


class User(TypedDict):
    name: str
    age: Annotated[int, Metadata(default=0), Extra(ge=0)]
    email: NotRequired[Annotated[str, Extra(min_length=5, max_length=100)]]


class Book(TypedDict):
    author: NotRequired[User]


class A(TypedDict):
    a: list[User]
    b: dict[str, User]
    c: tuple[User, ...]


class B(TypedDict):
    a: list[tuple[Book]]
    b: dict[str, tuple[Book, ...]]


T = TypeVar("T", bound=TypedDict)


@pytest.mark.parametrize(
    "typeddict, value",
    [
        (User, {"name": "John", "age": 30}),
        (Book, {"author": {"name": "John", "age": 30}}),
        (
            A,
            {
                "a": [{"name": "John", "age": 30}],
                "b": {"John": {"name": "John", "age": 30}},
                "c": ({"name": "John", "age": 30},),
            },
        ),
        (
            B,
            {
                "a": [({"author": {"name": "John", "age": 30}},)],
                "b": {"John": ({"author": {"name": "John", "age": 30}},)},
            },
        ),
    ],
)
def test_to_pydantic(typeddict: Type[T], value: T) -> None:
    pydantic_model = to_pydantic(typeddict)
    pydantic_model.parse_obj(value)


@pytest.mark.parametrize(
    "typeddict, value",
    [
        (User, {"name": "John", "age": -1}),
        (User, {"name": "John", "age": 30, "email": "123"}),
        (Book, {"author": {"name": "John", "age": -1}}),
        (
            A,
            {
                "a": [{"name": "John", "age": -1}],
                "b": {"John": {"name": "John", "age": -1}},
                "c": ({"name": "John", "age": -1},),
            },
        ),
    ],
)
def test_to_pydantic_error(typeddict: Type[T], value: T) -> None:
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        pydantic_model = to_pydantic(typeddict)
        pydantic_model.parse_obj(value)
