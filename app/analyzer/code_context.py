import ast

from app.analyzer.patch_parser import extract_changed_lines
from app.schemas.pr import ChangedFile


def build_local_context(file: ChangedFile, window: int = 40) -> str | None:
    if not file.content or not file.patch:
        return None

    changed_lines = extract_changed_lines(file.patch)
    if not changed_lines:
        return None

    if file.filename.endswith(".py"):
        python_context = _extract_python_scope(file.content, changed_lines)
        if python_context:
            return python_context

    return _extract_window(file.content, changed_lines, window)


def _extract_python_scope(content: str, changed_lines: list[int]) -> str | None:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    scopes: list[ast.AST] = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and hasattr(node, "lineno")
        and hasattr(node, "end_lineno")
    ]

    matched: list[ast.AST] = []
    for scope in scopes:
        start = scope.lineno
        end = scope.end_lineno or start
        if any(start <= line <= end for line in changed_lines):
            matched.append(scope)

    if not matched:
        return None

    lines = content.splitlines()
    blocks: list[str] = []
    for scope in sorted(matched, key=lambda node: node.lineno)[:3]:
        name = getattr(scope, "name", "scope")
        start = max(scope.lineno, 1)
        end = min(scope.end_lineno or start, len(lines))
        code = "\n".join(_with_line_numbers(lines[start - 1 : end], start))
        blocks.append(f"### Python scope: {name} ({start}-{end})\n```python\n{code}\n```")

    return "\n".join(blocks)


def _extract_window(content: str, changed_lines: list[int], window: int) -> str:
    lines = content.splitlines()
    center = changed_lines[0]
    start = max(center - window, 1)
    end = min(center + window, len(lines))
    code = "\n".join(_with_line_numbers(lines[start - 1 : end], start))
    return f"### Local window ({start}-{end})\n```text\n{code}\n```"


def _with_line_numbers(lines: list[str], start: int) -> list[str]:
    return [f"{line_no:>4}: {line}" for line_no, line in enumerate(lines, start)]

