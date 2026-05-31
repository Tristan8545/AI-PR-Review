from pathlib import PurePosixPath

from app.schemas.pr import ChangedFile


def guess_related_test_paths(files: list[ChangedFile]) -> list[str]:
    candidates: list[str] = []

    for file in files:
        path = file.filename.replace("\\", "/")
        lower = path.lower()
        if _is_test_path(lower):
            continue

        guessed = _guess_for_path(path)
        for item in guessed:
            if item not in candidates:
                candidates.append(item)

    return candidates


def _guess_for_path(path: str) -> list[str]:
    p = PurePosixPath(path)
    stem = p.stem
    suffix = p.suffix
    parent = str(p.parent)
    candidates: list[str] = []

    if suffix == ".py":
        module_parts = list(p.parts)
        if module_parts and module_parts[0] == "app":
            relative = "/".join(module_parts[1:])
            candidates.append(f"tests/{relative}".replace(f"{stem}.py", f"test_{stem}.py"))
        candidates.extend(
            [
                f"tests/test_{stem}.py",
                f"{parent}/test_{stem}.py",
                f"tests/{stem}_test.py",
            ]
        )

    if suffix == ".java":
        candidates.extend(
            [
                path.replace("src/main/java", "src/test/java").replace(".java", "Test.java"),
                path.replace("src/main/java", "src/test/java").replace(".java", "Tests.java"),
            ]
        )

    if suffix in {".js", ".ts", ".tsx", ".jsx"}:
        candidates.extend(
            [
                f"{parent}/{stem}.test{suffix}",
                f"{parent}/{stem}.spec{suffix}",
                f"tests/{stem}.test{suffix}",
                f"tests/{stem}.spec{suffix}",
            ]
        )

    return [candidate for candidate in candidates if candidate and candidate != path]


def _is_test_path(path: str) -> bool:
    return (
        "/test_" in path
        or path.startswith("tests/")
        or ".test." in path
        or ".spec." in path
        or path.endswith("test.java")
        or path.endswith("tests.java")
    )

