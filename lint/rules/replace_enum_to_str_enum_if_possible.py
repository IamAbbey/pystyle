from fixit import (
    CstLintRule,
    InvalidTestCase as Invalid,
    ValidTestCase as Valid,
)
import libcst as cst

import libcst.matchers as m


class ReplaceEnumWithStrEnumIfPossibleRule(CstLintRule):
    """
    In python 3.11, StrEnum was added,
    with members that can be used as (and must be) strings.
    """

    VALID = [
        Valid(
            """
            class RiskIndicator(StrEnum):
                CAR = "112"
                MACHINE = "112"
            """
        ),
        Valid(
            """
            class RiskIndicator(Enum):
                CAR = "112"
                MACHINE = "112"
                VEHICLE = 234
            """
        ),
    ]
    INVALID = [
        Invalid(
            """
            class RiskIndicator(Enum):
                CAR = "112"
                MACHINE = "112"
            """,
            expected_replacement="""
            class RiskIndicator(StrEnum):
                CAR = "112"
                MACHINE = "112"
            """,
        ),
    ]

    MESSAGE = "When all Enum properties are string, use StrEnum instead of Enum"

    to_be_change: set[str] = set()

    def visit_Attribute(self, node: cst.Attribute) -> None:
        if m.matches(node, matcher=m.Attribute(value=m.Attribute(value=m.Name()))):
            node_value: cst.Attribute = cst.ensure_type(node.value, cst.Attribute)
            if (
                attribute_name := cst.ensure_type(node_value.value, cst.Name)
                in self.to_be_change
            ):
                self.report(
                    node,
                    message="Potential StrEnum class should not have .value",
                    replacement=node.with_changes(
                        value=attribute_name,
                        attr=node_value.attr,
                        dot=node_value.dot,
                        lpar=node_value.lpar,
                        rpar=node_value.rpar,
                    ),
                )

    def visit_ClassDef(
        self,
        node: cst.ClassDef,
    ) -> None:
        has_enum_base = m.matches(
            node,
            m.ClassDef(
                bases=[
                    m.AtMostN(
                        n=1,
                        matcher=m.Arg(value=m.Name("Enum")),
                    )
                ]
            ),
        )

        num_of_string_property = 0
        num_of_lines = 0

        if has_enum_base:
            for line in node.body.body:
                num_of_lines += 1
                if m.matches(
                    line,
                    m.SimpleStatementLine(
                        body=[
                            m.Assign(
                                targets=[m.AssignTarget()],
                                value=m.SimpleString(),
                            )
                        ]
                    ),
                ):
                    num_of_string_property += 1

            if num_of_lines == num_of_string_property:
                self.to_be_change.add(node.name.value)
                self.report(
                    node,
                    replacement=node.with_changes(
                        bases=(node.bases[0].with_changes(value=cst.Name("StrEnum")),)
                    ),
                )
