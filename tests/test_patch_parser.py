from app.analyzer.patch_parser import extract_changed_lines


def test_extract_changed_lines_from_patch():
    patch = """@@ -10,4 +10,5 @@ def login():
 context
-old
+new
+another
 unchanged
"""

    assert extract_changed_lines(patch) == [11, 12]

