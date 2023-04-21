from fixit import CstLintRule, InvalidTestCase as Invalid, ValidTestCase as Valid
import libcst as cst
import libcst.matchers as m
from typing import Union

class ReplaceUnionWithPipeRule(CstLintRule):
    """
    In python 3, the pipe operator | can be use in place of Union
    e.g Union[int, str] == int | str
    """

    MESSAGE = "Use | instead of Union"

    VALID = [
        Valid(
            """
            foo: str
            """
        ),
        Valid(
            """
            foo: None | str
            """
        ),
        Valid(
            """
            foo: int | str
            """
        ),
        Valid(
            """
            foo: float | int | str
            """
        ),
        Valid(
            """
            def func() -> str:
                pass
            """
        ),
        Valid(
            """
            def func() -> int | str:
                pass
            """
        ),
    ]

    INVALID = [
        Invalid(
            """
            foo: Union[str]
            """,
            expected_replacement="""
            foo: str
            """,
        ),
        Invalid(
            """
            foo: Union[None, str]
            """,
            expected_replacement="""
            foo: None | str
            """,
        ),
        Invalid(
            """
            foo: Union[int, str]
            """,
            expected_replacement="""
            foo: int | str
            """,
        ),
        Invalid(
            """
            foo: Union[float, int, str]
            """,
            expected_replacement="""
            foo: float | int | str
            """,
        ),
        Invalid(
            """
            def func() -> Union[str]:
                pass
            """,
            expected_replacement="""
            def func() -> str:
                pass
            """,
        ),
        Invalid(
            """
            def func() -> Union[int, str]:
                pass
            """,
            expected_replacement="""
            def func() -> int | str:
                pass
            """,
        ),
    ]

    def annotation_contains_union(self, node: cst.Annotation) -> bool:
        # This does not cater for nexted Unions
        return m.matches(
            node,
            m.Annotation(
                m.Subscript(
                    value=m.Name("Union"),
                    slice=[m.AtLeastN(n=1, matcher=m.SubscriptElement(m.Index()))],
                )
            ),
        )

    def leave_Annotation(self, original_node: cst.Annotation) -> None:
        # Only interested in annotations with unions
        if self.annotation_contains_union(original_node):
            union_index: set[str] = set()
            # this check is to not allow apply_fix on nexted Unions but allow run check
            allow_replacement = True
            for s in cst.ensure_type(original_node.annotation, cst.Subscript).slice:
                # this will be true for non nexted Unions
                if m.matches(s, m.SubscriptElement(m.Index(m.Name()))):
                    union_index.add(s.slice.value.value)
                else:
                    allow_replacement = False

            self.report(
                original_node,
                replacement=original_node.with_changes(
                    annotation=cst.parse_expression(" | ".join(sorted(union_index)))
                )
                if allow_replacement
                else None,
            )
