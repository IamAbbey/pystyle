from typing import Sequence

import libcst.matchers as m
import libcst as cst


def make_simple_package_import(package: str) -> cst.Import:
    assert "." not in package, "this only supports a root package, e.g. 'import os'"
    return cst.Import(names=[cst.ImportAlias(name=cst.Name(package))])


def make_simple_package_import_from(module: str, package: str) -> cst.ImportFrom:
    """from x import y"""
    assert "." not in module, "this only supports a root module, e.g. 'import os'"
    assert "." not in package, "this only supports a root package, e.g. 'import os'"
    return cst.ImportFrom(
        module=cst.Name(module), names=[cst.ImportAlias(name=cst.Name(package))]
    )


def _is_import_line(line: cst.SimpleStatementLine | cst.BaseCompoundStatement) -> bool:
    return m.matches(line, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()]))


def with_added_imports(
    module_node: cst.Module, import_nodes: Sequence[cst.Import | cst.ImportFrom]
) -> cst.Module:
    """
    Adds new import `import_node` after the first import in the module `module_node`.
    """
    updated_body: list[cst.SimpleStatementLine | cst.BaseCompoundStatement] = []
    added_import = False
    for line in module_node.body:
        updated_body.append(line)
        if not added_import and _is_import_line(line):
            for import_node in import_nodes:
                updated_body.append(cst.SimpleStatementLine(body=tuple([import_node])))
            added_import = True

    if not added_import:
        raise RuntimeError("Failed to add imports")

    return module_node.with_changes(body=tuple(updated_body))
