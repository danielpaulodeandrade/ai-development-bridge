import os
import pytest
from src.storage_layer.config import ConfigManager

def test_config_manager_load_empty(tmp_path):
    config_file = tmp_path / "empty_config.yaml"
    config_file.write_text("")
    
    manager = ConfigManager(str(config_file))
    assert manager.get("nonexistent") is None
    assert manager.get("nonexistent", "default") == "default"

def test_config_manager_load_missing(tmp_path):
    missing_file = tmp_path / "missing.yaml"
    manager = ConfigManager(str(missing_file))
    assert manager.get("key") is None

def test_config_manager_set_and_save(tmp_path):
    config_file = tmp_path / "config.yaml"
    manager = ConfigManager(str(config_file))
    
    manager.set("app_name", "AI Workspace Bridge")
    manager.set("version", 1)
    manager.save()
    
    assert config_file.exists()
    
    # Reload in a new manager to verify persistence
    manager2 = ConfigManager(str(config_file))
    assert manager2.get("app_name") == "AI Workspace Bridge"
    assert manager2.get("version") == 1

def test_config_manager_load_invalid_yaml(tmp_path):
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("invalid: [yaml: file: {")
    
    manager = ConfigManager(str(config_file))
    # Should fall back to empty config on parse error
    assert manager.get("invalid") is None
