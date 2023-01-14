from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar
from typing import cast as typecast

from pydantic import BaseModel, Field, create_model
from typing_extensions import TypedDict

from .fields import ParseTypedDictAnnotations, recursive_parsing


class ParseTypedDictToPydantic(ParseTypedDictAnnotations):
    def handle_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        options.setdefault("default", ...)
        return (key, field_type, options)

    def handle_not_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        return (key, Optional[field_type], options)

    def create_schema(self, name: str, fields: List[Tuple[str, Any, Dict[str, Any]]]):
        return create_model(
            name,
            **{
                field_name: (
                    (recursive_parsing(field_type, self), Field(**options))
                    if options
                    else (recursive_parsing(field_type, self), None)
                )
                for field_name, field_type, options in fields
            }
        )


_parse = ParseTypedDictToPydantic()


def to_pydantic(typeddict: Type[TypedDict]) -> Type[BaseModel]:
    """
    Convert a TypedDict to a Pydantic model.
    """
    return _parse(typeddict)


T = TypeVar("T", bound=TypedDict)


def cast(typeddict: Type[T], value: Dict[Any, Any]) -> T:
    """
    Cast a Dict to a TypedDict.
    """
    return typecast(T, to_pydantic(typeddict).parse_obj(value).dict())
