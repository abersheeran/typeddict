from typing_extensions import TypedDict, NotRequired, Annotated

import typeddict
from typeddict import Metadata, Extra


class User(TypedDict):
    name: str
    age: Annotated[int, Metadata(default=0), Extra(ge=0)]
    email: NotRequired[str]


user: User = {"name": "John", "age": 30}  # Type check, pass!
print(repr(user))

# Then use it in fastapi / index.py or other frameworks
UserModel = typeddict.to_pydantic(User)
print(repr(UserModel.parse_obj(user)))
