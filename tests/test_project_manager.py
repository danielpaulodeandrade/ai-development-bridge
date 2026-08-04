import os
import pytest
from src.workspace_core.project_manager import ProjectManager

def test_project_manager_invalid_path():
    with pytest.raises(ValueError):
        ProjectManager("invalid_nonexistent_path_123")

def test_project_manager_metadata(tmp_path):
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text("[project]\nname = 'test-bridge'\nversion = '1.0.0'")
    
    pm = ProjectManager(str(tmp_path))
    metadata = pm.get_metadata()
    assert metadata.get("name") == "test-bridge"
    assert metadata.get("version") == "1.0.0"

def test_project_manager_metadata_no_file(tmp_path):
    pm = ProjectManager(str(tmp_path))
    assert pm.get_metadata() == {}

def test_project_manager_list_resources(tmp_path):
    # Create some files
    (tmp_path / "main.py").write_text("print('hello')")
    
    # Create ignored directory and file inside it
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("core")
    
    # Create standard directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "utils.py").write_text("pass")
    
    pm = ProjectManager(str(tmp_path))
    resources = pm.list_resources()
    
    # Should contain main.py and src/utils.py
    assert "main.py" in resources
    assert "src/utils.py" in resources
    
    # Should NOT contain .git/config
    assert ".git/config" not in resources
