from fixit import add_lint_rule_tests_to_module
from lint.rules import (
    ReplaceUnionWithPipeRule,
    ReplaceEnumWithStrEnumIfPossibleRule,
    ReplaceClassMethodReturnTypeToSelfRule,
    ReplaceStarredDictWithPipeRule,
)
import unittest

add_lint_rule_tests_to_module(
    globals(),
    rules={
        ReplaceUnionWithPipeRule,
        ReplaceEnumWithStrEnumIfPossibleRule,
        ReplaceClassMethodReturnTypeToSelfRule,
        ReplaceStarredDictWithPipeRule,
    },
)


unittest.main(argv=["first-arg-is-ignored"], exit=False)
