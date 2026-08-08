import os
import pytest
from src.agent.models import FileAction, ActionType
from src.agent.file_executor import FileExecutor

@pytest.fixture
def workspace_mock(monkeypatch, tmp_path):
    """Mock do diretório de workspace para isolar os testes"""
    # Cria uma simulação da classe Settings
    class MockSettings:
        def get_workspace_dir(self):
            return str(tmp_path)
            
    monkeypatch.setattr("src.agent.file_executor.Settings", MockSettings)
    return tmp_path

def test_file_create(workspace_mock):
    action = FileAction(
        action_type=ActionType.FILE_CREATE,
        original_match="",
        path="new.txt",
        content="ola"
    )
    result = FileExecutor.execute(action)
    
    assert "✅" in result
    assert (workspace_mock / "new.txt").exists()
    assert (workspace_mock / "new.txt").read_text(encoding="utf-8") == "ola"

def test_file_replace_creates_backup(workspace_mock):
    # Cria o arquivo original
    target_file = workspace_mock / "target.txt"
    target_file.write_text("texto velho", encoding="utf-8")
    
    action = FileAction(
        action_type=ActionType.FILE_REPLACE,
        original_match="",
        path="target.txt",
        content="texto novo"
    )
    
    result = FileExecutor.execute(action)
    
    assert "backup salvo" in result
    assert target_file.read_text(encoding="utf-8") == "texto novo"
    assert (workspace_mock / "target.txt.bak").exists()
    assert (workspace_mock / "target.txt.bak").read_text(encoding="utf-8") == "texto velho"

def test_file_replace_resilience(workspace_mock):
    # O arquivo não existe, deve ser criado (resiliência)
    action = FileAction(
        action_type=ActionType.FILE_REPLACE,
        original_match="",
        path="inexistente.txt",
        content="texto novo"
    )
    
    result = FileExecutor.execute(action)
    assert "✅" in result
    assert (workspace_mock / "inexistente.txt").exists()
    assert (workspace_mock / "inexistente.txt").read_text(encoding="utf-8") == "texto novo"

def test_path_traversal_prevention(workspace_mock):
    # Tentativa maliciosa de escapar do diretório
    action = FileAction(
        action_type=ActionType.FILE_CREATE,
        original_match="",
        path="../../malicioso.txt",
        content="hack"
    )
    
    result = FileExecutor.execute(action)
    assert "❌ Erro" in result
    assert "Acesso negado" in result

def test_move_file(workspace_mock):
    src = workspace_mock / "src.txt"
    src.write_text("origem")
    
    action = FileAction(
        action_type=ActionType.MOVE_FILE,
        original_match="",
        path="src.txt",
        destination_path="dst.txt"
    )
    
    result = FileExecutor.execute(action)
    
    assert "✅" in result
    assert not src.exists()
    assert (workspace_mock / "dst.txt").exists()
    assert (workspace_mock / "dst.txt").read_text() == "origem"
