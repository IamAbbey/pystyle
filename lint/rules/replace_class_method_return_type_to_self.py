from fixit import CstLintRule, InvalidTestCase as Invalid, ValidTestCase as Valid
import libcst as cst
from libcst.metadata import (
    QualifiedName,
    QualifiedNameProvider,
    QualifiedNameSource,
)
from libcst import matchers as m


class ReplaceClassMethodReturnTypeToSelfRule(CstLintRule):
    """
    In python 3.11, a new Self annotation was introduced to provide a simple and
    intuitive way to annotate methods that return an instance of their class.
    """

    VALID = [
        Valid(
            """
            class Foo:
                # classmethod with Self as return type.
                @classmethod
                def cm(cls) -> Self:
                    pass
            """
        ),
        Valid(
            """
            class Foo:
                # non-classmethod with non-cls first arg.
                def nm(self, a, b, c):
                    pass
            """
        ),
        Valid(
            """
            class Foo:
                # staticmethod with non-cls first arg.
                @staticmethod
                def sm(a):
                    pass
            """
        ),
    ]
    INVALID = [
        Invalid(
            """
            class Foo:
                # No return type.
                @classmethod
                def cm(cls):
                    pass
            """,
            expected_replacement="""
             class Foo:
                 # No return type.
                 @classmethod
                 def cm(cls) -> Self:
                     pass
             """,
        ),
        Invalid(
            """
            class Foo:
                # Wrong return type.
                @classmethod
                def cm(cls) -> "Bar":
                    pass
            """,
            expected_replacement="""
             class Foo:
                 # Wrong return type.
                 @classmethod
                 def cm(cls) -> Self:
                     pass
             """,
        ),
        Invalid(
            """
            class Foo:
                # Using class name as return type.
                @classmethod
                def cm(cls) -> "Foo":
                    pass
            """,
            expected_replacement="""
             class Foo:
                 # Using class name as return type.
                 @classmethod
                 def cm(cls) -> Self:
                     pass
             """,
        ),
    ]

    METADATA_DEPENDENCIES = (QualifiedNameProvider,)
    MESSAGE = "When using @classmethod, the return type should be Self"

    def visit_FunctionDef(
        self,
        node: cst.FunctionDef,
    ) -> None:
        if any(
            QualifiedNameProvider.has_name(
                self,
                decorator.decorator,
                QualifiedName(
                    name="builtins.classmethod",
                    source=QualifiedNameSource.BUILTIN,
                ),
            )
            for decorator in node.decorators
        ):  # we are only interested in functions with @classmethod decorator.
            new_returns = (
                node.returns.with_changes(annotation=cst.Name(value="Self"))
                if node.returns is not None
                else cst.Annotation(
                    annotation=cst.Name(
                        value="Self",
                        lpar=[],
                        rpar=[],
                    )
                )
            )
            new_function_def = node.with_changes(returns=new_returns)
            if node.returns is None or not m.matches(
                node.returns.annotation, m.Name(value="Self")
            ):
                self.report(
                    node,
                    replacement=new_function_def,
                )
