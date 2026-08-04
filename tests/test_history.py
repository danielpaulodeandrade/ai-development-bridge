import pytest
import os
import json
from datetime import datetime
from src.workspace_core.scanner import FileMeta
from src.workspace_core.size_controller import ContextChunk
from src.workspace_core.history import ContextHistory, ExportRecord

def test_context_history_log_export(tmp_path):
    history_file = tmp_path / ".bridge_history.json"
    history = ContextHistory(str(history_file))
    
    files = [
        FileMeta(path="src/main.py", size_bytes=100, extension=".py", last_modified=datetime.now()),
        FileMeta(path="README.md", size_bytes=200, extension=".md", last_modified=datetime.now())
    ]
    chunks = [
        ContextChunk(index=1, total_chunks=1, text_content="data chunk")
    ]
    
    record = history.log_export(files, chunks)
    
    assert record.total_chunks == 1
    assert "src/main.py" in record.files
    
    # Valida escrita no disco
    assert history_file.exists()
    
    # Valida leitura
    last = history.get_last_export()
    assert last is not None
    assert last.total_chunks == 1
    assert last.files == ["src/main.py", "README.md"]
    assert isinstance(last.timestamp, datetime)

def test_context_history_limit(tmp_path):
    history_file = tmp_path / ".bridge_history.json"
    history = ContextHistory(str(history_file))
    
    # Força logar 60 vezes
    for i in range(60):
        history.log_export([], [])
        
    # Verifica tamanho limite
    data = history._load_history()
    assert len(data["exports"]) == 50
