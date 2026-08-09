import pytest
from src.agent.models import RunAction, ActionType
from src.agent.shell_executor import ShellExecutor

def test_shell_execute_authorized(monkeypatch):
    # Simula o usuário digitando 'y'
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    
    action = RunAction(
        action_type=ActionType.RUN,
        original_match="",
        command="python -c \"print('Hello World')\""
    )
    
    result = ShellExecutor.execute(action)
    assert "Exit Code: 0" in result
    assert "Hello World" in result

def test_shell_execute_rejected(monkeypatch):
    # Simula o usuário digitando 'n'
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    
    action = RunAction(
        action_type=ActionType.RUN,
        original_match="",
        command="rm -rf /"
    )
    
    result = ShellExecutor.execute(action)
    assert result == "Comando rejeitado pelo usuário por razões de segurança. Não tente novamente."
    assert "Exit Code" not in result

def test_shell_execute_timeout_loop(monkeypatch, capsys):
    # Testa se o loop do timeout continua rodando sem quebrar o processo
    # (Não podemos rodar por 60s reais no teste unitário, então vamos mockar communicate)
    
    # Simula o usuário autorizando
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    
    import subprocess
    
    class MockPopen:
        def __init__(self, *args, **kwargs):
            self.returncode = 0
            self.call_count = 0
            
        def communicate(self, timeout=None):
            self.call_count += 1
            if self.call_count == 1:
                # Na primeira vez lança timeout
                raise subprocess.TimeoutExpired(cmd="fake", timeout=60)
            else:
                # Na segunda vez retorna sucesso
                return ("Concluído", "")
                
    monkeypatch.setattr(subprocess, 'Popen', MockPopen)
    
    action = RunAction(action_type=ActionType.RUN, original_match="", command="sleep 120")
    result = ShellExecutor.execute(action)
    
    # Verifica se a saída capturada é o retorno da segunda tentativa
    assert "STDOUT:\nConcluído" in result
    
    # Verifica se o print de aviso ocorreu
    captured = capsys.readouterr()
    assert "ainda está rodando (passaram-se 60s)" in captured.out
