import pytest
from src.workspace_core.project_manager import ProjectManager
from src.workspace_core.scanner import WorkspaceScanner, FileMeta

def test_workspace_scanner(tmp_path):
    # Setup dummy structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    py_file = src_dir / "main.py"
    py_file.write_text("print('hello world')")
    
    # Initialize
    pm = ProjectManager(str(tmp_path))
    scanner = WorkspaceScanner(pm)
    
    # Scan
    results = scanner.scan()
    
    assert len(results) == 1
    meta = results[0]
    
    assert isinstance(meta, FileMeta)
    assert meta.path == "src/main.py"
    assert meta.size_bytes == 20
    assert meta.extension == ".py"
    assert meta.last_modified is not None

def test_workspace_scanner_empty(tmp_path):
    pm = ProjectManager(str(tmp_path))
    scanner = WorkspaceScanner(pm)
    assert len(scanner.scan()) == 0
