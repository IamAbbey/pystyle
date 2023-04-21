from .replace_starred_dict_with_pipe import ReplaceStarredDictWithPipeRule
from .replace_union_with_pipe import ReplaceUnionWithPipeRule
from .replace_class_method_return_type_to_self import (
    ReplaceClassMethodReturnTypeToSelfRule,
)
from .replace_enum_to_str_enum_if_possible import ReplaceEnumWithStrEnumIfPossibleRule


__all__ = [
    ReplaceUnionWithPipeRule,
    ReplaceEnumWithStrEnumIfPossibleRule,
    ReplaceClassMethodReturnTypeToSelfRule,
    ReplaceStarredDictWithPipeRule,
]
