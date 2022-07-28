# TypedDict

Use `TypedDict` replace [pydantic](https://pydantic-docs.helpmanual.io/) definitions.

## Why?

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int = Field(default=0, ge=0)
    email: Optional[str]


user: User = {"name": "John", "age": 30}  # Type check, error!
print(repr(user))
```

In index.py or other framework, maybe you write the following code. And then got an type check error in `Annotated[Message, ...]`, because the type of `{"message": "..."}` is not `Message`.

```python
class Message(BaseModel):
    message: str


@routes.http.get("/user")
async def create_user(
    ...
) -> Annotated[Message, JSONResponse[200, {}, Message]]:
    ...
    return {"message": "Created successfully!"}
```

## Usage

Use `Annotated` to provide extra information to `pydantic.Field`. Other than that, everything conforms to the general usage of `TypedDict`. Using `to_pydantic` will create a semantically equivalent pydantic model. You can use it in frameworks like [index.py](https://github.com/index-py/index.py) / [fastapi](https://fastapi.tiangolo.com/) / [xpresso](https://github.com/adriangb/xpresso).

```python
from typing_extensions import TypedDict, NotRequired, Annotated

import typeddict
from typeddict import Metadata, Extra


class User(TypedDict):
    name: str
    age: Annotated[int, Metadata(default=0), Extra(ge=0)]
    email: NotRequired[str]


user: User = {"name": "John", "age": 30}  # Type check, pass!
print(repr(user))

# Then use it in index.py / fastapi or other frameworks
UserModel = typeddict.to_pydantic(User)
print(repr(UserModel.parse_obj(user)))
```
