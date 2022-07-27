from typing_extensions import Annotated, NotRequired, TypedDict

from typeddict import Extra, Metadata, to_pydantic


class User(TypedDict):
    name: str
    age: Annotated[int, Metadata(), Extra()]
    email: NotRequired[str]


user: User = {"name": "John", "age": 30}
print(user)
UserModel = to_pydantic(User)
print(UserModel)
print(UserModel.parse_obj(user))
