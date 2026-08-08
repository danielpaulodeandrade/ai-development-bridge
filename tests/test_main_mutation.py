import pytest
from src.agent.parser import AACPParser
from src.agent.models import ActionType, FileAction, RunAction
from src.agent.file_executor import FileExecutor
from src.agent.shell_executor import ShellExecutor

def test_response_mutation_logic(monkeypatch):
    """Testa isoladamente a lógica de mutação presente no main.py"""
    
    # Mock dos executors para não rodarem de verdade
    monkeypatch.setattr(FileExecutor, "execute", lambda x: "✅ Diretório criado: test")
    
    original_response = (
        "Aqui está a pasta que você pediu:\n"
        "<<<MKDIR:test>>>\n"
        "Foi criada com sucesso!"
    )
    
    # Lógica idêntica ao main.py
    response_text = original_response
    actions = AACPParser.parse(response_text)
    
    for action in actions:
        result_msg = ""
        if isinstance(action, FileAction):
            result_msg = FileExecutor.execute(action)
        elif isinstance(action, RunAction):
            result_msg = ShellExecutor.execute(action)
            
        badge = f"\n> **Agent Execution:**\n> ```text\n> {result_msg}\n> ```\n"
        response_text = response_text.replace(action.original_match, badge)
        
    assert "✅ Diretório criado: test" in response_text
    assert "<<<MKDIR:test>>>" not in response_text
    assert "Aqui está a pasta que você pediu" in response_text
