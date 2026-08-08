import pytest
from src.agent.parser import AACPParser
from src.agent.models import ActionType

def test_parse_file_create():
    text = """Aqui está o código:
<<<FILE_CREATE:test.txt>>>
hello world
<<<END_FILE>>>
Finalizado."""
    actions = AACPParser.parse(text)
    assert len(actions) == 1
    assert actions[0].action_type == ActionType.FILE_CREATE
    assert actions[0].path == "test.txt"
    assert actions[0].content == "hello world"

def test_parse_run():
    text = """Rodando o script:
<<<RUN>>>
python script.py
<<<END>>>"""
    actions = AACPParser.parse(text)
    assert len(actions) == 1
    assert actions[0].action_type == ActionType.RUN
    assert actions[0].command == "python script.py"

def test_parse_inline_commands():
    text = """
<<<DELETE_FILE:old.txt>>>
<<<MKDIR:new_folder>>>
<<<MOVE_FILE:old.txt|new.txt>>>
"""
    actions = AACPParser.parse(text)
    assert len(actions) == 3
    assert actions[0].action_type == ActionType.DELETE_FILE
    assert actions[0].path == "old.txt"
    
    assert actions[1].action_type == ActionType.MKDIR
    assert actions[1].path == "new_folder"
    
    assert actions[2].action_type == ActionType.MOVE_FILE
    assert actions[2].path == "old.txt"
    assert actions[2].destination_path == "new.txt"

def test_ignore_malformed_blocks():
    # Faltou <<<END_FILE>>>
    text = """<<<FILE_CREATE:fail.txt>>>
conteúdo incompleto
"""
    actions = AACPParser.parse(text)
    assert len(actions) == 0

def test_multiple_commands():
    text = """
<<<FILE_CREATE:1.txt>>>
um
<<<END_FILE>>>
Texto intermediário.
<<<RUN>>>
ls
<<<END>>>
"""
    actions = AACPParser.parse(text)
    assert len(actions) == 2
    assert actions[0].action_type == ActionType.FILE_CREATE
    assert actions[1].action_type == ActionType.RUN
