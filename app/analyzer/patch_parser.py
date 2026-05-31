import re


HUNK_RE = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def extract_changed_lines(patch: str) -> list[int]:
    changed_lines: list[int] = []
    new_line_no: int | None = None

    for line in patch.splitlines():
        match = HUNK_RE.match(line)
        if match:
            new_line_no = int(match.group(1))
            continue

        if new_line_no is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            changed_lines.append(new_line_no)
            new_line_no += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        else:
            new_line_no += 1

    return changed_lines

