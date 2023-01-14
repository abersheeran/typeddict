import abc
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Generic,
    List,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import (
    Annotated,
    NotRequired,
    Required,
    TypedDict,
    get_args,
    get_origin,
    is_typeddict,
)

T = TypeVar("T")


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


def recursive_parsing(field_type: Any, call: Callable) -> Any:
    if is_typeddict(field_type):
        return call(field_type)

    origin_type = get_origin(field_type)
    if origin_type is None:
        return field_type
    if origin_type is Annotated:
        field_type, *options_list = get_args(field_type)
        field_type = recursive_parsing(field_type, call)
        return Annotated.__class_getitem__(tuple((field_type, *options_list)))  # type: ignore
    if origin_type is list:
        (field_type,) = get_args(field_type)
        if hasattr(list, "__class_getitem__"):
            return list.__class_getitem__(recursive_parsing(field_type, call))
        else:
            return List.__getitem__(recursive_parsing(field_type, call))  # type: ignore
    if origin_type is dict:
        key_type, value_type = get_args(field_type)
        if hasattr(dict, "__class_getitem__"):
            return dict.__class_getitem__(
                (recursive_parsing(key_type, call), recursive_parsing(value_type, call))
            )
        else:
            return Dict.__getitem__(  # type: ignore
                (recursive_parsing(key_type, call), recursive_parsing(value_type, call))
            )
    if origin_type is tuple:
        field_types = get_args(field_type)
        if hasattr(tuple, "__class_getitem__"):
            return tuple.__class_getitem__(
                tuple(recursive_parsing(t, call) for t in field_types)
            )
        else:
            return Tuple.__getitem__(  # type: ignore
                tuple(recursive_parsing(t, call) for t in field_types)
            )
    if origin_type is set:
        (field_type,) = get_args(field_type)
        if hasattr(set, "__class_getitem__"):
            return set.__class_getitem__(recursive_parsing(field_type, call))
        else:
            return Set.__getitem__(recursive_parsing(field_type, call))  # type: ignore
    if origin_type is frozenset:
        (field_type,) = get_args(field_type)
        if hasattr(frozenset, "__class_getitem__"):
            return frozenset.__class_getitem__(recursive_parsing(field_type, call))
        else:
            return FrozenSet.__getitem__(recursive_parsing(field_type, call))  # type: ignore
    if origin_type is Required:
        (field_type,) = get_args(field_type)
        return Required.__class_getitem__(recursive_parsing(field_type, call))  # type: ignore
    if origin_type is NotRequired:
        (field_type,) = get_args(field_type)
        return NotRequired.__class_getitem__(recursive_parsing(field_type, call))  # type: ignore
    if origin_type is Union:
        field_types = get_args(field_type)
        return Union.__getitem__(tuple(recursive_parsing(t, call) for t in field_types))  # type: ignore
    raise NotImplementedError(
        f"Unsupported type: {field_type}, it's origin type: {origin_type}"
    )


class ParseTypedDictAnnotations(Generic[T], metaclass=abc.ABCMeta):
    def handle_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        return (key, field_type, options)

    def handle_not_required_field(
        self, key: str, field_type: Any, options: Dict[str, Any]
    ) -> Tuple[str, Any, Dict[str, Any]]:
        return (key, field_type, options)

    @abc.abstractmethod
    def create_schema(
        self, name: str, fields: List[Tuple[str, Any, Dict[str, Any]]]
    ) -> T:
        raise NotImplementedError

    def __call__(self, typeddict: Type[TypedDict]) -> T:
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

            fields.append(self.handle_required_field(key, field_type, options))

        for key in typeddict.__optional_keys__:
            field_type = typeddict.__annotations__.get(key)
            options = {}
            if is_not_required(field_type):
                field_type = get_args(field_type)[0]
            if get_origin(field_type) is Annotated:
                field_type, *options_list = get_args(field_type)
                for option in options_list:
                    options.update(option)

            fields.append(self.handle_not_required_field(key, field_type, options))

        return self.create_schema(typeddict.__name__, fields)
