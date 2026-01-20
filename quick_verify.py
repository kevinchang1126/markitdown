
import ast
import sys

files = [
    r"c:\Users\ertai\githubproject\markitdown\packages\markitdown\src\markitdown\api_server.py",
    r"c:\Users\ertai\githubproject\markitdown\packages\markitdown\src\markitdown\_markitdown.py",
    r"c:\Users\ertai\githubproject\markitdown\packages\markitdown\src\markitdown\converters\_image_converter.py",
    r"c:\Users\ertai\githubproject\markitdown\packages\markitdown\src\markitdown\converters\_llm_caption.py"
]

has_error = False

for file_path in files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            ast.parse(content)
            print(f"OK: {file_path}")
    except Exception as e:
        print(f"ERROR checking {file_path}: {e}")
        has_error = True

if has_error:
    sys.exit(1)
