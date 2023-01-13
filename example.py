from typing_extensions import Annotated, NotRequired, TypedDict

import typeddict
from typeddict import Extra, Metadata


class User(TypedDict):
    name: str
    age: Annotated[int, Metadata(default=0), Extra(ge=0)]
    email: NotRequired[Annotated[str, Extra(min_length=5, max_length=100)]]


class Book(TypedDict):
    author: NotRequired[User]


user: User = {"name": "John", "age": 30}  # Type check, pass!
print(repr(user))

# Then use it in fastapi / index.py or other frameworks
UserModel = typeddict.to_pydantic(User)
print(repr(UserModel.__signature__))
print(repr(UserModel.parse_obj(user)))

book: Book = {"author": user}  # Type check, pass!
print(repr(book))

# Then use it in fastapi / index.py or other frameworks
BookModel = typeddict.to_pydantic(Book)
print(repr(BookModel.__signature__))
print(repr(BookModel.parse_obj(book)))
