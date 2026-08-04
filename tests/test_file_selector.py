import pytest
from datetime import datetime
from src.workspace_core.scanner import FileMeta
from src.workspace_core.selector import FileSelector, SelectionRules

def test_file_selector_size_limit():
    files = [
        FileMeta(path="small.py", size_bytes=100, extension=".py", last_modified=datetime.now()),
        FileMeta(path="large.py", size_bytes=1_000_000, extension=".py", last_modified=datetime.now())
    ]
    rules = SelectionRules(max_size_bytes=500_000)
    selector = FileSelector(rules)
    
    selected = selector.select(files)
    assert len(selected) == 1
    assert selected[0].path == "small.py"

def test_file_selector_allowed_extensions():
    files = [
        FileMeta(path="script.py", size_bytes=100, extension=".py", last_modified=datetime.now()),
        FileMeta(path="readme.md", size_bytes=200, extension=".md", last_modified=datetime.now()),
        FileMeta(path="image.png", size_bytes=300, extension=".png", last_modified=datetime.now())
    ]
    rules = SelectionRules(allowed_extensions={".py", ".md"})
    selector = FileSelector(rules)
    
    selected = selector.select(files)
    assert len(selected) == 2
    paths = [f.path for f in selected]
    assert "script.py" in paths
    assert "readme.md" in paths
    assert "image.png" not in paths

def test_file_selector_ignored_paths():
    files = [
        FileMeta(path="src/main.py", size_bytes=100, extension=".py", last_modified=datetime.now()),
        FileMeta(path="secret/passwords.txt", size_bytes=50, extension=".txt", last_modified=datetime.now()),
        FileMeta(path="tests/test_main.py", size_bytes=150, extension=".py", last_modified=datetime.now())
    ]
    rules = SelectionRules(ignored_paths={"secret"})
    selector = FileSelector(rules)
    
    selected = selector.select(files)
    assert len(selected) == 2
    paths = [f.path for f in selected]
    assert "src/main.py" in paths
    assert "tests/test_main.py" in paths
