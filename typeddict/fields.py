import abc
from typing import Any, Callable, Dict, List, Tuple, Type

from typing_extensions import (
    Annotated,
    NotRequired,
    Required,
    TypedDict,
    get_args,
    get_origin,
    is_typeddict,
)


class Metadata(TypedDict, total=False):
    """
    Metadata for a field.
    """

    default: Any
    default_factory: Callable[[], Any]
    alias: str
    title: str
    description: str


class Extra(Dict[str, Any]):
    """
    Extra field information.
    """


def is_required(field_type: Any) -> bool:
    """
    Check if a field is required.
    """
    return get_origin(field_type) is Required


def is_not_required(field_type: Any) -> bool:
    """
    Check if a field is not required.
    """
    return get_origin(field_type) is NotRequired


class ParseTypedDictAnnotations(metaclass=abc.ABCMeta):
    def handle_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        return (key, field_type, options)

    def handle_not_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        return (key, field_type, options)

    @abc.abstractmethod
    def create_schema(self, name: str, fields: List[Tuple[str, Any, Dict[str, Any]]]):
        raise NotImplementedError

    def __call__(self, typeddict: Type[TypedDict]):
        assert is_typeddict(typeddict)

        fields = []
        for key in typeddict.__required_keys__:
            field_type = typeddict.__annotations__.get(key)
            options = {}
            if is_required(field_type):
                field_type = get_args(field_type)[0]
            if get_origin(field_type) is Annotated:
                field_type, *options_list = get_args(field_type)
                for option in options_list:
                    options.update(option)

            fields.append((key, field_type, options))

        for key in typeddict.__optional_keys__:
            field_type = typeddict.__annotations__.get(key)
            options = {}
            if is_not_required(field_type):
                field_type = get_args(field_type)[0]
            if get_origin(field_type) is Annotated:
                field_type, *options_list = get_args(field_type)
                for option in options_list:
                    options.update(option)

            fields.append((key, field_type, options))

        return self.create_schema(typeddict.__name__, fields)
