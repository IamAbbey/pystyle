import libcst as cst
import libcst.matchers as m

from fixit import CstLintRule, InvalidTestCase as Invalid, ValidTestCase as Valid
from typing import Sequence, Any


class ReplaceStarredDictWithPipeRule(CstLintRule):
    """
    In python 3, the pipe operator | can be use for dict merging
    e.g {**a, **b} == a | b
    """

    MESSAGE = "Use | instead for dict merging"

    VALID = [
        Valid(
            """
            a = { 'foo' : 'bar' }
            """
        ),
        Valid(
            """
            a = {'foo' : 'bar' }
            b = {'bar' : 'foo' }
            c = a | b
            print(c)
            """
        ),
        Valid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = a | b | { 'gender' : 'male' }
            print(c)
            """
        ),
        Valid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            print(a | b)
            """
        ),
    ]

    INVALID = [
        Invalid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = {**a, **b}
            print(c)
            """,
            expected_replacement="""
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = a | b
            print(c)
            """,
        ),
        Invalid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            print({**a, **b})
            """,
            expected_replacement="""
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            print(a | b)
            """,
        ),
        Invalid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = {**a, **b, 'gender':'male'}
            print(c)
            """,
            expected_replacement="""
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = a | b | {'gender':'male'}
            print(c)
            """,
        ),
        Invalid(
            """
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = {'age': 12, **a, **b, 'gender': 'male'}
            print(c)
            """,
            expected_replacement="""
            a = { 'foo' : 'bar' }
            b = { 'bar' : 'foo' }
            c = a | b | {'age': 12, 'gender': 'male'}
            print(c)
            """,
        ),
    ]

    def is_dict_merging(self, node: cst.BaseExpression) -> bool:
        # check if the node is a dict node
        # a = {**c}
        # {a:1, b:3}
        if m.matches(node, m.Dict()):
            # use ensure_type type to type check node
            node = cst.ensure_type(node, cst.Dict)
            # We only want to apply rule when there is atleast 2 elements in the dict
            # and also when atleast one of the elements is a starred dict
            return len(node.elements) >= 2 and any(
                isinstance(element, cst.StarredDictElement) for element in node.elements
            )

        return False

    def _construct_binary_operation_bit_or(
        self, *, left: cst.BaseExpression, right: cst.BaseExpression
    ):
        return cst.BinaryOperation(
            left=left,
            operator=cst.BitOr(
                whitespace_before=cst.SimpleWhitespace(
                    value=" ",
                ),
                whitespace_after=cst.SimpleWhitespace(
                    value=" ",
                ),
            ),
            right=right,
            lpar=[],
            rpar=[],
        )

    def _zip_in_max_two(self, sequence: Sequence[Any]):
        result = list(zip(sequence[0::2], sequence[1::2]))

        if len(sequence) % 2 == 1:
            result.append((sequence[-1],))

        return result

    def _main(self, node: cst.Assign | cst.Arg):
        # only interested in dicts with dict merging
        if self.is_dict_merging(node.value):
            assign_value = cst.ensure_type(node.value, cst.Dict)
            starred_dict_objects: list = []
            non_starred_dict_objects: list = []

            # loop through the dict elements and separate
            # dict elements from star dicts
            for dict_element in assign_value.elements:
                if isinstance(dict_element, cst.StarredDictElement):
                    starred_dict_objects.append(
                        cst.ensure_type(dict_element, cst.StarredDictElement).value
                    )

                elif isinstance(dict_element, cst.DictElement):
                    non_starred_dict_objects.append(
                        cst.ensure_type(dict_element, cst.DictElement)
                    )

            # The bitor operator requires left and right operands
            # the below groups the merged list of starred dict list and
            # dict node with dict element list from above in twos
            result = self._zip_in_max_two(
                [
                    *starred_dict_objects,
                    cst.Dict(elements=non_starred_dict_objects),
                ]
                if len(non_starred_dict_objects) > 0
                else [*starred_dict_objects]
            )

            response = None

            for index in range(len(result)):
                if len(result[index]) == 2:
                    if response is None:
                        response = self._construct_binary_operation_bit_or(
                            left=result[index][0], right=result[index][1]
                        )
                    else:
                        response = self._construct_binary_operation_bit_or(
                            left=response,
                            right=self._construct_binary_operation_bit_or(
                                left=result[index][0], right=result[index][1]
                            ),
                        )
                else:
                    response = self._construct_binary_operation_bit_or(
                        left=response, right=result[index][0]
                    )

            self.report(
                node,
                replacement=node.deep_replace(node.value, response)
                if response
                else None,
            )

    def leave_Arg(self, node: cst.Arg) -> None:
        self._main(node)

    def leave_Assign(self, node: cst.Assign) -> None:

        self._main(node)
