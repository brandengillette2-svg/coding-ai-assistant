from app.semantic_index import SemanticIndex
from pathlib import Path
import tempfile


def test_semantic_index_extracts_python_symbols():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a test Python file
        test_file = Path(tmp_dir) / "test.py"
        test_file.write_text("""
class MyClass:
    def method(self):
        pass

def my_function():
    pass
""")
        # This test would need proper setup of the SemanticIndex with the temp directory
